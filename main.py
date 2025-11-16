"""
Advanced Modular File Organization System
Main entry point for the application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced File Organizer")
    app.setOrganizationName("FileOrgSystem")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()