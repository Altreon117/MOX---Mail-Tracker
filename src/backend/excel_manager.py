import os
from openpyxl import Workbook, load_workbook

class ExcelManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Vérifie si l'Excel existe. Sinon, crée le fichier avec en-têtes ET fausses données."""
        if not os.path.exists(self.file_path):
            print(f"Création du fichier {self.file_path} avec données de test...")
            wb = Workbook()
            ws = wb.active
            ws.title = "Rapports"
            
            # Création des en-têtes
            headers = ["client", "professionnel", "numero_commande", "status", "date_envoi", "date_reception"]
            ws.append(headers)
            
            # Injection des fausses données directement dans les cellules Excel
            ws.append(["Raphaël PHAN", "Dr. Goetz", "N/A", "Envoyé", "19/06/2026", ""])
            ws.append(["Pablo LANCEL", "Dr. Goetz", "N/A", "Reçu", "19/06/2026", "20/06/2026"])
            
            wb.save(self.file_path)

    def read_data(self):
        """Lit le fichier Excel et renvoie une liste de dictionnaires pour l'UI."""
        wb = load_workbook(self.file_path)
        ws = wb.active
        data = []
        
        # On lit à partir de la ligne 2 pour ignorer les en-têtes
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # Si la cellule "client" n'est pas vide
                data.append({
                    "client": row[0],
                    "professionnel": row[1],
                    "numero_commande": row[2],
                    "status": row[3],
                    "date_envoi": row[4],
                    "date_reception": row[5]
                })
        return data

    def update_status_to_recu(self, client_name):
        """Cherche le client dans l'Excel et met son statut à 'Reçu'."""
        wb = load_workbook(self.file_path)
        ws = wb.active
        for row in ws.iter_rows(min_row=2):
            if row[0].value == client_name:
                row[3].value = "Reçu"  # La colonne D (index 3) est le status
                break
        wb.save(self.file_path)