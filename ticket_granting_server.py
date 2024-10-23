#This is the script that takes in a principals ticket-granting-ticket and authenticates it and then issues a service ticket

from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from typing import List
import sqlite3

#Needs to decrypt TGT, extract session_key
#Decrypt user_authenticator message
#Validate data - match ID's, match timestamps, compare ipaddress, check not expired
#Check cache for authenticator ticket, add ticket to cache

def add_to_cache(ID:int,time:str):
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO tgs_cache VALUES ('{ID}', '{time}')""")
    con.commit()
    con.close()

#Now we need to make tickets

@dataclass
class ServiceSessionKeyTicket:
    """Needs to be encrypted with TGS session key"""
    SERVICE_ID : int
    TIMESTAMP : str
    TTL : int
    SERVICE_SESSION_KEY : str

@dataclass
class ServiceTicket:
    """Needs to be encrypted with service session key"""
    UID : int
    SERVICE_ID : int
    TIMESTAMP : str
    IP : ip_address | List[ip_address] | ip_network | None
    SERVICE_TTL : int
    SERVICE_SESSION_KEY : str

