import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json
import time
from datetime import datetime
import pysobus

# Configuração da página
st.set_page_config(
    page_title="JD-ISOBus Monitor",
    page_icon="🚜",
    layout="wide"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .status-connected {
        color: green;
        font-weight: bold;
    }
    .status-disconnected {
        color: red;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'esp_ip' not in st.session_state:
    st.session_state.esp_ip = "192.168.4.1"

# Título principal
st.title("JD-ISOBus Monitor")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    # Campo para IP do ESP32
    esp_ip = st.text_input("IP do ESP32", st.session_state.esp_ip)
    
    # Botão para testar conexão
    if st.button("Testar Conexão"):
        try:
            response = requests.get(f"http://{esp_ip}/status", timeout=5)
            if response.status_code == 200:
                st.session_state.connected = True
                st.session_state.esp_ip = esp_ip
                st.success("Conectado com sucesso!")
            else:
                st.session_state.connected = False
                st.error("Falha na conexão")
        except:
            st.session_state.connected = False
            st.error("Erro ao conectar")
    
    # Status da conexão
    st.write("Status:", 
             f'<span class="status-connected">Conectado</span>' if st.session_state.connected 
             else f'<span class="status-disconnected">Desconectado</span>', 
             unsafe_allow_html=True)
    
    # Filtros
    st.header("Filtros")
    pgn_filter = st.multiselect(
        "PGN",
        options=pysobus.pgn.PGN_NAMES.keys(),
        format_func=lambda x: f"{x} - {pysobus.pgn.PGN_NAMES[x]}"
    )

# Layout principal em três colunas
col1, col2, col3 = st.columns(3)

# Função para criar gauge
def create_gauge(value, title, min_val, max_val, suffix=""):
    return go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [min_val, max_val*0.33], 'color': "lightgray"},
                {'range': [max_val*0.33, max_val*0.66], 'color': "gray"},
                {'range': [max_val*0.66, max_val], 'color': "darkgray"}
            ]
        }
    ))

# Exemplo de gauges (substitua pelos dados reais do CAN bus)
with col1:
    st.subheader("Velocidade do Motor")
    fig = create_gauge(1800, "RPM", 0, 3000)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Temperatura")
    fig = create_gauge(85, "°C", 0, 120)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader("Nível de Combustível")
    fig = create_gauge(75, "%", 0, 100)
    st.plotly_chart(fig, use_container_width=True)

# Gráfico de linha temporal
st.subheader("Histórico de Dados")
chart_data = pd.DataFrame({
    'Tempo': pd.date_range(start=datetime.now(), periods=100, freq='S'),
    'RPM': [1800 + i*10 for i in range(100)],
    'Temperatura': [85 + i*0.5 for i in range(100)],
    'Combustível': [75 - i*0.2 for i in range(100)]
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=chart_data['Tempo'], y=chart_data['RPM'],
                        mode='lines', name='RPM'))
fig.add_trace(go.Scatter(x=chart_data['Tempo'], y=chart_data['Temperatura'],
                        mode='lines', name='Temperatura'))
fig.add_trace(go.Scatter(x=chart_data['Tempo'], y=chart_data['Combustível'],
                        mode='lines', name='Combustível'))

fig.update_layout(
    xaxis_title="Tempo",
    yaxis_title="Valor",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# Tabela de mensagens CAN
st.subheader("Mensagens CAN")
if st.session_state.connected:
    try:
        # Aqui você deve implementar a lógica para receber dados do ESP32
        # Este é apenas um exemplo
        data = {
            'Timestamp': [datetime.now()],
            'PGN': ['61444'],
            'Descrição': ['Electronic Engine Controller 1'],
            'Dados': ['FF FF FF FF FF FF FF FF']
        }
        df = pd.DataFrame(data)
        st.dataframe(df)
    except:
        st.error("Erro ao receber dados do ESP32")
else:
    st.warning("Conecte-se ao ESP32 para visualizar os dados") 