# boot.py - Configuração inicial do ESP32
import network
import json
import machine
from time import sleep

# Configurações do Access Point
AP_SSID = "JD-ISOBUS-Config"
AP_PASSWORD = "12345678"
AP_AUTHMODE = 3  # WPA2

# Configurações do cliente WiFi
WIFI_FILE = 'wifi_config.json'

def create_ap():
    """Cria um Access Point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=AP_AUTHMODE)
    while not ap.active():
        pass
    print('Access Point ativo')
    print('SSID:', AP_SSID)
    print('IP:', ap.ifconfig()[0])
    return ap

def load_wifi_config():
    """Carrega as configurações WiFi salvas"""
    try:
        with open(WIFI_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def save_wifi_config(ssid, password):
    """Salva as configurações WiFi"""
    with open(WIFI_FILE, 'w') as f:
        json.dump({'ssid': ssid, 'password': password}, f)

def connect_wifi(ssid, password):
    """Conecta a uma rede WiFi"""
    sta = network.WLAN(network.STA_IF)
    if not sta.isconnected():
        print('Conectando ao WiFi...')
        sta.active(True)
        sta.connect(ssid, password)
        for _ in range(20):  # Timeout de 10 segundos
            if sta.isconnected():
                break
            sleep(0.5)
    if sta.isconnected():
        print('Conectado ao WiFi')
        print('IP:', sta.ifconfig()[0])
        return True
    return False

# Verifica se há configurações WiFi salvas
wifi_config = load_wifi_config()

if wifi_config:
    # Tenta conectar com as configurações salvas
    if connect_wifi(wifi_config['ssid'], wifi_config['password']):
        print('Conexão WiFi estabelecida')
    else:
        # Se falhar, cria AP
        ap = create_ap()
else:
    # Se não há configurações, cria AP
    ap = create_ap() 