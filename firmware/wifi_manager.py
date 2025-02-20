import network
import socket
import json
import time
import machine
import gc

class WifiManager:
    def __init__(self, ssid='JD-ISOBus-Config', password='12345678'):
        self.ap_ssid = ssid
        self.ap_password = password
        self.ap = network.WLAN(network.AP_IF)
        self.sta = network.WLAN(network.STA_IF)
        self.web_server = None
        self.config_file = 'wifi_config.json'
        self.html_config = {
            'title': 'WiFi Manager',
            'custom_html': '',
            'success_message': 'Conectado com sucesso!'
        }
    
    def config(self, **kwargs):
        """Configura o WiFi Manager"""
        for key, value in kwargs.items():
            if key in self.html_config:
                self.html_config[key] = value
    
    def create_ap(self):
        """Cria um Access Point"""
        print("\nCriando Access Point...")
        try:
            self.ap.active(False)
            time.sleep(1)
            self.ap.active(True)
            
            self.ap.config(
                essid=self.ap_ssid,
                password=self.ap_password,
                authmode=network.AUTH_WPA_WPA2_PSK,
                max_clients=1
            )
            
            for _ in range(10):
                if self.ap.active():
                    print(f"AP criado: {self.ap_ssid}")
                    print(f"IP: {self.ap.ifconfig()[0]}")
                    return True
                time.sleep(1)
            
            return False
            
        except Exception as e:
            print(f"Erro ao criar AP: {str(e)}")
            return False
    
    def scan_networks(self):
        """Escaneia redes WiFi disponíveis"""
        try:
            self.sta.active(True)
            networks = self.sta.scan()
            return [net[0].decode('utf-8') for net in networks]
        except:
            return []
    
    def create_web_server(self):
        """Cria o servidor web"""
        try:
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            self.web_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.web_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.web_server.bind(addr)
            self.web_server.listen(1)
            print("Servidor web iniciado na porta 80")
            return True
        except Exception as e:
            print(f"Erro ao criar servidor web: {str(e)}")
            return False
    
    def generate_html(self):
        """Gera o HTML da página de configuração"""
        networks = self.scan_networks()
        network_list = "".join([
            f'<button onclick="selectNetwork(\'{net}\')" class="btn">{net}</button><br>'
            for net in networks
        ])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.html_config['title']}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial; margin: 20px; background-color: #f0f0f0; }}
                .container {{ max-width: 400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .btn {{ background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; width: 100%; margin: 5px 0; border-radius: 5px; }}
                .input {{ width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
                h2 {{ color: #333; text-align: center; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .success {{ background-color: #dff0d8; color: #3c763d; }}
                .error {{ background-color: #f2dede; color: #a94442; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>{self.html_config['title']}</h2>
                {self.html_config['custom_html']}
                <div id="networks">
                    <h3>Redes disponíveis:</h3>
                    {network_list}
                </div>
                <div id="password-form" style="display:none;">
                    <h3>Digite a senha para <span id="selected-network"></span></h3>
                    <input type="password" id="password" class="input">
                    <button onclick="submitPassword()" class="btn">Conectar</button>
                </div>
            </div>
            <script>
                function selectNetwork(ssid) {{
                    document.getElementById('selected-network').textContent = ssid;
                    document.getElementById('password-form').style.display = 'block';
                    window.selectedNetwork = ssid;
                }}
                
                function submitPassword() {{
                    var password = document.getElementById('password').value;
                    var data = {{
                        ssid: window.selectedNetwork,
                        password: password
                    }};
                    
                    fetch('/connect', {{
                        method: 'POST',
                        body: JSON.stringify(data)
                    }})
                    .then(response => {{
                        if(response.ok) {{
                            document.getElementById('status').textContent = '{self.html_config["success_message"]}';
                            setTimeout(() => {{
                                window.location.reload();
                            }}, 5000);
                        }} else {{
                            throw new Error('Falha na conexão');
                        }}
                    }})
                    .catch(error => {{
                        document.getElementById('status').className = 'status error';
                        document.getElementById('status').textContent = 'Erro: ' + error.message;
                    }});
                }}
            </script>
        </body>
        </html>
        """
    
    def handle_request(self, client):
        """Manipula requisições web"""
        try:
            request = client.recv(1024).decode()
            
            if not request:
                return
            
            try:
                method = request.split()[0]
                path = request.split()[1]
            except:
                return
            
            if method == 'POST' and path == '/connect':
                # Processa dados de conexão
                content_length = int(request.split('Content-Length: ')[1].split('\r\n')[0])
                body = request.split('\r\n\r\n')[1][:content_length]
                data = json.loads(body)
                
                # Salva configuração
                with open(self.config_file, 'w') as f:
                    json.dump(data, f)
                
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nOK"
                client.send(response.encode())
                
                # Agenda reinicialização
                time.sleep(2)
                machine.reset()
            else:
                # Serve página principal
                html = self.generate_html()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
                client.send(response.encode())
                
        except Exception as e:
            print(f"Erro ao manipular requisição: {str(e)}")
        finally:
            client.close()
    
    def load_saved_config(self):
        """Carrega configuração WiFi salva"""
        try:
            with open(self.config_file) as f:
                return json.load(f)
        except:
            return None
    
    def connect_wifi(self, ssid, password):
        """Conecta a uma rede WiFi"""
        print(f"Conectando à rede {ssid}...")
        
        try:
            self.sta.active(True)
            self.sta.connect(ssid, password)
            
            for _ in range(20):
                if self.sta.isconnected():
                    print(f"Conectado à rede {ssid}")
                    print(f"IP: {self.sta.ifconfig()[0]}")
                    return True
                time.sleep(1)
            
            return False
            
        except Exception as e:
            print(f"Erro ao conectar: {str(e)}")
            return False
    
    def start(self):
        """Inicia o WiFi Manager"""
        # Tenta carregar configuração salva
        config = self.load_saved_config()
        if config:
            if self.connect_wifi(config['ssid'], config['password']):
                return True
        
        # Se não conseguiu conectar, cria AP
        if not self.create_ap():
            return False
        
        # Inicia servidor web
        if not self.create_web_server():
            return False
        
        # Loop principal
        while True:
            try:
                client, addr = self.web_server.accept()
                self.handle_request(client)
            except socket.timeout:
                gc.collect()
                continue
            except Exception as e:
                print(f"Erro no loop principal: {str(e)}")
                continue 