# JD-ISOBUS - Leitor CAN Bus para Implementos John Deere

Este projeto consiste em um sistema de leitura de dados CAN Bus de implementos agrícolas John Deere, utilizando ESP32 e MCP2515, com interface web em Streamlit.

## Estrutura do Projeto

```
jd-isobus/
├── esp32/              # Código MicroPython para ESP32
│   ├── boot.py        # Configuração inicial do ESP32
│   ├── main.py        # Código principal
│   ├── wifi_manager.py # Gerenciador de WiFi e AP
│   └── can_reader.py  # Leitor CAN Bus
├── web/               # Aplicação Web
│   ├── app.py         # Aplicação Streamlit
│   ├── requirements.txt # Dependências Python
│   └── utils/         # Utilitários
│       ├── can_parser.py    # Parser CAN
│       └── data_processor.py # Processador de dados
```

## Requisitos

### Hardware
- ESP32
- Módulo MCP2515
- Conexões CAN Bus

### Software
- MicroPython para ESP32
- Python 3.8+
- Bibliotecas Python (ver requirements.txt)

## Configuração do Ambiente

1. **Configurar ESP32:**
   ```bash
   # Instalar ferramentas MicroPython
   pip install esptool
   pip install adafruit-ampy
   ```

2. **Configurar Ambiente Web:**
   ```bash
   cd web
   pip install -r requirements.txt
   ```

## Funcionalidades

- Leitura de dados CAN Bus via ESP32/MCP2515
- Access Point para configuração inicial
- Captive Portal para configuração WiFi
- Interface web com gráficos e gauges
- Filtragem de dados baseada no protocolo J1939
- Monitoramento em tempo real

## Uso

1. **Configuração Inicial ESP32:**
   - Conecte ao AP "JD-ISOBUS-Config"
   - Configure a rede WiFi desejada
   - O ESP32 se conectará à rede configurada

2. **Interface Web:**
   ```bash
   cd web
   streamlit run app.py
   ```

## Contribuição

Para contribuir com o projeto:
1. Faça um Fork
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes. 