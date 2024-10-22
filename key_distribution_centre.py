#This is the server that combines the authentication-server script and the ticket-granting-server script
#KDC needs to be able to register a new user

import importlib
import sqlite3
import authentication_server
import ticket_granting_server
from hashlib import sha256

def set_up_DB() -> None:
    """Set up the database"""
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE users(ID UNIQUE NOT NULL, secret_key NOT NULL)")
    cur.execute("""INSERT INTO users VALUES ('1234', 'example_secret_key')""")
    cur.execute("CREATE TABLE services(SERVICE_ID UNIQUE NOT NULL, secret_key NOT NULL)")
    cur.execute("""INSERT INTO services VALUES ('0000', 'example_secret_key')""")
    cur.execute("CREATE TABLE tgs_cache(UID UNIQUE NOT NULL, timestamp NOT NULL)")
    cur.execute("""INSERT INTO tgs_cache VALUES ('1234', 'example_timestamp')""")
    con.commit()
    con.close()

def search_DB(table:str, search_field: str, search_item: str, return_fields: tuple) -> bool:
    """Search the database for an item"""
    con = sqlite3.connect("master.db")
    cur = con.cursor()

    return_fields = str(str(return_fields)[1:-1])
    return_fields = return_fields.replace("'", "")

    command = f"""SELECT {return_fields} FROM {table} WHERE {search_field} = '{search_item}'"""

    res = cur.execute(command)
    res = res.fetchone()
    con.close()

    return not(res is None)

def generate_secret_key(username: str, password:str, domain:str, version_number: int = 0) -> str:
    unhashed_key = password + username + "@" + domain + str(version_number)
    key_bytes = unhashed_key.encode('UTF-8')
    hashed_key = sha256(key_bytes).hexdigest()
    return hashed_key

def register_new_user(UID:int):
    username = str(input("Please enter your username: "))
    password = str(input("Please enter your password: "))
    domain = str(input("Please enter the current domain: "))
    key = generate_secret_key(username, password, domain)
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO users VALUES ('{UID}', '{key}')""")
    con.close()

def clear_tgs_cache(time:str):
    last_recorded_clear = time
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute("DELETE FROM tgs_cache")
    con.close()
    return last_recorded_clear
