import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):
        self.data_buffer = {}
        self.buffer_size = 1000  # Tamanho máximo do buffer por PGN
    
    def add_data(self, pgn, timestamp, values):
        """
        Adiciona dados ao buffer
        Args:
            pgn (int): Parameter Group Number
            timestamp (float): Timestamp do dado
            values (dict): Valores dos SPNs
        """
        if pgn not in self.data_buffer:
            self.data_buffer[pgn] = {
                'timestamp': [],
                'values': {}
            }
            for key in values.keys():
                self.data_buffer[pgn]['values'][key] = []
        
        # Adicionar timestamp
        self.data_buffer[pgn]['timestamp'].append(timestamp)
        
        # Adicionar valores
        for key, value in values.items():
            if key not in self.data_buffer[pgn]['values']:
                self.data_buffer[pgn]['values'][key] = []
            self.data_buffer[pgn]['values'][key].append(value)
        
        # Limitar tamanho do buffer
        if len(self.data_buffer[pgn]['timestamp']) > self.buffer_size:
            self.data_buffer[pgn]['timestamp'] = self.data_buffer[pgn]['timestamp'][-self.buffer_size:]
            for key in self.data_buffer[pgn]['values'].keys():
                self.data_buffer[pgn]['values'][key] = self.data_buffer[pgn]['values'][key][-self.buffer_size:]
    
    def get_data_frame(self, pgn, spn=None, time_range=None):
        """
        Retorna um DataFrame com os dados do buffer
        Args:
            pgn (int): Parameter Group Number
            spn (str, optional): Nome do SPN específico
            time_range (tuple, optional): (início, fim) para filtrar dados
        Returns:
            pd.DataFrame: DataFrame com os dados
        """
        if pgn not in self.data_buffer:
            return pd.DataFrame()
        
        data = {
            'timestamp': self.data_buffer[pgn]['timestamp']
        }
        
        if spn:
            if spn in self.data_buffer[pgn]['values']:
                data[spn] = self.data_buffer[pgn]['values'][spn]
        else:
            for key, values in self.data_buffer[pgn]['values'].items():
                data[key] = values
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        
        if time_range:
            start, end = time_range
            df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
        
        return df
    
    def get_latest_value(self, pgn, spn):
        """
        Retorna o valor mais recente para um PGN e SPN específicos
        Args:
            pgn (int): Parameter Group Number
            spn (str): Nome do SPN
        Returns:
            float: Valor mais recente ou None se não disponível
        """
        if pgn in self.data_buffer and spn in self.data_buffer[pgn]['values']:
            values = self.data_buffer[pgn]['values'][spn]
            if values:
                return values[-1]
        return None
    
    def get_statistics(self, pgn, spn, window=60):
        """
        Calcula estatísticas para um PGN e SPN específicos
        Args:
            pgn (int): Parameter Group Number
            spn (str): Nome do SPN
            window (int): Janela de tempo em segundos
        Returns:
            dict: Estatísticas calculadas
        """
        df = self.get_data_frame(pgn, spn)
        if df.empty:
            return {
                'min': None,
                'max': None,
                'mean': None,
                'std': None
            }
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        df = df[df['timestamp'] >= window_start]
        
        if df.empty:
            return {
                'min': None,
                'max': None,
                'mean': None,
                'std': None
            }
        
        values = df[spn].values
        return {
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'std': float(np.std(values))
        }
    
    def clear_buffer(self):
        """Limpa o buffer de dados"""
        self.data_buffer.clear() 