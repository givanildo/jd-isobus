import machine
from machine import Pin, SPI
import network
import time

# Configurações do MCP2515
CS_PIN = 5  # GPIO5 para Chip Select
spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
cs = Pin(CS_PIN, Pin.OUT)

# Verifica conexão WiFi
sta_if = network.WLAN(network.STA_IF)
if sta_if.isconnected():
    print('Conectado ao WiFi')
    print('IP:', sta_if.ifconfig()[0])
else:
    print('Modo AP ativo')
    ap_if = network.WLAN(network.AP_IF)
    print('IP:', ap_if.ifconfig()[0]) 