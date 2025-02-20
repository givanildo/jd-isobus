from pysobus.parser import Parser
import json

class CANParser:
    def __init__(self):
        self.parser = Parser()
        self.message_cache = {}
    
    def parse_message(self, message_hex):
        """
        Parseia uma mensagem CAN no formato hexadecimal
        Args:
            message_hex (str): Mensagem CAN em formato hexadecimal
        Returns:
            dict: Mensagem parseada com informações do protocolo J1939
        """
        try:
            result = self.parser.parse_message(message_hex)
            if result:
                # Adicionar ao cache
                pgn = result.get('pgn')
                if pgn:
                    self.message_cache[pgn] = result
                return result
        except Exception as e:
            print(f"Erro ao parsear mensagem: {e}")
        return None
    
    def get_cached_messages(self):
        """
        Retorna todas as mensagens em cache
        Returns:
            dict: Dicionário com todas as mensagens cacheadas
        """
        return self.message_cache
    
    def clear_cache(self):
        """Limpa o cache de mensagens"""
        self.message_cache.clear()
    
    def get_message_by_pgn(self, pgn):
        """
        Retorna uma mensagem específica do cache pelo PGN
        Args:
            pgn (int): Parameter Group Number
        Returns:
            dict: Mensagem parseada ou None se não encontrada
        """
        return self.message_cache.get(pgn)
    
    def format_message(self, message):
        """
        Formata uma mensagem para exibição
        Args:
            message (dict): Mensagem parseada
        Returns:
            dict: Mensagem formatada para exibição
        """
        if not message:
            return None
        
        formatted = {
            'pgn': message.get('pgn'),
            'timestamp': message.get('info', {}).get('timestamp'),
            'source': message.get('info', {}).get('source'),
            'values': {}
        }
        
        # Adicionar valores específicos do SPN
        spn_vals = message.get('spn_vals', {})
        for key, value in spn_vals.items():
            formatted['values'][key] = {
                'value': value,
                'unit': self._get_unit_for_spn(key)
            }
        
        return formatted
    
    def _get_unit_for_spn(self, spn_name):
        """
        Retorna a unidade para um SPN específico
        Args:
            spn_name (str): Nome do SPN
        Returns:
            str: Unidade do SPN ou string vazia
        """
        # Mapeamento de unidades comuns
        unit_map = {
            'Engine_Speed': 'rpm',
            'Wheel_Based_Vehicle_Speed': 'km/h',
            'Engine_Percent_Load_At_Current_Speed': '%',
            'Fuel_Level': '%',
            'Engine_Oil_Pressure': 'kPa',
            'Engine_Coolant_Temperature': '°C',
            'Battery_Potential_Voltage': 'V',
            'Latitude': '°',
            'Longitude': '°',
            'Altitude': 'm',
            'Navigation_Based_Vehicle_Speed': 'km/h',
            'Pitch': '°',
            'Roll': '°',
            'Yaw_Rate': '°/s'
        }
        return unit_map.get(spn_name, '') 