from ldap3 import Server, Connection, ALL
import os


def get_ldap_data(username: str) -> list:
    """
    Function that will take a username and lookup ldap data that correspons to that username.
    :param username: the username to search for
    :return dict: a dictionary of ldap data containing the username, first name, last name, and email address
    """
    server = Server(host=os.getenv('LDAP_HOST'), port=int(
        os.getenv('LDAP_PORT')), get_info=ALL, connect_timeout=2)
    conn = Connection(server, auto_bind=True)
    conn.search(os.getenv('LDAP_BASE_DN'), f'(&(objectclass=person)(uid={username}))', attributes=[
                'uid', 'givenName', 'sn', 'mail'])
    return conn.response[0]['attributes']
