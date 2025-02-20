#include <JD_ISOBus.h>

// Pino CS do MCP2515
#define CAN_CS_PIN 5

// Instancia objeto da biblioteca
JD_ISOBus isobus(CAN_CS_PIN);

void setup() {
    Serial.begin(115200);
    Serial.println("Iniciando JD ISOBus...");
    
    // Inicializa CAN Bus
    if (!isobus.begin()) {
        Serial.println("Erro ao inicializar CAN Bus!");
        while(1);
    }
    
    Serial.println("CAN Bus inicializado com sucesso!");
}

void loop() {
    JD_ISOBus::CANMessage msg;
    JD_ISOBus::HarvestData data;
    
    // Tenta ler uma mensagem CAN
    if (isobus.getMessage(msg)) {
        
        // Tenta decodificar a mensagem
        if (isobus.parseMessage(msg, data)) {
            
            // Imprime os dados decodificados
            Serial.println("Dados recebidos:");
            Serial.print("PGN: 0x");
            Serial.println(msg.pgn, HEX);
            Serial.print("Fonte: ");
            Serial.println(msg.source);
            
            if (msg.pgn == PGN_GRAIN_FLOW) {
                Serial.print("Fluxo de grãos: ");
                Serial.print(data.grainFlow);
                Serial.println(" kg/s");
                
                Serial.print("Umidade: ");
                Serial.print(data.grainMoisture);
                Serial.println(" %");
            }
            else if (msg.pgn == PGN_HEADER_INFO) {
                Serial.print("Largura do cabeçote: ");
                Serial.print(data.headerWidth);
                Serial.println(" mm");
                
                Serial.print("Número de linhas: ");
                Serial.println(data.headerRows);
                
                Serial.print("Espaçamento: ");
                Serial.print(data.rowSpacing);
                Serial.println(" cm");
            }
            
            Serial.println();
        }
    }
    
    delay(100); // Pequeno delay para não sobrecarregar
} 