import socket

HOST = "172.20.10.2"
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(1)

print("NEXORA server is ready!")
print("Waiting for ESP32...")

try:
    connection, address = server.accept()

    with connection:
        print("ESP32 connected:", address)

        message = connection.recv(1024).decode().strip()
        print("Message from ESP32:", message)

        reply = "Laptop says: NEXORA communication successful!"
        connection.sendall((reply + "\n").encode())

        print("Reply sent:", reply)

finally:
    server.close()
