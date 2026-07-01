import os
from openpyxl import Workbook, load_workbook

class ExcelManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Vérifie si l'Excel existe. Sinon, crée un fichier vierge avec les en-têtes."""
        if not os.path.exists(self.file_path):
            print(f"Création du fichier {self.file_path}...")
            wb = Workbook()
            ws = wb.active
            ws.title = "Rapports"
            
            # Création des en-têtes selon notre modèle
            headers = [
                "client", "professionnel", "numero_commande", 
                "status", "date_envoi", "date_reception"
            ]
            ws.append(headers)
            wb.save(self.file_path)

    def get_mock_data(self):
        """Génère de fausses données pour tester l'interface visuelle sans Gmail."""
        return [
            {"client": "Raphaël PHAN", "status": "Envoyé", "numero_commande": "0000000000"},
            {"client": "Naomie CIBIEL", "status": "Reçu", "numero_commande": "Z0130819440"}
        ]