import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QSystemTrayIcon, QMenu, QApplication, 
                             QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QScrollArea, QLabel, QFrame)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer, Qt

from config import CHECK_INTERVAL_MS, EXCEL_FILE_PATH, APP_NAME
from src.backend.excel_manager import ExcelManager

# On importe notre nouveau composant
from src.ui.row_component import RowComponent

# --- HACK WINDOWS BARRE DES TÂCHES ---
if os.name == 'nt':
    import ctypes
    myappid = 'monentreprise.suivirapports.app.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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
        
        # On charge la vraie donnée depuis l'Excel
        self.load_data_from_excel()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search ...")
        # Activation de la recherche en temps réel
        self.search_bar.textChanged.connect(self.filter_reports)
        
        # Nouveau bouton Refresh 100% texte (Unicode)
        self.refresh_btn = QPushButton("↻") 
        self.refresh_btn.setFixedSize(30, 30)
        
        # On grossit un peu la police pour que le symbole prenne bien l'espace
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
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.scroll_area)

    def load_data_from_excel(self):
        """Lit l'Excel et instancie un RowComponent par ligne."""
        # On vide la liste actuelle avant de recharger
        for i in reversed(range(self.reports_layout.count())): 
            self.reports_layout.itemAt(i).widget().setParent(None)

        excel_data = self.excel_manager.read_data()
        
        for data in excel_data:
            # On instancie le composant en lui passant la donnée et la fonction de sauvegarde
            row = RowComponent(data, self.on_status_changed)
            self.reports_layout.addWidget(row)

    def filter_reports(self, text):
        """Filtre les composants affichés selon le texte de la barre de recherche."""
        search_text = text.lower()
        for i in range(self.reports_layout.count()):
            widget = self.reports_layout.itemAt(i).widget()
            if isinstance(widget, RowComponent):
                client_name = widget.data["client"].lower()
                # On cache le composant si le nom ne correspond pas à la recherche
                widget.setVisible(search_text in client_name)

    def on_status_changed(self, client_name):
        """Callback appelé par un RowComponent quand on clique sur 'Rapport reçu'."""
        self.excel_manager.update_status_to_recu(client_name)
        print(f"Statut mis à jour dans l'Excel pour {client_name}")

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
        # On rechargera les données de l'Excel ici après le scan

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        event.ignore()
        self.hide()