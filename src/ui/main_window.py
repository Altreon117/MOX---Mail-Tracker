import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QSystemTrayIcon, QMenu, QApplication, 
                             QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QScrollArea, QLabel, QFrame)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QTimer, Qt

# On importe APP_NAME en plus
from config import CHECK_INTERVAL_MS, EXCEL_FILE_PATH, APP_NAME
from src.backend.excel_manager import ExcelManager

# --- HACK WINDOWS BARRE DES TÂCHES ---
# Permet d'afficher notre icône au lieu de celle de Python pendant le développement
if os.name == 'nt':
    import ctypes
    myappid = 'monentreprise.suivirapports.app.1' # Identifiant arbitraire unique
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(400, 600)
        
        # 1. Chargement de l'icône personnalisée
        icon_path = os.path.abspath("assets/app_icon.ico")
        self.app_icon = QIcon(icon_path)
        self.setWindowIcon(self.app_icon)
        
        # 2. Initialisation des gestionnaires
        self.excel_manager = ExcelManager(EXCEL_FILE_PATH)
        
        # 3. Configuration de l'UI et du Background
        self.setup_ui()
        self.setup_tray_icon()
        self.setup_timer()
        
        # 4. Charger les fausses données pour tester le visuel
        self.load_dummy_data()

    def setup_ui(self):
        """Construit l'interface graphique principale."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # --- HEADER (Barre de recherche + Bouton Refresh) ---
        header_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search ...")
        
        # Configuration dynamique du bouton Refresh
        self.refresh_btn = QPushButton()
        self.refresh_btn.setFixedSize(30, 30)
        
        refresh_icon_path = os.path.abspath("assets/refresh_icon.ico")
        if os.path.exists(refresh_icon_path):
            self.refresh_btn.setIcon(QIcon(refresh_icon_path))
        else:
            self.refresh_btn.setText("🔄") # Fallback si le fichier n'existe pas
            
        self.refresh_btn.clicked.connect(self.run_background_check)
        
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.refresh_btn)
        
        # --- BODY (Zone défilante pour les rapports) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.reports_container = QWidget()
        self.reports_layout = QVBoxLayout(self.reports_container)
        self.reports_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.reports_container)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.scroll_area)

    def load_dummy_data(self):
        """Crée des composants visuels à partir des fausses données."""
        mock_data = self.excel_manager.get_mock_data()
        
        for data in mock_data:
            item_frame = QFrame()
            item_frame.setFrameShape(QFrame.Shape.StyledPanel)
            item_layout = QHBoxLayout(item_frame)
            
            name_label = QLabel(data["client"])
            status_label = QLabel(data["status"])
            
            item_layout.addWidget(name_label)
            item_layout.addWidget(status_label)
            
            self.reports_layout.addWidget(item_frame)

    # --- MÉTHODES DE BACKGROUND ---

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        
        # Ajout du texte au survol (Tooltip)
        self.tray_icon.setToolTip(APP_NAME)
        
        tray_menu = QMenu()
        
        # Nouvelle action : Scan Mail
        scan_action = QAction("Scan Mail", self)
        scan_action.triggered.connect(self.run_background_check)
        tray_menu.addAction(scan_action)
        
        tray_menu.addSeparator() # Petit séparateur visuel propre
        
        # Modification de l'action Quitter avec le nom de l'app
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