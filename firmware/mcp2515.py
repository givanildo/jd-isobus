"""
Driver MCP2515 para MicroPython
Adaptado para uso com ESP32 e protocolo J1939
"""

import time
from machine import Pin

# Registradores MCP2515
MCP_CANSTAT = 0x0E
MCP_CANCTRL = 0x0F
MCP_CNF3 = 0x28
MCP_CNF2 = 0x29
MCP_CNF1 = 0x2A
MCP_RXB0CTRL = 0x60
MCP_RXB1CTRL = 0x70
MCP_TXB0CTRL = 0x30
MCP_TXB1CTRL = 0x40
MCP_TXB2CTRL = 0x50

# Comandos SPI
RESET = 0xC0
READ = 0x03
WRITE = 0x02
READ_RX = 0x90
WRITE_TX = 0x40
RTS = 0x80
READ_STATUS = 0xA0
RX_STATUS = 0xB0
BIT_MODIFY = 0x05

# Modos de operação
MODE_NORMAL = 0x00
MODE_SLEEP = 0x20
MODE_LOOPBACK = 0x40
MODE_LISTENONLY = 0x60
MODE_CONFIG = 0x80

class CANMessage:
    """Classe para mensagens CAN"""
    def __init__(self, id=0, data=None, dlc=None, extended=True):
        self.id = id
        self.data = data if data else []
        self.dlc = dlc if dlc is not None else len(self.data)
        self.extended = extended

class MCP2515:
    """Driver para o controlador CAN MCP2515"""
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.extended = True
    
    def _cs_low(self):
        """Ativa o chip select"""
        self.cs.value(0)
    
    def _cs_high(self):
        """Desativa o chip select"""
        self.cs.value(1)
    
    def _spi_read(self, addr):
        """Lê um byte de um endereço"""
        self._cs_low()
        self.spi.write(bytes([READ, addr]))
        result = self.spi.read(1)[0]
        self._cs_high()
        return result
    
    def _spi_write(self, addr, data):
        """Escreve um byte em um endereço"""
        self._cs_low()
        self.spi.write(bytes([WRITE, addr, data]))
        self._cs_high()
    
    def _spi_read_bytes(self, cmd, length):
        """Lê múltiplos bytes"""
        self._cs_low()
        self.spi.write(bytes([cmd]))
        result = self.spi.read(length)
        self._cs_high()
        return result
    
    def _spi_write_bytes(self, cmd, data):
        """Escreve múltiplos bytes"""
        self._cs_low()
        self.spi.write(bytes([cmd]) + data)
        self._cs_high()
    
    def reset(self):
        """Reseta o controlador"""
        self._cs_low()
        self.spi.write(bytes([RESET]))
        self._cs_high()
        time.sleep_ms(10)
    
    def set_mode(self, mode):
        """Define o modo de operação"""
        self._spi_write(MCP_CANCTRL, mode)
        while (self._spi_read(MCP_CANSTAT) & 0xE0) != mode:
            time.sleep_ms(10)
    
    def set_bitrate(self, bitrate):
        """Configura o bitrate"""
        # Valores para cristal de 8MHz
        if bitrate == 250000:  # 250kbps
            cnf1 = 0x00
            cnf2 = 0x90
            cnf3 = 0x02
        else:
            raise ValueError("Bitrate não suportado")
        
        self.set_mode(MODE_CONFIG)
        self._spi_write(MCP_CNF1, cnf1)
        self._spi_write(MCP_CNF2, cnf2)
        self._spi_write(MCP_CNF3, cnf3)
    
    def set_normal_mode(self):
        """Coloca o controlador em modo normal"""
        self.set_mode(MODE_NORMAL)
    
    def is_rx_pending(self):
        """Verifica se há mensagens pendentes"""
        status = self._spi_read_bytes(READ_STATUS, 1)[0]
        return bool(status & 0x03)
    
    def recv(self):
        """Recebe uma mensagem"""
        status = self._spi_read_bytes(READ_STATUS, 1)[0]
        buf = 0 if status & 0x01 else 1 if status & 0x02 else -1
        
        if buf == -1:
            return None
        
        # Lê a mensagem do buffer
        self._cs_low()
        self.spi.write(bytes([READ_RX + (buf << 2)]))
        
        # Lê ID, DLC e dados
        data = self.spi.read(13)
        self._cs_high()
        
        # Processa ID
        id_h = data[0]
        id_l = data[1]
        id_ext_h = data[2]
        id_ext_l = data[3]
        
        if id_h & 0x08:  # Frame estendido
            id = ((id_h & 0x07) << 29) | (id_l << 21) | \
                 (id_ext_h << 13) | (id_ext_l << 5)
            extended = True
        else:  # Frame padrão
            id = (id_h << 3) | (id_l >> 5)
            extended = False
        
        # Processa DLC e dados
        dlc = data[4] & 0x0F
        msg_data = list(data[5:5+dlc])
        
        return CANMessage(id, msg_data, dlc, extended)
    
    def send(self, msg):
        """Envia uma mensagem"""
        # Encontra buffer livre
        status = self._spi_read_bytes(READ_STATUS, 1)[0]
        buf = 0 if not (status & 0x04) else \
              1 if not (status & 0x10) else \
              2 if not (status & 0x40) else -1
        
        if buf == -1:
            return False
        
        # Prepara ID
        if msg.extended:
            id_h = (msg.id >> 29) & 0x07
            id_h |= 0x08  # Define frame estendido
            id_l = (msg.id >> 21) & 0xFF
            id_ext_h = (msg.id >> 13) & 0xFF
            id_ext_l = (msg.id >> 5) & 0xFF
        else:
            id_h = (msg.id >> 3) & 0xFF
            id_l = (msg.id << 5) & 0xE0
            id_ext_h = 0
            id_ext_l = 0
        
        # Envia comando de escrita
        self._cs_low()
        self.spi.write(bytes([WRITE_TX + (buf << 1)]))
        self.spi.write(bytes([id_h, id_l, id_ext_h, id_ext_l]))
        
        # Envia DLC e dados
        self.spi.write(bytes([msg.dlc]))
        self.spi.write(bytes(msg.data))
        self._cs_high()
        
        # Inicia transmissão
        self._cs_low()
        self.spi.write(bytes([RTS + (1 << buf)]))
        self._cs_high()
        
        return True 