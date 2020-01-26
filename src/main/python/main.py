from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QFileDialog, QMessageBox, QDialog

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap,  QFont
import sys
import os
import logging
import platform
import webbrowser
import urllib3
import subprocess

# Globals
current_version = float(1.0)
version_check = 'https://raw.githubusercontent.com/jebr/WDS-ResetPass/master/version.txt'
repo_home = 'https://github.com/jebr/WDS-ResetPass'
repo_release = 'https://github.com/jebr/WDS-ResetPass/releases'
logo_icon = '../icons/logo.png'
app_title = 'WDS-Resetpass'

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


# Set logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

# What OS is running
what_os = platform.system()
if 'Windows' in what_os:
    username = os.environ.get('USERNAME')
    start_location = 'c:\\Users\\{}\\Documents'.format(username)
    logging.info('OS: Windows')
elif 'Linux' in what_os:
    username = os.environ.get('USER')
    start_location = '/home/{}/Documents'.format(username)
    logging.info('OS: Linux')
elif 'Darwin' in what_os:
    username = os.environ.get('USER')
    start_location = '/Users/{}/Documents'.format(username)
    logging.info('OS: MacOS')
else:
    exit()


# PyQT GUI
class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load Main UI
        loadUi(resource_path('../resources/ui/main_window.ui'), self)
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

        # Check user in domain
        self.domain_check = subprocess.check_output(['powershell.exe',
                                                     '(Get-WmiObject -Class Win32_ComputerSystem).PartOfDomain'],
                                                    encoding='utf-8')

        if 'False' in self.domain_check:
            logging.info('User in domain: {}'.format(self.domain_check))
            self.criticalbox('Your PC is not a member of a domain.\n\nThis application works only on a computer'
                             '\nwhich is part of a domain.')
            exit()
        if 'True' in self.domain_check:
            logging.info('User in domain: {}'.format(self.domain_check))

        # Check account name
        self.current_user = subprocess.check_output(['powershell.exe', 'whoami'], encoding='utf-8')
        self.current_user = self.current_user.split('\\')
        self.label_account.setText('Your account: {}'.format(self.current_user[1]))
        # Check user security group
        self.user_groups = subprocess.check_output(['gpresult', '-r'], shell=True)
        self.user_groups = str(self.user_groups)
        # TODO Account operator heeft onvoldoende rechten
        if 'Account Operators' in self.user_groups:
            self.label_role.setText('Your role: Account Operator')
            logging.info('Role user: Account operator')
        elif 'Administrator' in self.user_groups:
            self.label_role.setText('Your role: Administrator')
            logging.info('Role user: Administrator')
        else:
            self.criticalbox('You have insufficient rights to change a users password\n\n'
                             'Ask your system administrator for more information')

        # Change password Windows user
        self.lineEdit_account_password.setEchoMode(2)  # Hide password
        self.pushButton_reset.clicked.connect(self.reset_password)


    def website_update(self):
        webbrowser.open(repo_release)

    def check_update(self):
        # Version check
        try:
            timeout = urllib3.Timeout(connect=2.0, read=7.0)
            http = urllib3.PoolManager(timeout=timeout)
            response = http.request('GET', version_check)
            data = response.data.decode('utf-8')

            new_version = float(data)

            if current_version < new_version:
                logging.info('Current software version: v{}'.format(current_version))
                logging.info('New software version available v{}'.format(new_version))
                logging.info(repo_release)
                self.infobox_update('There is an update available\n Do you want to download it now?')
                self.statusBar().showMessage('New software version available v' + str(new_version))
                self.actionUpdate.setEnabled(True)
            else:
                logging.info('Current software version: v{}'.format(current_version))
                logging.info('Latest release: v{}'.format(new_version))
                logging.info('Software up-to-date')
                self.statusBar().showMessage('{} v'.format(app_title) + str(new_version))
                self.actionUpdate.setEnabled(False)

        except urllib3.exceptions.MaxRetryError:
            logging.error('No internet connection, max retry error')
        except urllib3.exceptions.ResponseError:
            logging.error('No internet connection, no response error')

    # TODO Functie uitzoeken
    def reset_password(self):
        account_name = self.lineEdit_account_name.text()
        account_new_password = self.lineEdit_account_password.text()
        # Check input
        if not account_name:
            logging.info('Please fill in account name')
        elif not account_new_password:
            logging.info('Please fill in new password')
        else:
            try:
                subprocess.check_call(['powershell', 'Set-ADAccountPassword –Identity {} –Reset '
                                                 '–NewPassword (ConvertTo-SecureString '
                                                 '-AsPlainText {} -Force)'.format(account_name,
                                                                                  account_new_password)])
                logging.info('Password changed for user: {}'.format(account_name))
                self.infobox('Password reset completed for user {}'.format(account_name))
            except subprocess.CalledProcessError:
                self.warningbox('Can\'t change password of user {}'.format(account_name))
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
        loadUi(resource_path('../resources/ui/info_dialog.ui'), self)
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
