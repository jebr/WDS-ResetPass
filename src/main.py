import domain as domain
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFileDialog, QMessageBox, QDialog

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap,  QFont
import sys
import os
import logging
import webbrowser
import subprocess
import system_checks
import domain_tools
import wdt_utils

# Instances
system_checks = system_checks.SystemChecks()
domain_tools = domain_tools.DomainTools()
wdt_utils = wdt_utils.WDTUtils()

# Globals
current_version = float(1.0)
version_check = 'https://raw.githubusercontent.com/jebr/WDS-ResetPass/master/version.txt'
repo_home = 'https://github.com/jebr/WDS-ResetPass'
repo_release = 'https://github.com/jebr/WDS-ResetPass/releases'
logo_icon = 'icons/logo.png'
app_title = 'WDS-Resetpass'
current_user = wdt_utils.powershell(['$env:username']).rstrip()

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except Exception:
    pass


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# PyQT GUI
class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Main UI
        loadUi(resource_path('resources/ui/main_window.ui'), self)
        # Set Size Application
        self.setFixedSize(407, 291)
        # Set Application Icon
        self.setWindowIcon(QtGui.QIcon(resource_path(logo_icon)))
        self.setWindowTitle(app_title)
        # Logo
        # label_logo
        # self.label_logo = QLabel(self)
        # self.label_logo.setGeometry(50, 40, 50, 50)
        # pixmap = QPixmap(resource_path(logo_icon))
        # pixmap = pixmap.scaledToWidth(50)
        # self.label_logo.setPixmap(pixmap)

        # Info menu
        self.actionInfo.triggered.connect(self.open_info_window)

        # Initial update check
        # self.check_update()

        # Update button
        self.actionUpdate.triggered.connect(self.website_update)

        # Pre-checks
        if not system_checks.domain_check():
            self.criticalbox('Your PC is not a member of a domain.\n\nThis application works only on a computer'
                             '\nwhich is part of a domain.')
            # sys.exit()

        if not system_checks.rsat_check():
            self.criticalbox('RSAT is not installed on this PC\n\nAsk your system administrator for help')
            # sys.exit()

        if not domain_tools.check_admin_user(f'{current_user}'):
            self.criticalbox('Insufficient rights to use this application\n\nAsk your system administrator for help')
            # sys.exit()

        # # TODO Lijst opvragen met Domain Users en deze weergeven in het veld lineEdit_account_name
        # # Powershell command
        # # Get-ADUser -filter * | select-object Name, SamAccountName
        # # Gebruiker Administrator, Heijmans, Servicehut en eigen account uit de lijst filteren
        #
        # # Change password Windows user
        self.lineEdit_account_password.setEchoMode(2)  # Hide password
        self.pushButton_reset.clicked.connect(self.reset_password)


    def website_update(self):
        webbrowser.open(repo_release)

    # TODO Functie uitzoeken
    def reset_password(self):
        account_name = self.lineEdit_account_name.text()
        account_new_password = self.lineEdit_account_password.text()
        # Check input
        if not account_name:
            self.infobox('Please fill in the account name')
        elif not account_new_password:
            self.infobox('Please fill in the new password')
        else:
            # set-adaccountpassword -identity test1 -Reset -NewPassword (convertto-securestring -asplaintext "Computer-02" -force)
            try:
                subprocess.check_call(['powershell', 'Set-ADAccountPassword –Identity {} –Reset '
                                                 '–NewPassword (ConvertTo-SecureString '
                                                 '-AsPlainText {} -Force)'.format(account_name,
                                                                                  account_new_password)])
                # Powershell command
                # Set-ADAccountPassword –Identity {} –Reset –NewPassword (ConvertTo-SecureString -AsPlainText {} -Force)
                wdt_utils.system_log(f'Password changed for user: {account_name}', 'info')
                self.infobox(f'Password reset completed for user {account_name}')
            except subprocess.CalledProcessError:
                self.warningbox(f'Can\'t change password of user {account_name}')
            finally:
                self.lineEdit_account_name.clear()
                self.lineEdit_account_password.clear()

    def open_info_window(self):
        info_window_ = InfoWindow()
        info_window_.exec_()

    # Messageboxen
    def criticalbox(self, message):
        buttonReply = QMessageBox.critical(self, 'Error', message, QMessageBox.Close)

    def warningbox(self, message):
        buttonReply = QMessageBox.warning(self, 'Warning', message, QMessageBox.Close)

    def infobox(self, message):
        buttonReply = QMessageBox.information(self, 'Info', message, QMessageBox.Close)

    def infobox_update(self, message):
        buttonReply = QMessageBox.information(self, 'Info', message, QMessageBox.Yes, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            webbrowser.open(repo_release)


class InfoWindow(QDialog):
    def __init__(self):
        super().__init__(None, QtCore.Qt.WindowCloseButtonHint)
        loadUi(resource_path('resources/ui/info_dialog.ui'), self)
        self.setWindowIcon(QtGui.QIcon(resource_path(logo_icon)))
        self.setFixedSize(320, 240)
        self.setWindowTitle(app_title)
        # Logo
        self.label_info_logo.setText("")
        self.label_info_logo = QLabel(self)
        info_icon = QPixmap(resource_path(logo_icon))
        info_icon = info_icon.scaledToWidth(40)
        self.label_info_logo.setPixmap(info_icon)
        # TODO Nakijken of dit nog nodig is na het nieuwe onwerp
        if 'Darwin' in what_os:
            self.label_info_logo.move(70, 20)
        else:
            self.label_info_logo.move(50, 25)
        # Labels
        self.label_info_title.setText('WDS v{}'.format(current_version))
        self.label_info_copyright.setText('Copyright {} {} 2020'.format('©', ' <a href="https://switchit.nu">SwitchIT</a'))
        self.label_info_copyright.setOpenExternalLinks(True)
        self.label_info_link.setText('<a href="{}">GitHub repository</a>'.format(repo_home))
        self.label_info_link.setOpenExternalLinks(True)
        self.label_info_dev.setText('Developers\nJeroen Brauns')


def main():
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
