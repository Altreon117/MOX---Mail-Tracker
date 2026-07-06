import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from config import URL_SUIVI_POSTE

class RowComponent(QFrame):
    def __init__(self, data, update_callback):
        super().__init__()
        self.data = data
        self.update_callback = update_callback  # Fonction de MainWindow pour MAJ l'Excel
        self.is_expanded = False
        
        self.setup_ui()

    def setup_ui(self):
        # Style de la bordure arrondie
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("QFrame { border: 1px solid gray; border-radius: 5px; margin-bottom: 5px; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # --- PARTIE HAUTE (Toujours visible) ---
        self.top_row = QWidget()
        self.top_row.setStyleSheet("border: none; margin: 0px;") # Retire la bordure interne
        top_layout = QHBoxLayout(self.top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.name_label = QLabel(self.data["client"])
        self.name_label.setStyleSheet("font-weight: bold; border: none;")
        
        self.status_label = QLabel(self.data["status"])
        self.status_label.setStyleSheet("border: none;")
        
        # Bouton pour agrandir
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_expand)

        top_layout.addWidget(self.name_label)
        top_layout.addStretch()  # Pousse le reste vers la droite
        top_layout.addWidget(self.status_label)
        top_layout.addWidget(self.toggle_btn)

        # --- PARTIE BASSE (Cachée par défaut) ---
        self.bottom_row = QWidget()
        self.bottom_row.setStyleSheet("border: none; margin: 0px;")
        bottom_layout = QVBoxLayout(self.bottom_row)
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        cmd_layout = QHBoxLayout()
        self.cmd_label = QLabel(f"Commande n° : {self.data.get('numero_commande', 'N/A')}")
        self.suivre_btn = QPushButton("Suivre")
        self.suivre_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.suivre_btn.clicked.connect(self.ouvrir_suivi)
        
        cmd_layout.addWidget(self.cmd_label)
        cmd_layout.addWidget(self.suivre_btn)

        self.recu_btn = QPushButton("Rapport reçu")
        self.recu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.recu_btn.clicked.connect(self.mettre_en_recu)
        
        # Si c'est déjà reçu dans l'Excel, on grise le bouton
        if self.data["status"] == "Reçu":
            self.recu_btn.setEnabled(False)

        bottom_layout.addLayout(cmd_layout)
        bottom_layout.addWidget(self.recu_btn)

        # On cache la partie basse au démarrage
        self.bottom_row.setVisible(False)

        # Ajout au layout principal de la frame
        self.layout.addWidget(self.top_row)
        self.layout.addWidget(self.bottom_row)

    def toggle_expand(self):
        """Alterne l'affichage de la partie basse."""
        self.is_expanded = not self.is_expanded
        self.bottom_row.setVisible(self.is_expanded)
        self.toggle_btn.setText("︿" if self.is_expanded else "☰")

    def ouvrir_suivi(self):
        webbrowser.open(URL_SUIVI_POSTE)

    def mettre_en_recu(self):
        """Action déclenchée par le bouton 'Rapport reçu'."""
        self.data["status"] = "Reçu"
        self.status_label.setText("Reçu")
        self.recu_btn.setEnabled(False)
        # On informe la fenêtre principale qu'il faut modifier l'Excel
        self.update_callback(self.data["client"])