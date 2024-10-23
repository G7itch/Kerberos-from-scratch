#This is the resource on the network being requested
import sqlite3
from dataclasses import dataclass
import socket

SERVICE_ID = "0002"
SECRET_KEY = "athis_is_the_service_secret_key"

def set_up_DB() -> None:
    """Set up the database"""
    con = sqlite3.connect("service.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE service_cache(UID UNIQUE NOT NULL, timestamp NOT NULL)")
    cur.execute("""INSERT INTO service_cache VALUES ('1234', 'example_timestamp')""")
    con.commit()
    con.close()

def search_DB(table:str, search_field: str, search_item: str, return_fields: tuple) -> bool:
    """Search the database for an item"""
    con = sqlite3.connect("service.db")
    cur = con.cursor()

    return_fields = str(str(return_fields)[1:-1])
    return_fields = return_fields.replace("'", "")

    command = f"""SELECT {return_fields} FROM {table} WHERE {search_field} = '{search_item}'"""

    res = cur.execute(command)
    res = res.fetchone()
    con.close()

    return not(res is None)

def clear_service_cache(time:str):
    last_recorded_clear = time
    con = sqlite3.connect("service.db")
    cur = con.cursor()
    cur.execute("DELETE FROM service_cache")
    con.close()
    return last_recorded_clear

def add_to_cache(ID:int,time:str):
    con = sqlite3.connect("service.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO service_cache VALUES ('{ID}', '{time}')""")
    con.commit()
    con.close()

#decrypt the service ticket
#decrypt the user authenticator ticket
#validate data: match userid, timestamps, compare ips, check if TTL is valid

#check service cache, add ticket to cache

@dataclass
class ServiceAuthenticator:
    """Needs to be encrypted with service session key"""
    SERVICE_ID : int
    TIMESTAMP : str

#send this ticket to user

#finally data is sent encrypted with service session key