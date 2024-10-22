#This is a user or a service that wants access to a resource on the network

from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from typing import List
from hashlib import sha256
import sqlite3


#The user needs a secret key and an ID. the secetkey is generated based on a username and password
SECRET_KEY = ""
UID = 'userID goes here'

def login() -> tuple:
    username = str(input("Please enter your username: "))
    password = str(input("Please enter your password: "))
    domain = str(input("Please enter a domain you are authenticated with and a resource exists on that you wish to access: "))
    return username,password,domain

def generate_secret_key(username: str, password:str, domain:str, version_number: int = 0) -> str:
    unhashed_key = password + username + "@" + domain + str(version_number)
    key_bytes = unhashed_key.encode('UTF-8')
    hashed_key = sha256(key_bytes).hexdigest()
    return hashed_key

def set_up_DB() -> None:
    """Set up the database"""
    con = sqlite3.connect("user.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE user_cache(UID UNIQUE NOT NULL, timestamp NOT NULL)")
    cur.execute("""INSERT INTO user_cache VALUES ('1234', 'example_timestamp')""")
    con.commit()
    con.close()

def search_DB(table:str, search_field: str, search_item: str, return_fields: tuple) -> bool:
    """Search the database for an item"""
    con = sqlite3.connect("user.db")
    cur = con.cursor()

    return_fields = str(str(return_fields)[1:-1])
    return_fields = return_fields.replace("'", "")

    command = f"""SELECT {return_fields} FROM {table} WHERE {search_field} = '{search_item}'"""

    res = cur.execute(command)
    res = res.fetchone()
    con.close()

    return not(res is None)

def clear_user_cache(time:str):
    last_recorded_clear = time
    con = sqlite3.connect("user.db")
    cur = con.cursor()
    cur.execute("DELETE FROM user_cache")
    con.close()
    return last_recorded_clear

def add_to_cache(ID:int,time:str):
    con = sqlite3.connect("user.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO user_cache VALUES ('{ID}', '{time}')""")
    con.commit()
    con.close()

username, password, domain = login()
SECRET_KEY = generate_secret_key(username, password, domain)  


#The first thing the user needs to do is generate an inital request
@dataclass
class InitialRequest:
    """Class that is used to generate the message for to get the TGT"""
    UID : int
    SERVICE_ID : int
    IP : ip_address | List[ip_address] | ip_network | None
    TTL : int


#Once the inital request has been made, it is sent to the KDC
#Need to decrypt User_Auth_Ticket
#If the user is authenticated properly then they make more requests
@dataclass
class ServiceAccessRequest:
    SERVICE_ID : int
    TTL : int

@dataclass
class UserAuthenticator:
    """Needs to be encrypted with the TGS session key"""
    UID : int
    TIMESTAMP : str

#these messages are sent along with the TGT, to the TGS
#after the tgs validates our tickets and logs our request they send a couple of tickets back

#decrypt ServiceSessionKeyTicket using tgs session key

#create new UserAuthenticator ticket and encrypt it with the service session key

#forward this new ticket and the service ticket to the service

#Decrypt serviceauthenticator with service session key. verify
#check timestamp

#check cache, add auth

#finally data is sent encrypted with service session key
