import os
import re
from imap_tools import MailBox, AND
from dotenv import load_dotenv
from PyQt6.QtCore import QSettings

class MailConnector:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv("EMAIL_COMPTE")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = 'imap.gmail.com'
        
        # On lit les paramètres globaux
        self.settings = QSettings("MonEntreprise", "SuiviRapports")

    def check_new_reports(self):
        if not self.email or not self.password:
            print("Erreur : Identifiants introuvables dans le fichier .env")
            return []

        # On récupère le modèle utilisateur (ex: rapport_expertise_psychologique-X- X)
        template = self.settings.value("subject_template", "rapport_expertise_psychologique-X- X", type=str)
        
        # On protège le texte classique, puis on remplace le "X" par un groupe de capture Regex (.*?)
        # La regex finale ressemblera à : rapport\_expertise\_psychologique\-(.*?)\-\ (.*?)
        regex_pattern = re.escape(template).replace('X', '(.*?)')

        print("Connexion à Gmail en cours pour vérification...")
        nouveaux_rapports = []
        
        try:
            with MailBox(self.imap_server).login(self.email, self.password) as mailbox:
                
                # On lit tous les mails non lus
                for msg in mailbox.fetch(AND(seen=False)):
                    sujet = msg.subject
                    
                    # On compare le sujet avec la Regex générée dynamiquement
                    match = re.search(regex_pattern, sujet)
                    
                    if match:
                        # Le premier "X" capturé (group 1) est toujours le nom du client dans notre logique
                        nom_complet = match.group(1).strip()
                        
                        parts = nom_complet.split(' ')
                        if len(parts) > 1:
                            prenom = parts[-1].capitalize()
                            nom = " ".join(parts[:-1]).upper()
                        else:
                            nom = nom_complet.upper()
                            prenom = ""
                            
                        nouveaux_rapports.append((nom, prenom))
                        print(f"Nouveau rapport détecté pour : {nom} {prenom}")
                        
        except Exception as e:
            print(f"Erreur lors de la connexion IMAP : {e}")
            
        return nouveaux_rapports