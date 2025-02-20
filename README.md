# JD-ISOBus Monitor

Monitor de dados CAN bus para implementos agrícolas John Deere usando ESP32 e MCP2515.

## Características

- Leitura de dados CAN bus via protocolo J1939
- Configuração WiFi via portal cativo
- Interface web responsiva para visualização em tempo real
- Suporte para PGNs específicos da John Deere:
  - PGN 61184: Fluxo e umidade de grãos
  - PGN 65535: Informações do cabeçote
- Visualização em gauges e tabelas
- Armazenamento de configurações na memória flash

## Requisitos de Hardware

- ESP32
- Módulo MCP2515 CAN bus
- Conexões:
  ```
  ESP32     | MCP2515
  ----------|----------
  GPIO5     | CS
  GPIO18    | SCK
  GPIO23    | MOSI
  GPIO19    | MISO
  GPIO4     | INT
  3.3V      | VCC
  GND       | GND
  ```

## Instalação

### Dependências Arduino IDE

1. Instale as seguintes bibliotecas via Gerenciador de Bibliotecas:
   - ArduinoJson
   - MCP_CAN_lib

2. Instale manualmente as bibliotecas:
   - [AsyncTCP](https://github.com/me-no-dev/AsyncTCP)
   - [ESPAsyncWebServer](https://github.com/me-no-dev/ESPAsyncWebServer)

3. Instale o plugin "ESP32 Sketch Data Upload":
   - [ESP32 Sketch Data Upload](https://github.com/me-no-dev/arduino-esp32fs-plugin)

### Configuração

1. Clone este repositório:
   ```bash
   git clone https://github.com/givanildo/jd-isobus.git
   ```

2. Abra o arquivo `JD_ISOBus_Monitor.ino` na Arduino IDE

3. Selecione a placa "ESP32 Dev Module" em Ferramentas > Placa

4. Faça o upload do código

5. Use "ESP32 Sketch Data Upload" para enviar os arquivos da pasta data/

## Uso

1. Ao ligar, o ESP32 criará uma rede WiFi "JD-ISOBus-Config"
2. Conecte-se a esta rede (senha: 12345678)
3. Acesse o portal de configuração (geralmente 192.168.4.1)
4. Selecione sua rede WiFi e insira a senha
5. O ESP32 irá reiniciar e conectar-se à rede configurada
6. Acesse a interface web através do IP mostrado no monitor serial

## Interface Web

A interface web mostra:
- Status da conexão WiFi
- Dados em tempo real via gauges:
  - Fluxo de grãos (kg/s)
  - Umidade (%)
  - Largura do cabeçote (m)
- Tabela com últimas mensagens CAN recebidas

## Estrutura do Projeto

```
JD_ISOBus_Monitor/
  ├── JD_ISOBus_Monitor.ino    # Arquivo principal
  ├── WiFiManager.h            # Gerenciador WiFi (header)
  ├── WiFiManager.cpp          # Gerenciador WiFi (implementação)
  ├── JD_ISOBus.h             # Parser J1939 (header)
  ├── JD_ISOBus.cpp           # Parser J1939 (implementação)
  └── data/                    # Arquivos web
      └── index.html          # Interface web
```

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## Licença

MIT License

## Autor

Givanildo Brunetta
- Email: givanildobrunetta@gmail.com
- GitHub: https://github.com/givanildo
