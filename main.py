import socket
import struct
import random
import string
import requests
import time
import threading

# some default values you can touch

server_name = "MCNova [default name]"
server_motd = "Welcome to my server!"
server_port = 25565
server_ip = "192.168.100.55" # change this to your local ip


# do not touch this
server_running = False
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

def setupserver():
 listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 listener.bind((server_ip, server_port))
 listener.listen()
 clients = []

 server_running = True
 continuesetup(listener)

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
def receive_cp(v):
    if v == "info":
     info_packet = receive_bytes(client, 130)
     if info_packet == 0x00:
      version, name, mppass, _ = struct.unpack("!B64s64sB", info_packet)
      name, mppass = decode_string(name), decode_string(mppass)
    else:
     print("Error in receiving packets")
def send_cp(v, client):
    if v == "info":
         client.send(struct.pack("!BB64s64sB", 0x00, 7, encode_string(server_name), encode_string(server_motd), 0))
         client.send(b"\x02")
def handle_connect(self, client, client_addr):
    print(f"New Connection from {client_addr}")
    self.player_count += 1
    receive_cp(info)
    send_cp(info, client)
    name, mppass = receive_cp()
    print(f"{name} connected to server!")
    self.clients.append(client_socket)
    
    
 
def checkheartbeat():
    send_heartbeat()
    time.sleep(30) # Wait for 30 seconds 
def continuesetup(listener):
 client, client_address = listener.accept()
 print("Client Connected")
 client.send(struct.pack("!BB64s64sB", 0x00, 7, encode_string(server_name), encode_string(server_motd), 0))
 client.send(b"\x02")



def breakserver():
 heartbeat_thread.stop()
 listener.close()
 while server_running is not True:
     break
    
def shutdown(client, time):
 client.send(struct.pack("!BB64s", 0x0d, 255, encode_string("&eServer will shutdown in" + time)))
 # TODO: make it count to time then shutdown
 client.send(struct.pack("!B64s", 0x0e, encode_string("Server is shutdown")))
 server_running = False
 breakserver()

def main():
    heartbeat_thread = threading.Thread(target=checkheartbeat)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()
    
    try:
        while True:
                client_socket, client_address = listener.server_socket.accept()
                # Start a new thread to handle the client
                threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
            print("Server is shutting down...")
    finally:
            breakserver()




if __name__ == "__main__":
    server = Server(server_ip, server_port)  # Server running on localhost, port 12345
    server.start()
