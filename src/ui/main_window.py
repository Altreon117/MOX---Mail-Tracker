from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QStyle, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Suivi des Rapports")
        self.resize(400, 600)
        
        self.setup_tray_icon()
        self.setup_timer()

    def setup_tray_icon(self):
        """Configure l'icône dans la barre des tâches et son menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Menu clic-droit
        tray_menu = QMenu()
        quit_action = QAction("Quitter l'application", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Action au double-clic
        self.tray_icon.activated.connect(self.on_tray_click)

    def setup_timer(self):
        """Configure le chronomètre pour vérifier les mails toutes les 10 minutes."""
        from config import CHECK_INTERVAL_MS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_background_check)
        self.timer.start(CHECK_INTERVAL_MS)

    def run_background_check(self):
        """Fonction appelée automatiquement par le timer."""
        print("Timer déclenché : Lancement de la vérification des mails...")
        # Ici on appellera MailConnector plus tard

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        """Intercepte le clic sur la croix rouge pour cacher la fenêtre au lieu de la fermer."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application réduite",
            "La vérification des rapports continue en arrière-plan.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )