# main.py
import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication, QDialog, QSplashScreen
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

from styles import APP_STYLE
from config import resource_path

def main():
    if sys.platform == "win32":
        my_app_id = 'com.optiflow.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    
    splash_pix = QPixmap(resource_path("assets/logo.png"))
    bg_pix = QPixmap(500, 500)
    bg_pix.fill(QColor("white"))
    
    if not splash_pix.isNull():
        painter = QPainter(bg_pix)
        scaled_logo = splash_pix.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (500 - scaled_logo.width()) // 2
        y = (500 - scaled_logo.height()) // 2
        painter.drawPixmap(x, y, scaled_logo)
        painter.end()
        
    splash = QSplashScreen(bg_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    
    splash.showMessage("Initialisation de la base de données...", Qt.AlignBottom | Qt.AlignHCenter, Qt.blue)
    app.processEvents()
    
    from models.lens_model import LensModel
    from models.settings_model import SettingsModel
    from views.main_window import MainWindow
    from views.auth.login_dialog import LoginDialog
    from views.auth.activation_dialog import ActivationDialog
    from views.auth.setup_dialog import SetupDialog
    
    LensModel.initialize_matrix()

    # 1. Check License Activation
    if not SettingsModel.is_app_activated():
        splash.finish(None)
        
        # Check if trial is active or can be started
        trial_remaining = SettingsModel.get_trial_days_remaining()
        trial_used = SettingsModel.is_trial_used()
        
        activation_dialog = ActivationDialog()
        # If trial is active, dialog returns Accepted (user clicked "Continue")
        # If trial expired, dialog returns Rejected only if user closes it
        if activation_dialog.exec() == QDialog.Rejected:
            # User closed the dialog without activating or starting trial
            # But if trial is active, we should still allow app to run
            if not SettingsModel.is_trial_active():
                sys.exit(0)

    # 2. Check First-Time Setup
    if not SettingsModel.has_users():
        splash.finish(None)
        setup_dialog = SetupDialog()
        if setup_dialog.exec() == QDialog.Accepted:
            current_user = setup_dialog.current_user
            window = MainWindow(current_user)
            window.show()
            splash.finish(window)
            sys.exit(app.exec())
        else:
            sys.exit(0)

    # 3. Show Login Dialog
    splash.finish(None)
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        current_user = login_dialog.current_user
        window = MainWindow(current_user)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()