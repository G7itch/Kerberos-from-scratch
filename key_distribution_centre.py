#This is the server that combines the authentication-server script and the ticket-granting-server script
#KDC needs to be able to register a new user

import sqlite3
import authentication_server
import ticket_granting_server
from hashlib import sha256
import socket
from datetime import datetime
import string
import random

TGS_ID = "0000"
SECRET_KEY = "this_is_the_TGS_secret_key"

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

def search_DB(table:str, search_field: str, search_item: str, return_fields: tuple):
    """Search the database for an item"""
    con = sqlite3.connect("master.db")
    cur = con.cursor()

    if return_fields != str(return_fields):
        return_fields = str(str(return_fields)[1:-1])
    else:
        return_fields = str(return_fields)    
    
    return_fields = return_fields.replace("'", "")
    return_fields = return_fields.replace('"', "")

    command = f"SELECT {return_fields} FROM {table} WHERE {search_field} = '{search_item}'"

    res = cur.execute(command)
    res = res.fetchone()
    con.close()

    return res

def generate_secret_key(username: str, password:str, domain:str, version_number: int = 0) -> str:
    unhashed_key = password + username + "@" + domain + str(version_number)
    key_bytes = unhashed_key.encode('UTF-8')
    hashed_key = sha256(key_bytes).hexdigest()
    return hashed_key

def register_new_user(UID:str):
    username = str(input("Please enter your username: "))
    password = str(input("Please enter your password: "))
    domain = str(input("Please enter the current domain: "))
    key = generate_secret_key(username, password, domain)
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO users VALUES ('{UID}', '{key}')""")
    con.commit()
    con.close()

def register_new_service(UID:str,service_secret_key:str):
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO services VALUES ('{UID}', '{service_secret_key}')""")
    con.commit()
    con.close()

def clear_tgs_cache(time:str):
    last_recorded_clear = time
    con = sqlite3.connect("master.db")
    cur = con.cursor()
    cur.execute("DELETE FROM tgs_cache")
    con.commit()
    con.close()
    return last_recorded_clear

def repeat_to_length(string_to_expand, length):
    # Determine how many times the string should be repeated
    full_repeats, leftover_size = divmod(length, len(string_to_expand))
    # Repeat the string fully and then add the leftover part
    result_string = string_to_expand * full_repeats + string_to_expand[:leftover_size]
    return result_string

def xor_cipher(data, key):
    key = repeat_to_length(key,len(data))
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, key))

host = socket.gethostname() #because we are running the server locally
port = 5000
KDC_socket = socket.socket()
KDC_socket.bind((host,port))
KDC_socket.listen(10)
conn, address = KDC_socket.accept()
principal_ticket_1 = conn.recv(2048).decode('utf8')
KDC_socket.close()

#now the KDC needs to check if the UID exists in its database
user_id = principal_ticket_1.split("UID=")[1].split(",")[0].replace("'","")
TTL = principal_ticket_1.split("TTL=")[1].split(")")[0].replace("'","")
ip = principal_ticket_1.split("IP=")[1].split(")")[0].split("(")[1].replace("'","")

user_secret_key = search_DB("users","ID",user_id,("secret_key"))
if user_secret_key:
    pass
else:
    raise("What are you doing, you don't exist on this system") #should probably send something back to user here but this is a POC so dont care

user_secret_key = str(user_secret_key[0])
#we need to make two tickets here, the TGT and the  user auth ticket
TGS_SESSION_KEY = str(''.join(random.choices(string.ascii_letters,k=8)))
AS_ticket_1 = authentication_server.User_Auth_Ticket(TGS_ID, int(datetime.timestamp(datetime.now())),TTL,TGS_SESSION_KEY)

#This ticket needs to be encrypted with the users secret_key
ticket_bytes = str(AS_ticket_1)
AS_ticket_1 = xor_cipher(ticket_bytes,user_secret_key)

#set up the other ticket, the TGT. encrypted with TGS_secret key
AS_ticket_2 = authentication_server.TGT(user_id,TGS_ID, int(datetime.timestamp(datetime.now())),ip ,TTL,TGS_SESSION_KEY)
ticket_bytes = str(AS_ticket_1)
AS_ticket_2 = xor_cipher(ticket_bytes,SECRET_KEY)

#send these to user
KDC_socket = socket.socket()
KDC_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
KDC_socket.bind((host,port))
KDC_socket.listen(10)
conn, address = KDC_socket.accept()
print(conn,address)
KDC_socket.send(bytes(str(AS_ticket_1),encoding='utf8'))
KDC_socket.send(bytes(str(AS_ticket_2),encoding='utf8'))
KDC_socket.close()
