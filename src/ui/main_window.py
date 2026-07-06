import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QSystemTrayIcon, QMenu, QApplication, 
                             QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QScrollArea, QLabel, QFrame,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer, Qt

from config import CHECK_INTERVAL_MS, EXCEL_FILE_PATH, APP_NAME
from src.backend.excel_manager import ExcelManager
from src.ui.row_component import RowComponent

if os.name == 'nt':
    import ctypes
    myappid = 'monentreprise.suivirapports.app.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class AddReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un rapport manuellement")
        self.resize(300, 180)
        
        layout = QFormLayout(self)
        
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Optionnel (ex: Z01308...)")
        
        layout.addRow("Nom :", self.nom_input)
        layout.addRow("Prénom :", self.prenom_input)
        layout.addRow("N° de commande :", self.cmd_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        
    def get_data(self):
        # On force le nom de famille en majuscules pour garder un fichier Excel propre
        return (self.nom_input.text().strip().upper(), 
                self.prenom_input.text().strip(), 
                self.cmd_input.text().strip())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(400, 600)
        
        icon_path = os.path.abspath("assets/app_icon.ico")
        self.app_icon = QIcon(icon_path)
        self.setWindowIcon(self.app_icon)
        
        self.excel_manager = ExcelManager(EXCEL_FILE_PATH)
        
        self.setup_ui()
        self.setup_tray_icon()
        self.setup_timer()
        
        self.load_data_from_excel()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search ...")
        self.search_bar.textChanged.connect(self.filter_reports)
        
        self.refresh_btn = QPushButton("↻") 
        self.refresh_btn.setFixedSize(30, 30)
        font = self.refresh_btn.font()
        font.setPointSize(14)
        font.setBold(True)
        self.refresh_btn.setFont(font)
        self.refresh_btn.clicked.connect(self.run_background_check)
        
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.refresh_btn)
        
        # --- BODY ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.reports_container = QWidget()
        self.reports_layout = QVBoxLayout(self.reports_container)
        self.reports_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.reports_container)
        
        # --- BOUTON AJOUTER ---
        self.add_btn = QPushButton("➕ Ajouter un rapport")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.add_btn)

    def open_add_dialog(self):
        dialog = AddReportDialog(self)
        if dialog.exec():
            nom, prenom, numero_commande = dialog.get_data()
            if nom and prenom: 
                self.excel_manager.add_new_report(nom, prenom, numero_commande)
                self.load_data_from_excel() 
            else:
                QMessageBox.warning(self, "Erreur", "Le nom et le prénom sont obligatoires.")

    def load_data_from_excel(self):
        for i in reversed(range(self.reports_layout.count())): 
            self.reports_layout.itemAt(i).widget().setParent(None)

        excel_data = self.excel_manager.read_data()
        
        for data in excel_data:
            row = RowComponent(data, self.on_status_changed)
            self.reports_layout.addWidget(row)

    def filter_reports(self, text):
        search_text = text.lower()
        for i in range(self.reports_layout.count()):
            widget = self.reports_layout.itemAt(i).widget()
            if isinstance(widget, RowComponent):
                # On concatène nom et prénom pour que la recherche trouve les deux
                nom_complet = f"{widget.data['nom']} {widget.data['prenom']}".lower()
                widget.setVisible(search_text in nom_complet)

    def on_status_changed(self, nom, prenom):
        self.excel_manager.update_status_to_recu(nom, prenom)
        print(f"Statut mis à jour dans l'Excel pour {prenom} {nom}")

    # --- MÉTHODES DE BACKGROUND ---

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip(APP_NAME)
        
        tray_menu = QMenu()
        
        scan_action = QAction("Scan Mail", self)
        scan_action.triggered.connect(self.run_background_check)
        tray_menu.addAction(scan_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction(f"Quitter {APP_NAME}", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_click)

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_background_check)
        self.timer.start(CHECK_INTERVAL_MS)

    def run_background_check(self):
        print("Vérification manuelle ou automatique lancée...")

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        event.ignore()
        self.hide()