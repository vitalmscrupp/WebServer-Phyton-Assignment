import socket
import time
import sys

class WebSever(object):

    def __init__(self, port:5432):
        self.host = '127.0.0.1'
        self.port = port
        self.directory = 'web'

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("[STARTING SERVER]: {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
        except Exception as e:
            print("Could not bind to port {port}".format(port=self.port))
            self.shutdown()
            self.exit(1)

        self._listen()

    def shutdown(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            sys.exit(1)
        except Exception as e:
            pass

    def _listen(self):
        self.socket.listen(3)
        while True:
            (conn, address) = self.socket.accept()
            print("[RECEIVED CONNECTION]: {addr}".format(addr=address))
            data = conn.recv(2048)
            self._send_response(bytes.decode(data), conn)


    def _generate_header(self, respose_code):
        header_server = 'Sever: Python-Socket-TCP'
        header_connection_close = 'Connection: close\n\n'

        if respose_code == 200:
            header = 'HTTP/1.1 200 OK\n'
        elif respose_code == 404:
            header = 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b &Y %H:%M:%S", time.localtime())
        header += 'Date {now}\n'.format(now=time_now)
        header += header_server
        header += header_connection_close
        return header


    def _send_response(self, string, conn):
        request_method = string.split(' ')[0]
        print("================================")
        print("[REQUEST BODY]:\n\t", string.replace('\n', '\n\t'))
        print("================================")

        if request_method == 'GET':
            file_request = string.split(' ')[1].split('?')[0]
            if (file_request == "/"):
                file_request = '/index.html'

            file_request = self.directory + file_request

            try:
                file_handler = open(file_request, 'rb')
                response_content = file_handler.read()
                file_handler.close()
                response_headers = self._generate_header(200)
            except Exception as e:
                response_headers = self._generate_header(404)
                response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

            data = response_headers.encode() + response_content
            conn.send(data)
            conn.close()
        else:
            print("Unknown HTTP request method", request_method)
            self.shutdown()


server = WebSever(5432)
server.start()