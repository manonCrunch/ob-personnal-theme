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
		themes_dispo = os.listdir(EMPLACEMENT)
		for e in themes_dispo:
			if (os.path.isdir(e) == True):
				listeDeroulante.append_text(e)
				
	def theme_choix(self, listeDeroulante):
		choix = listeDeroulante.get_active_text()
		if (choix == "Thémes Disponible"):
			pass 
		else:
			chdir('{0}'.format(choix))
			fonctions.recherche_copie_conky(choix, "restauration")
			fonctions.restauration_theme()
			chdir(EMPLACEMENT)
				
	def saveConfig(self, widget):
		fonctions.creation_dossier("Ma_Config")
		chdir("Ma_Config")
		fonctions.recherche_copie_conky("Ma_Config", "sauvegarde")
		fonctions.sauvegarde_config()
		fonctions.sauvegarde_theme()
		self.boutonSaveConfig.set_label("Sauvegarde Réussie")
		chdir(EMPLACEMENT)
		
	def restaurationConfig(self, widget):
		try:
			chdir("Ma_Config")
		except OSError:
			self.boutonRestaurationConfig.set_label("Pas de sauvegarde")
		fonctions.recherche_copie_conky("Ma_Config", "restauration")
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
	
	def sauvegarde_theme(self):
		for fichierSource in [os.path.join(HOME_FOLDER, fichier) for fichier in THEME_PATHS]:
			fichierCopie = os.path.basename(fichierSource)
			self.copie_fichiers(fichierSource, fichierCopie) #Copie fichier
			
	def restauration_theme(self):
		for fichierCopie in [os.path.join(HOME_FOLDER, fichier) for fichier in THEME_PATHS]:
			fichierSource = os.path.basename(fichierCopie)
			self.copie_fichiers(fichierSource, fichierCopie) #Copie fichier
		if os.path.isfile("autostart") == True:
			shutil.copyfile("autostart", CONFIG_PATHS[0])
		self.tint2 = Tint2Thread(self)	
		self.tint2.start()
		subprocess.call("openbox --reconfigure && nitrogen --restore ", shell=True)
				
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
		
	def recherche_copie_conky(self, nom_theme, option):
		self.nomConky, self.condition = nom_theme, option
		conky = []
		i = 0
		#os.system("killall conky")
		autostart = open(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), 'r')
		try:
			modifAutostart = open("autostart", 'r')
		except IOError:
			pass
		newAutostart = open("newAutostart", 'w')

		if (self.condition == "sauvegarde"):
			autostart = open(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), 'r')
		elif (self.condition == "restauration") and os.path.isfile("autostart") == True:
			autostart = open("autostart", 'r')	
		elif(self.condition == "importation") and os.path.isfile("autostart") == True:
			autostart = open("autostart", 'r')
		
		for ligne in autostart:	
			if "conky -c" in ligne and ligne[-2] == '&':
				if ligne[0] == '#' or not '/' in ligne:
					pass
				i += 1
				parseLigne = ligne.split('/')
				cheminConky = ligne.split(' ')[-2]
				if (self.condition == "sauvegarde"):
					self.copie_fichiers(cheminConky.rstrip('\)'), self.nomConky+str(i)+"conkyrc") #Copie conky
					self.copie_fichiers(os.path.join(HOME_FOLDER, CONFIG_PATHS[0]), "autostart") #copie autostart
				elif(self.condition == "restauration"):
					
					os.system("conky -c "+EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc &")
				elif(action == "importation") and os.path.isfile(EMPLACEMENT+self.nomConky+"/"+str(i)+"conkyrc") == True :												   
					self.copie_fichiers("autostart", os.path.join(HOME_FOLDER, CONFIG_PATHS[0]))
					#os.system("conky -c "+EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc &")
					conky.append(str(parseLigne[0])+EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc")
		autostart.close()
					
		if (len(conky) != 0) and os.path.isfile(EMPLACEMENT+self.nomConky+"/autostart") == True:
			os.system("killall conky")
			for ligne in modifAutostart:
				if "conky -c" in ligne and ligne[-2] == '&':
					if ligne[0] == '#' or not '/' in ligne:
						pass
					else:
						for nomConky in conky:
							print >> newAutostart, "\(sleep 3s && "+str(nomConky)+"\) &"
							os.system("\(sleep 3s && conky -c "+EMPLACEMENT+self.nomConky+"/"+self.nomConky+str(i)+"conkyrc &")
							time.sleep(3)
				else:
					print >> newAutostart, str(ligne).rstrip('\n')
			modifAutostart.close()
			newAutostart.close()
			os.remove(HOME_FOLDER+CONFIG_PATHS[0])
			self.copie_fichiers("newAutostart", HOME_FOLDER+CONFIG_PATHS[0])
		os.remove("newAutostart")	
			
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
			fonctions.recherche_copie_conky(nom_theme, "sauvegarde")
			self.exportation = Exportation_thread(self, nom_theme)
			self.exportation.start()
		if (self.choix == "sauvegarde"):
			fonctions.recherche_copie_conky(nom_theme, "sauvegarde")
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
		fonctions.sauvegarde_theme()
		
		f_config_wall = open('{0}/{1}'.format(HOME_FOLDER,THEME_PATHS[1]), 'r')
		for ligne in f_config_wall:
			txt = ligne
			if "file=" in txt:
				place_wall = ligne.rstrip('\n\r').lstrip('file=')
				wall_nom = os.path.basename(place_wall)
		shutil.copyfile(place_wall, wall_nom)
		
		f_gtkrc = open('{0}/{1}'.format(HOME_FOLDER,THEME_PATHS[3]), 'r')
		for ligne in f_gtkrc:
			txt = ligne
			if "gtk-theme-name=" in txt:
				nom_theme = ligne.rstrip('\n\r').split("\"")
				theme_source = os.path.join(HOME_FOLDER, ".themes/{0}".format(nom_theme[1]))
				theme_source_2 = os.path.join(BASE, "usr/share/themes/{0}".format(nom_theme[1]))
				if os.path.isdir(theme_source) == True :
					try:
						shutil.copytree(theme_source, nom_theme[1])
					except OSError:
						pass
				else :
					try:
						shutil.copytree(theme_source_2, nom_theme[1])
					except OSError:
						pass	
						
			if "gtk-icon-theme-name=" in txt:	
				nom_icons = ligne.rstrip('\n\r').split("\"")
				icons_source = os.path.join(HOME_FOLDER, ".icons/{0}".format(nom_icons[1]))
				icons_source_2 = os.path.join(BASE, "usr/share/icons/{0}".format(nom_icons[1]))
				if os.path.isdir(icons_source) == True :
					try:
						shutil.copytree(icons_source, nom_icons[1])
					except OSError:
						pass
				else : 
					try:
						shutil.copytree(icons_source_2, nom_icons[1])
					except IOError:
						pass				
		time.sleep(2)
		
		chdir(HOME_FOLDER)
		
		etiquette.set_text("\nRecherche et copie du theme openbox \n ")
		tree = ET.parse('.config/openbox/rc.xml')
		root = tree.getroot()
		theme_open_box = root.find('{http://openbox.org/3.4/rc}theme/{http://openbox.org/3.4/rc}name').text
		theme_box = os.path.join(BASE, "usr/share/themes/{0}".format(theme_open_box))
		
		chdir(emplacement_theme)
		try:
			shutil.copytree(theme_box, theme_open_box)
		except OSError:
			pass
			
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
		
	def run(self):
		fenetre2 = gtk.Window()
		fenetre2.set_default_size(240, 140)
		etiquette = gtk.Label()
		etiquette.set_justify(gtk.JUSTIFY_CENTER)
		fenetre2.add(etiquette)
		fenetre2.show_all()
		
		nom_tar_gz =  self.nom_theme.split('.tar.gz')
		nom_dossier = os.path.basename(nom_tar_gz[0])
		etiquette.set_text("décompression de l'archive\n le plus long")
		tz = tarfile.open('{0}.tar.gz'.format(nom_tar_gz[0]), 'r')
		tz.extractall()
		tz.close()
		
		chdir("{0}{1}/".format(EMPLACEMENT, nom_dossier))
		
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
				nomTheme = ligne.rstrip('\n\r').split("\"")
				themeCopie  = os.path.join(HOME_FOLDER, ".themes/{0}".format(nomTheme[1]))
				try:
					shutil.copytree(nomTheme[1], themeCopie)
				except OSError:
					pass
			if "gtk-icon-theme-name=" in ligne:
				nomIcons = ligne.rstrip('\n\r').split("\"")
				iconsCopier = os.path.join(HOME_FOLDER, ".icons/{0}".format(nomIcons[1]))
				try:
					shutil.copytree(nomIcons[1], iconsCopier)
				except OSError:
					pass
		time.sleep(2)
		
		exportImport = open("exportImport.txt", 'r')
		txt = exportImport.read()
		nomBox = txt.rstrip('\n\r')
		themeBox = os.path.join(HOME_FOLDER, ".themes/{0}".format(nomBox))
		themeBase = os.path.join(BASE, "usr/share/themes/{0}".format(nomBox))
		os.remove("exportImport.txt")
		if os.path.isdir(themeBase) == True :
			pass
		else:
			try:
				shutil.copytree(nomBox, themeBox)
			except OSError:
				pass
				
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
