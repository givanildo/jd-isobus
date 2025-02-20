from machine import Pin, SPI
import time

# Registradores do MCP2515
MCP_RESET = 0xC0
MCP_READ = 0x03
MCP_WRITE = 0x02
MCP_RTS = 0x80
MCP_READ_STATUS = 0xA0
MCP_RX_STATUS = 0xB0
MCP_BIT_MODIFY = 0x05

# Registradores de configuração
CNF1 = 0x2A
CNF2 = 0x29
CNF3 = 0x28
CANINTE = 0x2B
CANINTF = 0x2C
TXB0CTRL = 0x30
RXB0CTRL = 0x60
RXB0SIDH = 0x61

class MCP2515:
    def __init__(self, spi, cs_pin, speed=250000):
        self.spi = spi
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)  # CS inativo
        self.speed = speed
        self.init_can()
    
    def _cs_low(self):
        """Ativa o chip select"""
        self.cs.value(0)
    
    def _cs_high(self):
        """Desativa o chip select"""
        self.cs.value(1)
    
    def _spi_read(self, addr):
        """Lê um byte do endereço especificado"""
        self._cs_low()
        self.spi.write(bytes([MCP_READ, addr]))
        result = self.spi.read(1)[0]
        self._cs_high()
        return result
    
    def _spi_write(self, addr, data):
        """Escreve um byte no endereço especificado"""
        self._cs_low()
        self.spi.write(bytes([MCP_WRITE, addr, data]))
        self._cs_high()
    
    def _spi_bit_modify(self, addr, mask, data):
        """Modifica bits específicos no endereço"""
        self._cs_low()
        self.spi.write(bytes([MCP_BIT_MODIFY, addr, mask, data]))
        self._cs_high()
    
    def reset(self):
        """Reseta o controlador MCP2515"""
        self._cs_low()
        self.spi.write(bytes([MCP_RESET]))
        self._cs_high()
        time.sleep_ms(10)
    
    def init_can(self):
        """Inicializa o controlador CAN"""
        self.reset()
        
        # Configurar modo de configuração
        self._spi_write(0x0F, 0x80)
        time.sleep_ms(10)
        
        # Configurar velocidade (250kbps com clock de 8MHz)
        self._spi_write(CNF1, 0x00)
        self._spi_write(CNF2, 0x90)
        self._spi_write(CNF3, 0x02)
        
        # Habilitar interrupções
        self._spi_write(CANINTE, 0x01)
        
        # Configurar filtros e máscaras
        for i in range(0x20, 0x30):  # Limpar filtros
            self._spi_write(i, 0)
        
        # Configurar modo normal
        self._spi_write(0x0F, 0x00)
        time.sleep_ms(10)
    
    def read_message(self):
        """Lê uma mensagem do barramento CAN"""
        status = self._spi_read(CANINTF)
        
        if status & 0x01:  # Mensagem disponível no buffer 0
            # Ler ID
            sidh = self._spi_read(RXB0SIDH)
            sidl = self._spi_read(RXB0SIDH + 1)
            
            # Ler comprimento dos dados
            dlc = self._spi_read(RXB0SIDH + 4) & 0x0F
            
            # Ler dados
            data = []
            for i in range(dlc):
                data.append(self._spi_read(RXB0SIDH + 5 + i))
            
            # Limpar flag de interrupção
            self._spi_bit_modify(CANINTF, 0x01, 0x00)
            
            # Calcular ID completo
            id = (sidh << 3) | (sidl >> 5)
            
            return {
                'id': id,
                'dlc': dlc,
                'data': data
            }
        
        return None
    
    def send_message(self, id, data, dlc=None):
        """Envia uma mensagem pelo barramento CAN"""
        if dlc is None:
            dlc = len(data)
        
        # Esperar buffer de transmissão livre
        while self._spi_read(TXB0CTRL) & 0x08:
            time.sleep_ms(1)
        
        # Configurar ID
        self._spi_write(TXB0CTRL + 1, id >> 3)
        self._spi_write(TXB0CTRL + 2, (id << 5) & 0xE0)
        
        # Configurar DLC
        self._spi_write(TXB0CTRL + 5, dlc)
        
        # Escrever dados
        for i, byte in enumerate(data):
            if i >= dlc:
                break
            self._spi_write(TXB0CTRL + 6 + i, byte)
        
        # Solicitar envio
        self._cs_low()
        self.spi.write(bytes([MCP_RTS | 0x01]))  # RTS para buffer 0
        self._cs_high()
        
        return True 