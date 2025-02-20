import machine
from machine import Pin, SPI
import network
import socket
import json
from time import sleep
import gc

# Configurações do MCP2515
CAN_SPEED = 250000  # 250 kbps
CS_PIN = 5  # GPIO5 para Chip Select

# Configuração do servidor web
WEB_PORT = 80

# Configuração do SPI
spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
cs = Pin(CS_PIN, Pin.OUT)
cs.value(1)  # CS inativo

class MCP2515:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.init_can()
    
    def init_can(self):
        """Inicializa o controlador CAN"""
        # Implementar inicialização do MCP2515
        pass
    
    def read_message(self):
        """Lê uma mensagem do barramento CAN"""
        # Implementar leitura de mensagens
        pass

class WebServer:
    def __init__(self, port=80):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(5)
        print(f'Servidor web iniciado na porta {port}')
    
    def handle_request(self, client):
        try:
            request = client.recv(1024).decode()
            method = request.split()[0]
            path = request.split()[1]
            
            if method == 'GET':
                if path == '/status':
                    response = {'status': 'online', 'ip': network.WLAN(network.STA_IF).ifconfig()[0]}
                    self.send_json_response(client, response)
                elif path == '/data':
                    # Implementar leitura de dados CAN
                    response = {'data': []}
                    self.send_json_response(client, response)
                else:
                    self.send_404(client)
            else:
                self.send_404(client)
        except Exception as e:
            print('Erro ao processar requisição:', e)
        finally:
            client.close()
    
    def send_json_response(self, client, data):
        response = json.dumps(data)
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: application/json\r\n')
        client.send('Access-Control-Allow-Origin: *\r\n')
        client.send(f'Content-Length: {len(response)}\r\n')
        client.send('\r\n')
        client.send(response)
    
    def send_404(self, client):
        response = 'Not Found'
        client.send('HTTP/1.1 404 Not Found\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send(f'Content-Length: {len(response)}\r\n')
        client.send('\r\n')
        client.send(response)
    
    def run(self):
        while True:
            try:
                client, addr = self.sock.accept()
                print('Cliente conectado de:', addr)
                self.handle_request(client)
            except Exception as e:
                print('Erro no servidor:', e)
            gc.collect()  # Coleta de lixo

def main():
    # Inicializa o controlador CAN
    can = MCP2515(spi, cs)
    
    # Inicia o servidor web
    server = WebServer(WEB_PORT)
    
    print('Sistema iniciado')
    server.run()

if __name__ == '__main__':
    main() 