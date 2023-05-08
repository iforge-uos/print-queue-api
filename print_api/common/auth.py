from print_api.common.ldap import LDAP


def ldap_authenticate(uid: str, password: str) -> bool:
    """
    Function to authenticate with the sheffield LDAP server
    :param uid: the user's username
    :param password: the user's password
    :return bool success: True if authenticated, False otherwise
    """
    ldap = LDAP()
    return ldap.authenticate(uid, password)
