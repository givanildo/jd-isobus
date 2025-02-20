import network
import socket
import ure
import time
import machine

ap_ssid = "JD-ISOBUS"
ap_password = "12345678"
ap_authmode = 3  # WPA2

NETWORK_PROFILES = 'wifi.dat'

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

def parse_post_data(request):
    try:
        # Encontra o corpo da requisição POST
        body = request.split('\r\n\r\n')[1]
        params = {}
        # Divide os parâmetros
        for param in body.split('&'):
            if '=' in param:
                key, value = param.split('=')
                # Decodifica os caracteres especiais
                value = value.replace('+', ' ')
                value = value.replace('%21', '!')
                value = value.replace('%23', '#')
                value = value.replace('%24', '$')
                value = value.replace('%25', '%')
                value = value.replace('%26', '&')
                value = value.replace('%27', "'")
                value = value.replace('%28', '(')
                value = value.replace('%29', ')')
                value = value.replace('%2A', '*')
                value = value.replace('%2B', '+')
                value = value.replace('%2C', ',')
                value = value.replace('%2F', '/')
                value = value.replace('%3A', ':')
                value = value.replace('%3B', ';')
                value = value.replace('%3D', '=')
                value = value.replace('%3F', '?')
                value = value.replace('%40', '@')
                value = value.replace('%5B', '[')
                value = value.replace('%5D', ']')
                params[key] = value
        return params
    except Exception as e:
        print('Erro ao parsear dados POST:', e)
        return None

def get_connection():
    """return a working WLAN(STA_IF) instance or None"""

    # First check if there already is any connection:
    if wlan_sta.isconnected():
        return wlan_sta

    connected = False
    try:
        # Read known network profiles from file
        with open(NETWORK_PROFILES, 'r') as f:
            for line in f:
                ssid, password = line.strip("\n").split(";")
                wlan_sta.active(True)
                wlan_sta.connect(ssid, password)
                print(f'Tentando conectar a {ssid}...')
                
                # Try to connect to WiFi for 10 seconds
                for _ in range(20):
                    if wlan_sta.isconnected():
                        connected = True
                        print('Conectado com sucesso!')
                        print('IP:', wlan_sta.ifconfig()[0])
                        break
                    time.sleep(0.5)
                if connected:
                    break
    except OSError:
        pass

    if connected:
        return wlan_sta

    # Start web server in AP mode
    wlan_sta.active(False)
    wlan_ap.active(True)
    wlan_ap.config(essid=ap_ssid, password=ap_password, authmode=ap_authmode)

    server_socket = socket.socket()
    server_socket.bind(('', 80))
    server_socket.listen(1)

    print('Access Point ativo')
    print('SSID:', ap_ssid)
    print('Senha:', ap_password)
    print('IP:', wlan_ap.ifconfig()[0])
    
    while True:
        conn, addr = server_socket.accept()
        print('Conexão recebida de:', addr)
        
        try:
            # Lê a requisição
            request = conn.recv(1024).decode()
            print('Requisição recebida:', request)
            
            # Verifica se é POST
            if request.startswith('POST'):
                params = parse_post_data(request)
                if params and 'ssid' in params and 'password' in params:
                    ssid = params['ssid']
                    password = params['password']
                    
                    print(f'Dados recebidos - SSID: {ssid}, Senha: {"*" * len(password)}')
                    
                    # Salva as configurações
                    with open(NETWORK_PROFILES, "w") as f:
                        f.write(f"{ssid};{password}")
                    
                    # Envia resposta
                    response = f"""
                    <html>
                        <head>
                            <title>Conectando...</title>
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <style>
                                body {{ font-family: Arial; text-align: center; margin-top: 50px; }}
                            </style>
                        </head>
                        <body>
                            <h2>Configurações salvas!</h2>
                            <p>Tentando conectar a: {ssid}</p>
                            <p>O dispositivo será reiniciado em 3 segundos...</p>
                        </body>
                    </html>
                    """
                    
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.send(response)
                    conn.close()
                    
                    print('Desativando AP...')
                    wlan_ap.active(False)
                    
                    print('Ativando modo Station...')
                    wlan_sta.active(True)
                    
                    print(f'Tentando conectar a {ssid}...')
                    wlan_sta.connect(ssid, password)
                    
                    # Aguarda conexão
                    for _ in range(20):
                        if wlan_sta.isconnected():
                            print('Conectado com sucesso!')
                            print('IP:', wlan_sta.ifconfig()[0])
                            time.sleep(3)
                            print('Reiniciando...')
                            machine.reset()
                        time.sleep(0.5)
                    
                    print('Falha ao conectar. Reiniciando...')
                    time.sleep(3)
                    machine.reset()
            else:
                # Página inicial
                response = """
                    <html>
                        <head>
                            <title>JD-ISOBUS WiFi</title>
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            <style>
                                body { font-family: Arial; margin: 20px; }
                                .container { max-width: 400px; margin: auto; }
                                input { width: 100%; padding: 10px; margin: 10px 0; }
                                .btn { background-color: #4CAF50; color: white; padding: 10px; border: none; width: 100%; cursor: pointer; }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Configuração WiFi</h1>
                                <form action="/connect" method="post">
                                    <input type="text" name="ssid" placeholder="Nome da rede WiFi" required>
                                    <input type="password" name="password" placeholder="Senha" required>
                                    <input type="submit" value="Conectar" class="btn">
                                </form>
                            </div>
                        </body>
                    </html>
                """
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.send(response)
                conn.close()

        except Exception as e:
            print('Erro:', e)
            conn.close() 