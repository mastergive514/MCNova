import socket
import struct
import random
import string
import requests
import time

# some default values you can touch

server_name = "MCNova [default name]"
server_motd = "Welcome to my server!"
server_port = 25565
server_ip = "192.168.100.55" # change this to your local ip
# do not touch this
def encode_string(s):
    # checks if the string isnt too long
    if len(s) > 64:
        raise ValueError("String too long (got %d, max 64)" % len(s))

    # pads the string to 64 characters
    s = "%.64s" % s

    return s.encode("cp437")

# decodes a string from the minecraft classic protocol string format
def decode_string(s):
    # checks if the string isnt too long
    if len(s) != 64:
        raise ValueError("String must be 64 bytes (got %d)" % len(s))
    
    # decodes the string
    s = s.decode("cp437")

    # removes the padding and returns the string
    return s.strip()
def receive_bytes(s, number):
    # data is what is gonna be returned
    # the b before the string indicates that its bytes
    data = b""

    while len(data) < number:
        data += s.recv(number-len(data))

    return data
    
message = ""
    
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((server_ip, server_port))
listener.listen()

def generate_salt(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to send the heartbeat
def send_heartbeat():
    url = "https://classicube.net/server/heartbeat/"
    salt = generate_salt()  # Generate a random salt
    params = {
        "name": server_name,   # Replace with your server name
        "port": server_port,              # Replace with your server's port
        "users": 0,                # Replace with the current number of players
        "max": 20,                  # Replace with the maximum number of players
        "public": "true",           # Set to "true" to make the server public
        "salt": salt,               # Generated salt
        "software": "MCNova 0.1b",  # Optional, replace with your software name
        "web": "false"               # Set to "true" if your server supports the web client
    }

    response = requests.get(url, params=params)
    body = response.text
    if "/play/" in body:
        print(f"Server URL: {body}")

    else:
        print(f"Failed to send heartbeat. Status code: {response.status_code}")
        print(f"{body}")
while True:
 send_heartbeat()
 time.sleep(30)
client, client_address = listener.accept()
print("Client Connected")
client.send(struct.pack("!BB64s64sB", 0x00, 7, encode_string(server_name), encode_string(server_motd), 0))
client.send(b"\x02")

first_packet = receive_bytes(client, 1)
if first_packet[0] == 0x00:
    first_packet += receive_bytes(client, 129)
    version, name, mppass, _ = struct.unpack("!B64s64sB", first_packet)
    name = decode_string(name)
    mppass = decode_string(mppass)

if first_packet[0] == 0x0d:
   first_packet += receive_bytes(client, 65)
   player_id, message = struct.unpack("!B64s", first_packet)
   message = decode_string(message)
   print(message)

client.send(struct.pack("!BB64s", 0x0d, 255, encode_string("&eServer will shutdown soon")))
time.sleep(2)
client.send(struct.pack("!B64s", 0x0e, encode_string("Server is shutdowning")))
listener.close()
