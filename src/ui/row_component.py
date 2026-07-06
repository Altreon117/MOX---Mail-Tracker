import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from config import URL_SUIVI_POSTE

class RowComponent(QFrame):
    def __init__(self, data, update_callback):
        super().__init__()
        self.data = data
        self.update_callback = update_callback 
        self.is_expanded = False
        
        self.setup_ui()

    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("QFrame { border: 1px solid gray; border-radius: 5px; margin-bottom: 5px; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # --- PARTIE HAUTE ---
        self.top_row = QWidget()
        self.top_row.setStyleSheet("border: none; margin: 0px;")
        top_layout = QHBoxLayout(self.top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Concaténation du nom et du prénom
        nom_complet = f"{self.data['nom']} {self.data['prenom']}"
        self.name_label = QLabel(nom_complet)
        self.name_label.setStyleSheet("font-weight: bold; border: none;")
        
        self.status_label = QLabel(self.data["status"])
        self.status_label.setStyleSheet("border: none;")
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_expand)

        top_layout.addWidget(self.name_label)
        top_layout.addStretch()
        top_layout.addWidget(self.status_label)
        top_layout.addWidget(self.toggle_btn)

        # --- PARTIE BASSE ---
        self.bottom_row = QWidget()
        self.bottom_row.setStyleSheet("border: none; margin: 0px;")
        bottom_layout = QVBoxLayout(self.bottom_row)
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        cmd_layout = QHBoxLayout()
        numero_commande = self.data.get('numero_commande', 'N/A')
        self.cmd_label = QLabel(f"Commande n° : {numero_commande}")
        
        self.suivre_btn = QPushButton("Suivre")
        self.suivre_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.suivre_btn.clicked.connect(self.ouvrir_suivi)
        
        cmd_layout.addWidget(self.cmd_label)
        cmd_layout.addWidget(self.suivre_btn)

        self.recu_btn = QPushButton("Rapport reçu")
        self.recu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.recu_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #777;
                border-radius: 5px;
                padding: 5px;
                background-color: transparent;
            }
            QPushButton:hover:!disabled {
                background-color: #bca0dc;
                border-color: #bca0dc;
                color: black;
            }
            QPushButton:disabled {
                border: 2px solid #555;
                background-color: #333;
                color: #777;
            }
        """)

        self.recu_btn.clicked.connect(self.mettre_en_recu)
        
        if self.data["status"] == "Reçu":
            self.recu_btn.setEnabled(False)

        bottom_layout.addLayout(cmd_layout)
        bottom_layout.addWidget(self.recu_btn)

        self.bottom_row.setVisible(False)

        self.layout.addWidget(self.top_row)
        self.layout.addWidget(self.bottom_row)

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        self.bottom_row.setVisible(self.is_expanded)
        self.toggle_btn.setText("︿" if self.is_expanded else "☰")

    def ouvrir_suivi(self):
        """Redirige vers l'URL spécifique si un numéro existe, sinon vers l'URL de base."""
        numero = self.data.get('numero_commande', '')
        if numero and numero != "N/A":
            # Redirection directe avec le numéro injecté dans l'URL
            webbrowser.open(f"https://www.laposte.fr/outils/suivre-vos-envois?code={numero}")
        else:
            # Redirection classique
            webbrowser.open(URL_SUIVI_POSTE)

    def mettre_en_recu(self):
        self.data["status"] = "Reçu"
        self.status_label.setText("Reçu")
        self.recu_btn.setEnabled(False)
        # On passe désormais le nom ET le prénom
        self.update_callback(self.data["nom"], self.data["prenom"])