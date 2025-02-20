def do_connect(ssid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Conectando ao WiFi...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print('Configuração de rede:', sta_if.ifconfig())

def start_ap():
    import network
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid='JD-ISOBUS', password='12345678', authmode=3)
    print('AP ativo:', ap_if.ifconfig()) 