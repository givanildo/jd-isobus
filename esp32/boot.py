# boot.py - Configuração inicial do ESP32
import network
import json
import machine
import time
import wifimgr
import usocket as socket
import gc
import wifi_config

# Configurações do Access Point
AP_SSID = "JD-ISOBUS-Config"
AP_PASSWORD = "12345678"
AP_AUTHMODE = 3  # WPA2

# Configurações do cliente WiFi
WIFI_FILE = 'wifi_config.json'

class WiFiManager:
    def __init__(self, ssid="JD-ISOBUS", password="12345678"):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.ap_ssid = ssid
        self.ap_password = password
        
    def connect_to_saved_wifi(self):
        try:
            with open(WIFI_FILE, 'r') as f:
                config = json.load(f)
                return self.connect_to_wifi(config['ssid'], config['password'])
        except:
            return False
            
    def connect_to_wifi(self, ssid, password):
        print(f'Conectando a {ssid}...')
        self.wlan_sta.connect(ssid, password)
        for _ in range(20):  # 10 segundos timeout
            if self.wlan_sta.isconnected():
                print('Conectado!')
                print('IP:', self.wlan_sta.ifconfig()[0])
                return True
            time.sleep(0.5)
        print('Falha ao conectar')
        return False
        
    def start_ap(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=self.ap_ssid, 
                          password=self.ap_password,
                          authmode=network.AUTH_WPA_WPA2_PSK)
        print('Access Point ativo')
        print('SSID:', self.ap_ssid)
        print('IP:', self.wlan_ap.ifconfig()[0])

# Inicializa o WiFi
wifi = WiFiManager()

# Tenta conectar ao WiFi salvo
if not wifi.connect_to_saved_wifi():
    # Se falhar, inicia o AP
    wifi.start_ap()

# Ativa o WiFi
wlan = wifimgr.get_connection()

# Aguarda conexão
if wlan is not None:
    print("ESP32 WiFi conectado!")
    print(wlan.ifconfig())

gc.collect()

ssid = 'JD-ISOBUS'
password = '12345678'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())

def web_page():
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body><h1>JD-ISOBUS WiFi Manager</h1>
    <form action="/connect">
        <p><input type="text" name="ssid" placeholder="SSID"></p>
        <p><input type="password" name="password" placeholder="Password"></p>
        <p><input type="submit" value="Connect"></p>
    </form></body></html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)
        
        ssid_start = request.find('ssid=')
        ssid_end = request.find('&', ssid_start)
        password_start = request.find('password=')
        password_end = request.find('&', password_start)
        
        if ssid_start > 0:
            ssid = request[ssid_start+5:ssid_end]
            password = request[password_start+9:password_end]
            
            sta = network.WLAN(network.STA_IF)
            sta.active(True)
            sta.connect(ssid, password)
            
            response = "Connecting to " + ssid
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.send(response)
        else:
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.send(web_page())
            
        conn.close()
    except Exception as e:
        print(e)
        conn.close()

# Inicia o AP
wifi_config.start_ap() 