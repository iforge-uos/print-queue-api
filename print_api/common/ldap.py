from typing import List, Dict, Union

import ldap3 as ld
from ldap3.core.exceptions import LDAPSocketOpenError
import os


class LDAP:
    def __init__(self):
        self.host_name = os.getenv("LDAP_HOST_NAME")
        self.port = int(os.getenv("LDAP_HOST_PORT"))
        self.connect_timeout = 1

    def _connect(self):
        try:
            conn = ld.Connection(ld.Server(self.host_name, port=self.port, connect_timeout=self.connect_timeout))
            conn.bind()
        except LDAPSocketOpenError:
            raise Exception("Could not connect to LDAP server")
        except Exception as e:
            raise e
        else:
            return conn

    def lookup(self, search_filter: str, attributes: List[str], return_as_str: bool = False) \
            -> Union[Dict[str, List[str]], Dict[str, str], None]:
        """
        Perform a lookup on the LDAP server.

        Args:
            search_filter(str): An LDAP search filter to restrict obtained results
            attributes(List[str]): The attributes to collect from the lookup result
            return_as_str(bool): Determines whether result values will be strings.
                                 By default, result values in Dict will be Lists
        Raises:
            LDAPSocketOpenError: If connection could not be established with the LDAP server
        Returns:
            (Union[Dict[str, List[str]],
            Dict[str, str]): If successful, a Dictionary of containing the result of the lookup.
                             Keys will be the specified attributes
            (None): If unsuccessful, indicates that no results exist for the lookup
        """
        try:
            conn = self._connect()
            conn.search(os.getenv("LDAP_BASE"), search_filter, attributes=attributes)
            result = conn.entries[0]
        except IndexError:  # Means conn.entries does not have any entries i.e no matching info found
            return None
        except LDAPSocketOpenError:
            raise
        except Exception:
            raise
        else:
            if return_as_str:
                return {key: ','.join(value) for key, value in result.entry_attributes_as_dict.items()}
            return result.entry_attributes_as_dict

    def get_dn(self, search_base: str, search_filter: str, attributes: List[str]) -> str:
        """
        Gets DN from a supplied username
        Returns: DN as a string
        """
        try:
            conn = self._connect()
            conn.search(search_base, search_filter, attributes=attributes)
            result = conn.entries[0]
        except IndexError:  # Means conn.entries does not have any entries i.e no matching info found
            raise
        except LDAPSocketOpenError:
            raise
        except Exception:
            raise
        else:
            return result.entry_dn

    def authenticate(self, uid: str, password: str) -> bool:
        """
        Function to authenticate with the sheffield LDAP server
        :param uid: the user's username
        :param password: the user's password
        :return bool success: True if authenticated, False otherwise
        """
        dn = self.get_dn(os.getenv("LDAP_BASE"), f"(&(objectclass=person)(uid={uid}))", ['givenName', 'sn', 'mail'])
        try:
            conn = ld.Connection(
                ld.Server(self.host_name, port=self.port, connect_timeout=self.connect_timeout),
                user=dn, password=password)
            if not conn.bind():
                return False
            else:
                return True
        except LDAPSocketOpenError:
            raise
        except Exception:
            raise
