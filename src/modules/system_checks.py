import subprocess
import os
import wdt_utils

wdt = wdt_utils.WDTUtils()

class SystemChecks():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def domain_check(self) -> bool:
        in_domain = wdt.powershell(['(Get-WmiObject -Class Win32_ComputerSystem).PartOfDomain']) == 'True'
        if in_domain == 'True':
            return True
        else:
            return False

    def rsat_check(self) -> bool:
        rsat_check = wdt.powershell(['wmic qfe list full | findstr KB2693643'])
        if rsat_check == 'HotFixID=KB2693643':
            return True
        else:
            return False


