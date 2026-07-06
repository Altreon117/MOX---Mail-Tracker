from PyQt6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QLineEdit, 
                             QCheckBox, QDialogButtonBox, QLabel)
from PyQt6.QtCore import QSettings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        # --- FENÊTRE AGRANDIE ---
        self.resize(500, 300)
        
        self.settings = QSettings("MonEntreprise", "SuiviRapports")
        
        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20) # Ajoute de l'espace entre les lignes pour que ce soit moins tassé
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setSuffix(" min")
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("ex: rapport_expertise-X- X")
        
        self.subject_help = QLabel("<i>Utilisez 'X' pour remplacer le Nom et la Date.</i>")
        self.subject_help.setStyleSheet("color: gray; font-size: 11px;")
        
        self.landscape_checkbox = QCheckBox("Mode Paysage (Large)")
        
        layout.addRow("Rafraîchissement :", self.interval_spinbox)
        layout.addRow("Format de l'objet :", self.subject_input)
        layout.addRow("", self.subject_help)
        layout.addRow("Affichage :", self.landscape_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        
        # Ajout d'un espacement avant les boutons
        layout.addRow("", QLabel("")) 
        layout.addRow("", self.button_box)

    def load_current_settings(self):
        interval = self.settings.value("refresh_interval", 10, type=int)
        subject = self.settings.value("subject_template", "rapport_expertise_psychologique-X- X", type=str)
        landscape = self.settings.value("landscape_mode", False, type=bool)
        
        self.interval_spinbox.setValue(interval)
        self.subject_input.setText(subject)
        self.landscape_checkbox.setChecked(landscape)

    def save_settings(self):
        self.settings.setValue("refresh_interval", self.interval_spinbox.value())
        self.settings.setValue("subject_template", self.subject_input.text().strip())
        self.settings.setValue("landscape_mode", self.landscape_checkbox.isChecked())
        self.accept()