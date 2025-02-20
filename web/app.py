import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

# Configuração da página
st.set_page_config(
    page_title="JD-ISOBUS Monitor",
    page_icon="🚜",
    layout="wide"
)

# Título da aplicação
st.title("🚜 JD-ISOBUS Monitor")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    # Campo para IP do ESP32
    esp32_ip = st.text_input("IP do ESP32", "192.168.4.1")
    
    # Botão para testar conexão
    if st.button("Testar Conexão"):
        try:
            response = requests.get(f"http://{esp32_ip}/status", timeout=5)
            if response.status_code == 200:
                st.success("Conectado ao ESP32!")
            else:
                st.error("Erro ao conectar ao ESP32")
        except:
            st.error("Erro ao conectar ao ESP32")

# Layout principal em colunas
col1, col2 = st.columns(2)

# Coluna 1: Gauges e indicadores
with col1:
    st.subheader("Indicadores em Tempo Real")
    
    # Exemplo de gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 270,
        title = {'text': "Velocidade"},
        gauge = {
            'axis': {'range': [None, 500]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 250], 'color': "lightgray"},
                {'range': [250, 400], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 490
            }
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

# Coluna 2: Gráficos de linha
with col2:
    st.subheader("Histórico de Dados")
    
    # Dados de exemplo
    chart_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="S"),
            "valor": [10, 20, 15, 25, 30, 20, 15, 25, 30, 35]
        }
    )
    
    # Gráfico de linha
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data["timestamp"],
        y=chart_data["valor"],
        mode='lines+markers',
        name='Valor'
    ))
    fig.update_layout(
        xaxis_title="Tempo",
        yaxis_title="Valor",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Área para logs e mensagens
st.subheader("Logs do Sistema")
log_container = st.empty()
log_container.code("Sistema iniciado. Aguardando dados do ESP32...") 