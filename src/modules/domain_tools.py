import wdt_utils

wdt = wdt_utils.WDTUtils()

class DomainTools():
    def __init__(self):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def check_admin_user(self, samaccountname: str):
        """
        Check user in group Domain Admin or System Operator
        """
        try:
            memberof = wdt.powershell([f'get-aduser -Identity {samaccountname} -properties Memberof).memberof']).lower()
            if 'domain admin' in memberof:
                return True
            if 'account operator' in memberof:
                return True
            else:
                return False
        except Exception as e:
            return f'check_admin_user - Error: {e}'


