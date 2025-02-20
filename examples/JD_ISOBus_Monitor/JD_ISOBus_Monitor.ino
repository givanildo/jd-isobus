#include "WiFiManager.h"
#include "JD_ISOBus.h"
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>

// Pinos do MCP2515
#define CAN_CS_PIN 5
#define CAN_INT_PIN 4

// Objetos globais
WiFiManager wifiManager;
JD_ISOBus isobus(CAN_CS_PIN);
AsyncWebServer webServer(80);

// Buffer circular para mensagens CAN
const int MAX_CAN_MESSAGES = 50;
JD_ISOBus::CANMessage canBuffer[MAX_CAN_MESSAGES];
int canBufferIndex = 0;

// Função para gerar JSON com dados do sistema
String getSystemData() {
    StaticJsonDocument<512> doc;
    
    // Status da rede
    doc["wifi"]["connected"] = wifiManager.isConnected();
    doc["wifi"]["ssid"] = wifiManager.getSSID();
    doc["wifi"]["ip"] = wifiManager.getLocalIP();
    doc["wifi"]["gateway"] = wifiManager.getGateway();
    
    // Status do CAN
    JsonArray messages = doc["can_messages"].createNestedArray();
    
    for(int i = 0; i < MAX_CAN_MESSAGES; i++) {
        if(canBuffer[i].timestamp > 0) {
            JsonObject msg = messages.createNestedObject();
            msg["pgn"] = canBuffer[i].pgn;
            msg["source"] = canBuffer[i].source;
            msg["timestamp"] = canBuffer[i].timestamp;
            
            // Converte payload para string hex
            char payload[20];
            sprintf(payload, "%016llX", canBuffer[i].payload);
            msg["payload"] = payload;
        }
    }
    
    String output;
    serializeJson(doc, output);
    return output;
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nIniciando JD-ISOBus Monitor...");
    
    // Inicializa SPIFFS
    if(!SPIFFS.begin(true)) {
        Serial.println("Erro ao montar SPIFFS");
        return;
    }
    
    // Inicializa WiFi
    wifiManager.begin();
    
    // Inicializa CAN
    pinMode(CAN_INT_PIN, INPUT);
    if(!isobus.begin()) {
        Serial.println("Erro ao inicializar CAN Bus!");
        return;
    }
    Serial.println("CAN Bus inicializado");
    
    // Configura rotas do servidor web
    webServer.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(SPIFFS, "/index.html", "text/html");
    });
    
    webServer.on("/data", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "application/json", getSystemData());
    });
    
    webServer.serveStatic("/", SPIFFS, "/");
    
    // Inicia servidor web
    webServer.begin();
    Serial.println("Servidor web iniciado");
}

void loop() {
    // Processa mensagens CAN
    JD_ISOBus::CANMessage msg;
    JD_ISOBus::HarvestData data;
    
    if(isobus.getMessage(msg)) {
        // Armazena no buffer circular
        canBuffer[canBufferIndex] = msg;
        canBufferIndex = (canBufferIndex + 1) % MAX_CAN_MESSAGES;
        
        // Decodifica e imprime dados
        if(isobus.parseMessage(msg, data)) {
            Serial.printf("PGN: 0x%X, Source: %d\n", msg.pgn, msg.source);
            
            if(msg.pgn == PGN_GRAIN_FLOW) {
                Serial.printf("Fluxo: %.2f kg/s, Umidade: %.1f%%\n", 
                    data.grainFlow, data.grainMoisture);
            }
            else if(msg.pgn == PGN_HEADER_INFO) {
                Serial.printf("Largura: %d mm, Linhas: %d, Espaçamento: %d cm\n",
                    data.headerWidth, data.headerRows, data.rowSpacing);
            }
        }
    }
    
    delay(10); // Pequeno delay para não sobrecarregar
} 