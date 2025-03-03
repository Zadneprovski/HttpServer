import socket
import threading
import os

HOST = "localhost"
PORT = 8080
DOCUMENT_ROOT = "./www"


def handle_request(client_socket):
    try:
        request = client_socket.recv(1024).decode("utf-8")
        if not request:
            return

        lines = request.split("\r\n")
        request_line = lines[0].split()

        if len(request_line) < 2:
            return

        method, path = request_line[0], request_line[1]
        file_path = os.path.join(DOCUMENT_ROOT, path.lstrip("/"))

        if method not in ["GET", "HEAD"]:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            client_socket.sendall(response.encode("utf-8"))
            return

        if not os.path.isfile(file_path):
            response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
            client_socket.sendall(response.encode("utf-8"))
            return

        with open(file_path, "rb") as file:
            content = file.read()
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Length: {}\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
            ).format(len(content))
            client_socket.sendall(response_headers.encode("utf-8"))
            if method == "GET":
                client_socket.sendall(content)

    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_request, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    start_server()
