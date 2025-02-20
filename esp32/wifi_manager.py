import network
import socket
import json
import machine
from time import sleep

class DNSServer:
    def __init__(self, ip):
        self.ip = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 53))
        self.sock.setblocking(False)
    
    def process_dns_query(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            # Resposta DNS simples redirecionando para o IP do ESP32
            response = (
                data[:2] +  # ID
                b'\x81\x80' +  # Flags
                data[4:6] +  # QDCOUNT
                data[4:6] +  # ANCOUNT
                b'\x00\x00' +  # NSCOUNT
                b'\x00\x00' +  # ARCOUNT
                data[12:] +  # Original query
                b'\xc0\x0c' +  # Pointer to domain name
                b'\x00\x01' +  # TYPE A
                b'\x00\x01' +  # CLASS IN
                b'\x00\x00\x00\x3c' +  # TTL (60 seconds)
                b'\x00\x04' +  # RDLENGTH (4 bytes)
                bytes(map(int, self.ip.split('.')))  # IP address
            )
            self.sock.sendto(response, addr)
        except:
            pass

class CaptivePortal:
    def __init__(self, ip):
        self.ip = ip
        self.html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JD-ISOBUS Config</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f0f0f0;
                }
                .container {
                    max-width: 400px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                .form-group {
                    margin-bottom: 15px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    color: #666;
                }
                input[type="text"],
                input[type="password"] {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                }
                button:hover {
                    background-color: #45a049;
                }
                #networks {
                    margin-bottom: 15px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>JD-ISOBUS Config</h1>
                <form action="/connect" method="post">
                    <div class="form-group">
                        <label for="networks">Redes Disponíveis:</label>
                        <select id="networks" name="ssid" style="width: 100%; padding: 8px;">
                            {{NETWORKS}}
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="password">Senha:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Conectar</button>
                </form>
            </div>
        </body>
        </html>
        """
        self.sock = socket.socket()
        self.sock.bind(('', 80))
        self.sock.listen(1)
        self.sock.setblocking(False)
    
    def get_networks(self):
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        networks = sta.scan()
        options = ''
        for net in sorted(networks, key=lambda x: x[3], reverse=True):
            ssid = net[0].decode('utf-8')
            rssi = net[3]
            options += f'<option value="{ssid}">{ssid} ({rssi}dB)</option>'
        return options
    
    def handle_request(self, client):
        try:
            request = client.recv(1024).decode()
            
            if 'POST /connect' in request:
                # Extrair SSID e senha do corpo da requisição
                body = request.split('\r\n\r\n')[1]
                params = {}
                for param in body.split('&'):
                    key, value = param.split('=')
                    params[key] = value.replace('+', ' ')
                
                # Salvar configurações e reiniciar
                with open('wifi_config.json', 'w') as f:
                    json.dump({
                        'ssid': params['ssid'],
                        'password': params['password']
                    }, f)
                
                response = """
                HTTP/1.1 200 OK
                Content-Type: text/html

                <html><body>
                <h1>Configuração Salva</h1>
                <p>O dispositivo será reiniciado e tentará conectar à rede WiFi.</p>
                </body></html>
                """
                client.send(response.encode())
                sleep(2)
                machine.reset()
            else:
                # Página principal
                networks = self.get_networks()
                html = self.html.replace('{{NETWORKS}}', networks)
                response = f"""
                HTTP/1.1 200 OK
                Content-Type: text/html

                {html}
                """
                client.send(response.encode())
        
        except Exception as e:
            print('Erro ao processar requisição:', e)
        finally:
            client.close()
    
    def handle_clients(self):
        try:
            client, addr = self.sock.accept()
            print('Cliente conectado de:', addr)
            self.handle_request(client)
        except:
            pass

class WiFiManager:
    def __init__(self):
        self.ap = network.WLAN(network.AP_IF)
        self.sta = network.WLAN(network.STA_IF)
    
    def start_ap(self, ssid, password):
        self.ap.active(True)
        self.ap.config(essid=ssid, password=password, authmode=3)  # WPA2
        print('Access Point ativo')
        print('SSID:', ssid)
        print('IP:', self.ap.ifconfig()[0])
        
        # Iniciar servidores DNS e Web
        dns_server = DNSServer(self.ap.ifconfig()[0])
        captive_portal = CaptivePortal(self.ap.ifconfig()[0])
        
        while True:
            dns_server.process_dns_query()
            captive_portal.handle_clients()
            sleep(0.01)
    
    def connect_wifi(self, ssid, password):
        self.sta.active(True)
        self.sta.connect(ssid, password)
        
        # Aguardar conexão
        for _ in range(20):
            if self.sta.isconnected():
                print('Conectado ao WiFi')
                print('IP:', self.sta.ifconfig()[0])
                return True
            sleep(0.5)
        
        print('Falha ao conectar ao WiFi')
        return False
    
    def load_config(self):
        try:
            with open('wifi_config.json', 'r') as f:
                return json.load(f)
        except:
            return None 