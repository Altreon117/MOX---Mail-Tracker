import os
import re
from imap_tools import MailBox, AND
from dotenv import load_dotenv

class MailConnector:
    def __init__(self):
        # Charge les variables cachées du fichier .env
        load_dotenv()
        self.email = os.getenv("EMAIL_COMPTE")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.imap_server = 'imap.gmail.com'

    def check_new_reports(self):
        """Se connecte à Gmail, extrait les noms des nouveaux rapports signés."""
        if not self.email or not self.password:
            print("Erreur : Identifiants introuvables dans le fichier .env")
            return []

        print("Connexion à Gmail en cours pour vérification...")
        nouveaux_rapports = []
        
        try:
            with MailBox(self.imap_server).login(self.email, self.password) as mailbox:
                
                # On cherche les mails contenant notre mot-clé
                # NOTE: Pour tes tests, enlève `, seen=False` si le mail de test est déjà "lu"
                criteres = AND(subject='rapport_expertise_psychologique', seen=False)
                
                for msg in mailbox.fetch(criteres):
                    sujet = msg.subject
                    
                    # Regex pour capturer le texte entre "psychologique-" et "- XX/XX/XXXX"
                    match = re.search(r'rapport_expertise_psychologique-(.*?)-', sujet)
                    
                    if match:
                        nom_complet = match.group(1).strip()
                        
                        # Logique simple de séparation Nom / Prénom
                        # On part du principe que le dernier mot est le prénom
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