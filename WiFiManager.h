#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>

class WiFiManager {
public:
    WiFiManager();
    void begin();
    bool isConnected();
    String getLocalIP();
    String getGateway();
    String getSSID();

private:
    WebServer server;
    DNSServer dnsServer;
    
    // Configurações do AP
    const char* AP_SSID = "JD-ISOBus-Config";
    const char* AP_PASS = "12345678";
    const byte DNS_PORT = 53;
    
    // Funções do servidor web
    void setupAP();
    void handleRoot();
    void handleScan();
    void handleConnect();
    void handleNotFound();
    
    // Funções auxiliares
    bool connectToWiFi(const char* ssid, const char* pass, int timeout = 20);
    void saveConfig(const char* ssid, const char* pass);
    bool loadConfig();
    String getNetworkList();
    String generateHTML();
};

#endif 