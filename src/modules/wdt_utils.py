import os
import subprocess
import logging
import requests


class WDTUtils():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def powershell(self, input_: list) -> str:
        """
        Returns a string when no error
        If an exception occurs the exeption is logged and None is returned
        """
        try:
            proc = subprocess.Popen(['powershell.exe'] + input_,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE,
                                    cwd=os.getcwd(),
                                    env=os.environ)
            proc.stdin.close()
            outs, errs = proc.communicate(timeout=15)
            return outs.decode('U8')
        except Exception as e:
            return f'Error: {e}'

    def update_check(self, url: str, current_version: float) -> str:
        """"
        Return a string with Latest version if there is no update available. Returns New Version if there is an update
        available.
        Example Url: https://raw.githubusercontent.com/jebr/windows-deployment-tool/master/version.txt
        :param url: link to the raw url of version.txt in the master repo
        """
        try:
            resp = requests.get(url, timeout=2)
        except Exception as e:
            logging.error(f'{e}')
            return ('Connection Error')
        if not resp.ok:
            logging.error(f'{resp.status_code}')
            logging.error(f'{resp.text}')
            return 'Connection Error'
        latest_version = float(resp.text)
        if latest_version <= current_version:
            return 'Latest Version'
        return 'New Version'

    def system_log(self, message: str, errorlevel: str):
        """
        Write a message log to c:\\users\\current-user\\AppData\\Local\\Temp\\WDT\\WDT.log
        :param message: Message to write to the log (str)
        :param errorlevel:  info, error (str)
        """
        current_user = self.powershell(['$env:username']).rstrip()

        # Create temp folder
        if not os.path.exists(f'c:\\users\\{current_user}\\AppData\\Local\\Temp\\WDT'):
            os.makedirs(f'c:\\users\\{current_user}\\AppData\\Local\\Temp\\WDT')

        # Set logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=f'c:\\users\\{current_user}\\AppData\\Local\\Temp\\WDT\\WDT.log',
                            filemode='a')
        # logging.disable(logging.DEBUG)
        # FIXME Console logging alleen voor ontwikkeling, uitzetten bij een release
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        if errorlevel == 'info':
            logging.info(message)
        if errorlevel == 'error':
            logging.error(message)

