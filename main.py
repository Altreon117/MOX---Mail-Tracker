import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Empêche la fermeture du programme quand on masque l'interface
    app.setQuitOnLastWindowClosed(False) 
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()