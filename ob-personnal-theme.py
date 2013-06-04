#!/usr/bin/env python
# -*-coding:utf-8-*


import pygtk
pygtk.require("2.0")
import gtk 
import os
from os import chdir
import shutil, tarfile, threading, time, subprocess, gobject
from xml.etree import ElementTree as  ET

gobject.threads_init()
BASE = os.path.expanduser('/')
HOME_FOLDER = os.path.expanduser('~')
NOM = os.environ['USER']
EMPLACEMENT = os.path.join(HOME_FOLDER, ".obpersonnal-theme/")
THEME_PATHS = ['.config/tint2/tint2rc', '.config/nitrogen/bg-saved.cfg', '.conkyrc',
				'.gtkrc-2.0', '.config/openbox/rc.xml', '.config/compton.conf'] 				
CONFIG_PATHS = ['.config/openbox/autostart', '.config/openbox/menu.xml']
				
chdir(HOME_FOLDER)

if os.path.isdir(".obpersonnal-theme") != True: #si le dossier n'est pas présent
	os.mkdir(".obpersonnal-theme") #on créer le dossier
		
chdir(EMPLACEMENT)


class ObPersonalTheme :
	
	def Quitter(self, widget):
		gtk.main_quit()
		
	def sauvegarde(self, widget):
		ChoixNomTheme(self, "sauvegarde")
		self.boutonSauvegarde.set_label("Sauvegarde Réussie")

	def exportation_theme(self, widget):
		ChoixNomTheme(self, "exportation")
		
	def importation_theme(self, widget):
		SelecteurFichier(self)
		
	def listeTheme(self, listeDeroulante):
		themes_dispo= [nom for nom  in os.listdir(EMPLACEMENT) if os.path.isdir(nom) == True]
		for e in themes_dispo:
			listeDeroulante.append_text(e)
						
	def theme_choix(self, listeDeroulante): #########################################################
		choix = listeDeroulante.get_active_text()
		if (choix == "Thémes Disponible"):
			pass 
		else:
			chdir('{0}'.format(choix))
			if os.path.isfile("autostart") == True:
				listConky = fonctions.analyse_import_conky(choix)
				if len(listConky) != 0 :
					fonctions.importation_conky(choix, listConky)
			fonctions.restauration_theme()
			chdir(EMPLACEMENT)
				
	def saveConfig(self, widget):
		fonctions.creation_dossier("Ma_Config")
		chdir("Ma_Config")
		fonctions.sauvegarde_conky("Ma_Config")
		fonctions.sauvegarde_config()
		fonctions.sauvegarde_theme()
		self.boutonSaveConfig.set_label("Sauvegarde Réussie")
		chdir(EMPLACEMENT)
		
	def restaurationConfig(self, widget):
		try:
			chdir("Ma_Config")
		except OSError:
			self.boutonRestaurationConfig.set_label("Pas de sauvegarde")
		fonctions.restauration_config()
		fonctions.restauration_theme()
		chdir(EMPLACEMENT)
		
	def saveConfTargz(self, widget):
		fonctions.creation_dossier("Ma_Config")
		nom_theme = "Ma_Config" 
		self.savetargz = Exportation_thread(self, nom_theme)
		self.savetargz.start()
								
	def __init__(self):
		
		maFenetre = gtk.Window()
		maFenetre.set_title("Ob_Personal_Thèmes")
		maFenetre.connect("destroy", self.Quitter)
		maFenetre.set_default_size(300, 300)
		
		separateur = gtk.HSeparator()
		separateur.set_size_request(150, 4)
		
		cadre1 = gtk.Frame("Sauvegarde")
		cadre1.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		
		tableau1 = gtk.Table(2, 2)
		cadre1.add(tableau1)
		
		self.boutonSauvegarde = gtk.ToggleButton(label = "Sauvegarder le thème actuel")
		self.boutonSauvegarde.connect("clicked" ,self.sauvegarde)
		tableau1.attach(self.boutonSauvegarde, 0, 1, 0, 1)
		
		self.boutonExportation = gtk.ToggleButton(label = "Exporter le thème actuel")
		self.boutonExportation.connect("clicked" ,self.exportation_theme)
		tableau1.attach(self.boutonExportation,  0, 1, 1, 2)
		
		cadre2 = gtk.Frame("Importation")
		cadre2.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		tableau2 = gtk.Table(2, 2)
		cadre2.add(tableau2)
		
		self.boutonImportation = gtk.ToggleButton(label = "Importer un thème")
		self.boutonImportation.connect("clicked" ,self.importation_theme)
		tableau2.attach(self.boutonImportation, 0, 1, 0, 1)
		
		listeDeroulante = gtk.combo_box_new_text()
		listeDeroulante.append_text('Thémes Disponible')
		listeDeroulante.set_wrap_width(2)
		self.listeTheme(listeDeroulante)
		listeDeroulante.connect('changed', self.theme_choix)
		listeDeroulante.set_active(0)
		tableau2.attach(listeDeroulante, 0, 1, 1, 2)
	
		cadre3 = gtk.Frame("Administration")
		cadre3.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		tableau3 = gtk.Table(3, 2)
		cadre3.add(tableau3)
		
		self.boutonSaveConfig = gtk.ToggleButton(label = "Sauvegarder Configuration")
		self.boutonSaveConfig.connect("clicked", self.saveConfig)
		tableau3.attach(self.boutonSaveConfig, 0, 1, 0, 1)
		
		self.boutonRestaurationConfig = gtk.ToggleButton(label = "Restaurer Configuration")
		self.boutonRestaurationConfig.connect("clicked", self.restaurationConfig)
		tableau3.attach(self.boutonRestaurationConfig, 0, 1, 1, 2)
		
		self.boutonSaveTarGz = gtk.ToggleButton(label = "Sauvegarder en Tar.gz")
		self.boutonSaveTarGz.connect("clicked", self.saveConfTargz)
		tableau3.attach(self.boutonSaveTarGz, 0, 1, 2, 3) 
		
		separateur2 = gtk.HSeparator()
		separateur2.set_size_request(150, 4)
		separateur3 = gtk.HSeparator()
		separateur3.set_size_request(150, 4)
		separateur4 = gtk.HSeparator()
		separateur4.set_size_request(150, 4)
		
		boutonQuitter = gtk.Button("Quitter", stock = gtk.STOCK_QUIT)
		boutonQuitter.connect("clicked", self.Quitter)
		
		vBox = gtk.VBox()
		vBox.pack_start(separateur, False, True, 2)
		vBox.pack_start(cadre1, False, False, 4)
		vBox.pack_start(separateur2, False, True, 2)
		vBox.pack_start(cadre2, False, False, 4)
		vBox.pack_start(separateur3, False, True, 2)
		vBox.pack_start(cadre3, False, False, 4)
		vBox.pack_start(separateur4, False, True, 2)
		vBox.pack_end(boutonQuitter, False, False, 2)
		maFenetre.add(vBox)
		maFenetre.show_all()
		

class Fonctions:
	
	def copie_fichiers(self, fichierSource, fichierCopie):
		self.source, self.copie = fichierSource, fichierCopie
		try:
			shutil.copyfile(self.source, self.copie)
		except (IOError, shutil.Error):
			pass
	
	def creation_dossier(self, nomDossier):
		self.nom = nomDossier
		try:
			os.mkdir(self.nom)
		except OSError:
			pass 
			
	def copie_dossier(self, dossierSource, dossierCopie):
		self.source, self.copie = dossierSource, dossierCopie
		try:
			shutil.copytree(self.source, self.copie)
		except OSError:
			pass
					
	def sauvegarde_theme(self):
		for fichierSource in [os.path.join(HOME_FOLDER, fichier) for fichier in THEME_PATHS]:
			fichierCopie = os.path.basename(fichierSource)
			self.copie_fichiers(fichierSource, fichierCopie) #Copie fichier
			
	def restauration_theme(self):
		for fichierCopie in [os.path.join(HOME_FOLDER, fichier) for fichier in THEME_PATHS]:
			fichierSource = os.path.basename(fichierCopie)
			self.copie_fichiers(fichierSource, fichierCopie) #Copie fichier
		self.tint2 = Tint2Thread(self)	
		self.tint2.start()
		subprocess.call("openbox --reconfigure && nitrogen --restore ", shell=True)
		os.system("conky -q &")
				
	def sauvegarde_config(self):
		self.sauvegarde_theme()
		for fichierSource in [os.path.join(HOME_FOLDER, fichier) for fichier in CONFIG_PATHS]:
			fichierCopie = os.path.basename(fichierSource)
			self.copie_fichiers(fichierSource, fichierCopie)
				
	def restauration_config(self):
		for fichierCopie in [os.path.join(HOME_FOLDER, fichier) for fichier in THEME_PATHS]:
			fichierSource = os.path.basename(fichierCopie)
			self.copie_fichiers(fichierSource, fichierCopie)
		self.restauration_theme()
		
	def sauvegarde_conky(self, nom_theme):
		self.nomConky = nom_theme
		i = 0
		autostart = open(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), 'r')
		for ligne in autostart:	
			if ("conky -c" in ligne) and (ligne[0] != '#'):
				i += 1
				parseLigne = ligne.split('conky -c ')[1]
				cheminConky = parseLigne.replace(' ', '').rstrip('\)&\n')
				if cheminConky[0] == '~':
					self.copie_fichiers(HOME_FOLDER+"/"+cheminConky[1:], EMPLACEMENT+self.nomConky) 	
				self.copie_fichiers(cheminConky, EMPLACEMENT+self.nomConky) 
				self.copie_fichiers(HOME_FOLDER+"/"+CONFIG_PATHS[0], "autostart")
		del i
		autostart.close()
		
	def analyse_import_conky(self, nom_theme):####################################################
		autostart = open("autostart",  'r')
		self.nomConky = nom_theme
		os.system("killall conky")
		conky = []
		i = 0
		for ligne in autostart:	
			if ("conky -c" in ligne) and (ligne[0] != '#'):
				i += 1
				parseLigne = ligne.split('conky -c ')[1]
				cheminConky = parseLigne.replace(' ', '')
				os.system("conky -c "+EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc &")
				conky.append(EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc")
		autostart.close()
		del i
		return conky
		
	def importation_conky(self, nom_theme, listConky):
		self.nom_theme, self.newConky = nom_theme, listConky
		autostart = open(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), 'r')
		newautostart = open("autostart", 'w')
		i = 0
		for ligne in autostart:	
			if ("conky -c" in ligne) and (ligne[0] != '#'):
				i += 1
				if (len(self.newConky) != 0):
					for nom in self.newConky:
						print >> newautostart, "(sleep 3s && conky -c "+str(nom)+") &"
			else:
				print >> newautostart, str(ligne).rstrip('\n')
		autostart.close()
		newautostart.close()
		self.copie_fichiers("autostart", HOME_FOLDER+"/"+CONFIG_PATHS[0])
		if (i == 0):
			self.ajout_autostart(self, self.newConky)
		del i
				
	def ajout_autostart(self, newConky):
		self.conkySup = newConky 
		autostart = open(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), 'a')
		for nom in self.conkySup:
			print >> autostart, "(sleep 3s && conky -q ) &"
		self.copie_fichiers(HOME_FOLDER+"/"+CONFIG_PATHS[0], "autostart")
		del self.conkySup
		
class ChoixNomTheme:
	
	def __init__(self, widget, choix):
		self.fenetre = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.fenetre.set_size_request(200, 100)
		self.fenetre.set_title("Nom du theme")
		self.fenetre.connect("delete_event", gtk.main_quit)
		self.choix = choix
		etiquette = gtk.Label()
		etiquette.set_text("Nom de votre thème :")
		nom_theme_export = gtk.Entry()
		nom_theme_export.set_text("votre theme")
		nom_theme_export.connect("activate", self.validation, nom_theme_export)
		
		bouton_valider = gtk.Button("Valider")
		bouton_valider.connect("clicked", self.validation, nom_theme_export)
		
		vBox = gtk.VBox()
		vBox.pack_start(etiquette)
		vBox.pack_start(nom_theme_export)
		vBox.pack_start(bouton_valider,  False, False, 2)
		
		self.fenetre.add(vBox)
		self.fenetre.show_all()
		
	def validation(self,fenetre,  nom_theme_export):
		nom_theme = nom_theme_export.get_text()
		emplacement_theme = os.path.join(EMPLACEMENT, '{0}'.format(nom_theme))
		fonctions.creation_dossier('{0}'.format(nom_theme))
		chdir(nom_theme)
		self.quitter(fenetre, nom_theme_export)
		if (self.choix == "exportation"):
			self.exportation = Exportation_thread(self, nom_theme)
			self.exportation.start()
		if (self.choix == "sauvegarde"):
			fonctions.sauvegarde_conky(nom_theme)
			fonctions.sauvegarde_theme()
			chdir(EMPLACEMENT)
			
	def quitter(self, widget, nom_theme_export):
		self.fenetre.destroy()
		
			
class Exportation_thread(threading.Thread):
	 
	def __init__ (self, fenetre, nom_theme):
		threading.Thread.__init__ (self, target=self)
		self.nom_theme = nom_theme
		
	def run(self):
		emplacement_theme = os.path.join(EMPLACEMENT, '{0}'.format(self.nom_theme))
		
		fenetre2 = gtk.Window()
		fenetre2.set_default_size(240, 140)
		
		etiquette = gtk.Label()
		etiquette.set_justify(gtk.JUSTIFY_CENTER)
		fenetre2.add(etiquette)
		fenetre2.show_all()
		
		etiquette.set_text("\nCopie des fichiers\nde configuration\n")
		
		if (self.nom_theme == "Ma_Config"):
			
			fonctions.sauvegarde_config()
			
		fonctions.sauvegarde_conky(self.nom_theme)
		fonctions.sauvegarde_theme()
		
		f_config_wall = open('{0}/{1}'.format(HOME_FOLDER,THEME_PATHS[1]), 'r')
		for ligne in f_config_wall:
			if "file=" in ligne:
				place_wall = ligne.rstrip('\n\r').lstrip('file=')
				wall_nom = os.path.basename(place_wall)
		shutil.copyfile(place_wall, wall_nom)
		
		f_gtkrc = open('{0}/{1}'.format(HOME_FOLDER,THEME_PATHS[3]), 'r')
		for ligne in f_gtkrc:
			if "gtk-theme-name=" in ligne:
				nom_theme = ligne.rstrip('\n\r').split("\"")[1]
				themeSource = os.path.join(HOME_FOLDER, ".themes/{0}".format(nom_theme))
				themeSource_2 = os.path.join(BASE, "usr/share/themes/{0}".format(nom_theme))
				if os.path.isdir(themeSource) == True : 
					fonctions.copie_dossier(themeSource, nom_theme)
				else :
					fonctions.copie_dossier(themeSource_2, nom_theme)
 
			if "gtk-icon-theme-name=" in ligne:	
				nom_icons = ligne.rstrip('\n\r').split("\"")[1]
				icons_source = os.path.join(HOME_FOLDER, ".icons/{0}".format(nom_icons))
				icons_source_2 = os.path.join(BASE, "usr/share/icons/{0}".format(nom_icons))
				if os.path.isdir(icons_source) == True :
					fonctions.copie_dossier(icons_source, nom_icons)
				else :
					fonctions.copie_dossier(icons_source_2, nom_icons) 
						
		time.sleep(2)
		
		chdir(HOME_FOLDER)
		
		etiquette.set_text("\nRecherche et copie du theme openbox \n ")
		tree = ET.parse('.config/openbox/rc.xml')
		root = tree.getroot()
		theme_open_box = root.find('{http://openbox.org/3.4/rc}theme/{http://openbox.org/3.4/rc}name').text
		theme_box = os.path.join(BASE, "usr/share/themes/{0}".format(theme_open_box))
		
		chdir(emplacement_theme)
		fonctions.copie_dossier(icons_source, nom_icons)
			
		f_nom_theme= open("exportImport.txt", 'w')
		print >> f_nom_theme, "{0}".format(theme_open_box)
		f_nom_theme.close()
		time.sleep(2)
		
		etiquette.set_text("\nCréation de l'archive\nle plus long...\n")
			
		chdir(EMPLACEMENT)
		tz = tarfile.open('{0}.tar.gz'.format(self.nom_theme), 'w:gz')
		tz.add(self.nom_theme)
		tz.close()
		
		chdir(HOME_FOLDER)
		shutil.move('{0}.tar.gz'.format(emplacement_theme), "{0}.tar.gz".format(self.nom_theme))
		chdir(EMPLACEMENT)
		etiquette.set_text("Exportation Terminée\nVotre theme se trouve \ndans votre dossier personnel")
		time.sleep(4)
		
		fenetre2.destroy()
		
			
class SelecteurFichier:
	
	def destroy(self, widget):
		self.selectfichier.destroy()
	def choix_fichier(self, w):
		chdir(EMPLACEMENT)
		nomThemeImport = self.selectfichier.get_filename()
		self.selectfichier.destroy()
		
		self.importation = ImportationThread(self, nomThemeImport)
		self.importation.start()
		
	def __init__(self, widget): 
		chdir(HOME_FOLDER)
		self.selectfichier = gtk.FileSelection("Selection de fichier")
		self.selectfichier.connect("destroy", self.destroy)
		self.selectfichier.ok_button.connect("clicked", self.choix_fichier)
		self.selectfichier.cancel_button.connect("clicked", lambda w: self.selectfichier.destroy())
		self.selectfichier.set_filename("manon")
		self.selectfichier.show()
		
				 
class ImportationThread(threading.Thread):
	def __init__ (self, widget,  nomThemeImport):
		threading.Thread.__init__ (self, target=self)
		self.nom_theme = nomThemeImport
		listConky = []
	def run(self):
		fenetre2 = gtk.Window()
		fenetre2.set_default_size(240, 140)
		etiquette = gtk.Label()
		etiquette.set_justify(gtk.JUSTIFY_CENTER)
		fenetre2.add(etiquette)
		fenetre2.show_all()
		
		nom_tar_gz =  self.nom_theme.split('.tar.gz')[0]
		nom_dossier = os.path.basename(nom_tar_gz)
		etiquette.set_text("décompression de l'archive\n le plus long")
		time.sleep(2)
		tz = tarfile.open('{0}.tar.gz'.format(nom_tar_gz), 'r')
		tz.extractall()
		tz.close()
		
		chdir("{0}{1}/".format(EMPLACEMENT, nom_dossier))
		if os.path.isfile("autostart") == True: 
			etiquette.set_text("recherche et copie\n fichier conky\n")
			time.sleep(2)
			listConky = fonctions.analyse_import_conky(nom_dossier)#Recherche des conky
			if len(listConky) != 0 :
				fonctions.importation_conky(nom_dossier, listConky)#copie des conky
		
		etiquette.set_text("recherche emplacement wallpaper\npuis sauvegarde")
		
		themeBgsavedCfg = open("bg-saved.cfg", 'r')
		baseBgsavedCfg = open('{0}/{1}'.format(HOME_FOLDER,THEME_PATHS[1]), 'r')
		copieBgsavedCfg = open("copie.cfg", 'w')
		for ligne in themeBgsavedCfg:
			if "file=" in ligne:
				wallNom = os.path.basename(ligne.rstrip('\n\r'))
				for ligne in baseBgsavedCfg:
					if "file=" in ligne:
						ancienWall = os.path.basename(ligne.rstrip('\n\r'))
						wallp= ligne.rstrip('\n\r').lstrip('file=')
						wallPosition = wallp.strip(ancienWall)
						
				print >> copieBgsavedCfg, "file={0}{1}".format(wallPosition, wallNom)
			else:
				print >> copieBgsavedCfg, "{0}".format(ligne)
		themeBgsavedCfg.close()
		baseBgsavedCfg.close()
		copieBgsavedCfg.close()
		os.remove("bg-saved.cfg")
		os.rename("copie.cfg", "bg-saved.cfg")
		shutil.copyfile(wallNom, "{0}{1}".format(wallPosition, wallNom))
		time.sleep(2)
		
		etiquette.set_text("recherche et copie du theme et des icônes")
		
		fgtkrc = open(".gtkrc-2.0", 'r')
		for ligne in fgtkrc:
			if "gtk-theme-name=" in ligne:
				nomTheme = ligne.rstrip('\n\r').split("\"")[1]
				themeCopie  = os.path.join(HOME_FOLDER, ".themes/{0}".format(nomTheme))
				fonctions.copie_dossier(nomTheme,themeCopie)
				del nomTheme, themeCopie
			if "gtk-icon-theme-name=" in ligne:
				nomIcons = ligne.rstrip('\n\r').split("\"")[1]
				iconsCopier = os.path.join(HOME_FOLDER, ".icons/{0}".format(nomIcons))
				fonctions.copie_dossier(nomIcons, iconsCopier)
				del nomIcons, iconsCopier
		time.sleep(2)
		
		exportImport = open("exportImport.txt", 'r')
		txt = exportImport.read()
		nomBox = txt.rstrip('\n\r')
		themeBox = os.path.join(HOME_FOLDER, ".themes/{0}".format(nomBox))
		themeBase = os.path.join(BASE, "usr/share/themes/{0}".format(nomBox))
		os.remove("exportImport.txt")
		if os.path.isdir(themeBase) == True :#si le theme est deja présent on pass
			pass
		else:
			fonctions.copie_dossier(nomBox, themeBox)
			
		fonctions.restauration_theme()
		
		chdir(HOME_FOLDER)
	
		if ET.VERSION[0:3] == '1.2':
			def fixtag(tag, namespaces):
				import string
				if isinstance(tag, ET.QName):
					tag = tag.text
				namespace_uri, tag = string.split(tag[1:], "}", 1)
				prefix = namespaces.get(namespace_uri)
				if namespace_uri not in namespaces:
					prefix = ET._namespace_map.get(namespace_uri)
					if namespace_uri not in ET._namespace_map:
						prefix = "ns%d" % len(namespaces)
					namespaces[namespace_uri] = prefix
					if prefix == "xml":
						xmlns = None
					else:
						if prefix is not None:
							nsprefix = ':' + prefix
						else:
							nsprefix = ''
						xmlns = ("xmlns%s" % nsprefix, namespace_uri)
				else:
					xmlns = None
				if prefix is not None:
					prefix += ":"
				else:
					prefix = ''

				return "%s%s" % (prefix, tag), xmlns
			ET.fixtag = fixtag
			ET._namespace_map['http://openbox.org/3.4/rc'] = None
		else:
			ET.register_namespace('', 'http://openbox.org/3.4/rc')
		
		tree = ET.parse(".config/openbox/rc.xml")
		root = tree.getroot()
		root.find('{http://openbox.org/3.4/rc}theme/{http://openbox.org/3.4/rc}name').text = nomBox
		tree.write('.config/openbox/rc.xml')
		
		etiquette.set_text("Mise en place du theme")
		subprocess.call("openbox --reconfigure && nitrogen --restore ", shell=True)
		time.sleep(2)
		
		etiquette.set_text("Importation Terminée")
		time.sleep(2)
		
		chdir(EMPLACEMENT)
		fenetre2.destroy()
		
				
class Tint2Thread(threading.Thread):
	
	def __init__ (self, tint2):
		threading.Thread.__init__ (self, target=self)
	def run(self):
		os.system("pkill tint2 && tint2 &")	
		
		
if __name__ == "__main__":
	
	fonctions = Fonctions()
	ObPersonalTheme()
	gtk.main()
