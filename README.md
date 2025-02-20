# Biblioteca JD_ISOBus

Biblioteca Arduino para monitoramento de implementos agrícolas John Deere via CAN bus J1939.

## Recursos

- 📊 Leitura de dados CAN J1939
  - Fluxo de grãos
  - Umidade
  - Informações do cabeçote
- 📱 Interface web responsiva
- 🔄 Configuração WiFi via portal cativo
- 💾 Armazenamento de configurações

## Hardware Necessário

- ESP32
- Módulo MCP2515 (CAN Bus)

### Conexões

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

1. Baixe este repositório
2. Copie para a pasta `libraries` do Arduino
3. Instale as dependências:
   - ArduinoJson
   - AsyncTCP
   - ESPAsyncWebServer
   - MCP_CAN_lib

## Exemplos

### Monitor Básico
```cpp
#include <JD_ISOBus.h>

JD_ISOBus isobus(5); // CS no pino 5

void setup() {
  Serial.begin(115200);
  if (!isobus.begin()) {
    Serial.println("Erro CAN!");
    while(1);
  }
}

void loop() {
  JD_ISOBus::CANMessage msg;
  JD_ISOBus::HarvestData data;
  
  if (isobus.getMessage(msg) && isobus.parseMessage(msg, data)) {
    Serial.printf("Fluxo: %.2f kg/s\n", data.grainFlow);
    Serial.printf("Umidade: %.1f%%\n", data.grainMoisture);
  }
  delay(100);
}
```

### Monitor Web
Veja o exemplo completo em `examples/JD_ISOBus_Monitor`

## Interface Web

![Interface Web](docs/interface.png)

- Status da conexão
- Dados em tempo real
- Gráficos e indicadores
- Histórico de mensagens

## PGNs Suportados

- `61184`: Fluxo e umidade de grãos
- `65535`: Informações do cabeçote

## Licença

MIT License

## Autor

Givanildo Brunetta
- Email: givanildobrunetta@gmail.com
- GitHub: https://github.com/givanildo
