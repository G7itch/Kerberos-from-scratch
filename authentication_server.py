#This is the script that authenticates the principal in the realm and generates ticket-granting-tickets

from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from typing import List


TGS_ID = "CHANGE_ME"
SECRET_KEY = "this_is_the_TGS_secret_key"

@dataclass
class TGT:
    """Needs the be encrypted with TGS secret key"""
    UID : int
    TGS_ID : int
    TIMESTAMP : str
    IP : ip_address | List[ip_address] | ip_network | None
    TTL : int
    SESSION_KEY : str


@dataclass
class User_Auth_Ticket:
    """Needs to be encrypted with clients secret key"""
    TGS_ID : int
    TIMESTAMP : str
    TTL : int
    SESSION_KEY : str

