#include "WiFiManager.h"

WiFiManager::WiFiManager() : server(80) {
}

void WiFiManager::begin() {
    // Inicializa SPIFFS
    if(!SPIFFS.begin(true)) {
        Serial.println("Erro ao montar SPIFFS");
        return;
    }

    // Tenta carregar configuração salva
    if(loadConfig()) {
        Serial.println("Configuração WiFi carregada");
        return;
    }

    // Se não conseguiu conectar, cria AP
    setupAP();
}

void WiFiManager::setupAP() {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    
    Serial.println("Access Point criado");
    Serial.print("SSID: ");
    Serial.println(AP_SSID);
    Serial.print("IP: ");
    Serial.println(WiFi.softAPIP());

    // Configura DNS para portal cativo
    dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());

    // Configura rotas do servidor web
    server.on("/", HTTP_GET, [this](){ handleRoot(); });
    server.on("/scan", HTTP_GET, [this](){ handleScan(); });
    server.on("/connect", HTTP_POST, [this](){ handleConnect(); });
    server.onNotFound([this](){ handleNotFound(); });
    
    server.begin();
    Serial.println("Servidor web iniciado");
}

void WiFiManager::handleRoot() {
    server.send(200, "text/html", generateHTML());
}

void WiFiManager::handleScan() {
    server.send(200, "application/json", getNetworkList());
}

void WiFiManager::handleConnect() {
    String ssid = server.arg("ssid");
    String pass = server.arg("password");

    if(ssid.length() > 0) {
        server.send(200, "text/plain", "Conectando...");
        
        if(connectToWiFi(ssid.c_str(), pass.c_str())) {
            saveConfig(ssid.c_str(), pass.c_str());
            ESP.restart();
        } else {
            WiFi.mode(WIFI_AP);
            server.send(500, "text/plain", "Falha ao conectar");
        }
    } else {
        server.send(400, "text/plain", "SSID não fornecido");
    }
}

void WiFiManager::handleNotFound() {
    server.sendHeader("Location", "/", true);
    server.send(302, "text/plain", "");
}

bool WiFiManager::connectToWiFi(const char* ssid, const char* pass, int timeout) {
    Serial.print("Conectando a ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pass);

    int attempts = 0;
    while(WiFi.status() != WL_CONNECTED && attempts < timeout) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if(WiFi.status() == WL_CONNECTED) {
        Serial.print("Conectado! IP: ");
        Serial.println(WiFi.localIP());
        return true;
    }

    Serial.println("Falha ao conectar");
    return false;
}

void WiFiManager::saveConfig(const char* ssid, const char* pass) {
    StaticJsonDocument<200> doc;
    doc["ssid"] = ssid;
    doc["password"] = pass;

    File file = SPIFFS.open("/wifi_config.json", "w");
    if(!file) {
        Serial.println("Erro ao abrir arquivo para escrita");
        return;
    }

    serializeJson(doc, file);
    file.close();
}

bool WiFiManager::loadConfig() {
    File file = SPIFFS.open("/wifi_config.json", "r");
    if(!file) {
        return false;
    }

    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    if(error) {
        return false;
    }

    const char* ssid = doc["ssid"];
    const char* pass = doc["password"];

    return connectToWiFi(ssid, pass);
}

String WiFiManager::getNetworkList() {
    int n = WiFi.scanNetworks();
    StaticJsonDocument<1024> doc;
    JsonArray networks = doc.createNestedArray("networks");

    for(int i = 0; i < n; i++) {
        networks.add(WiFi.SSID(i));
    }

    String result;
    serializeJson(doc, result);
    return result;
}

String WiFiManager::generateHTML() {
    return R"(
<!DOCTYPE html>
<html>
<head>
    <title>JD-ISOBus Config</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; margin: 5px 0; }
        .input { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        h2 { color: #333; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h2>JD-ISOBus Config</h2>
        <div id="networks"></div>
        <div id="connect-form" style="display:none">
            <h3>Conectar a <span id="ssid-label"></span></h3>
            <input type="password" id="password" class="input" placeholder="Senha">
            <button onclick="connect()" class="btn">Conectar</button>
        </div>
    </div>
    <script>
        // Carrega lista de redes
        fetch('/scan')
            .then(response => response.json())
            .then(data => {
                const networksDiv = document.getElementById('networks');
                data.networks.forEach(ssid => {
                    const btn = document.createElement('button');
                    btn.className = 'btn';
                    btn.textContent = ssid;
                    btn.onclick = () => showConnect(ssid);
                    networksDiv.appendChild(btn);
                });
            });

        function showConnect(ssid) {
            document.getElementById('ssid-label').textContent = ssid;
            document.getElementById('connect-form').style.display = 'block';
            window.selectedSSID = ssid;
        }

        function connect() {
            const data = new URLSearchParams();
            data.append('ssid', window.selectedSSID);
            data.append('password', document.getElementById('password').value);

            fetch('/connect', {
                method: 'POST',
                body: data
            })
            .then(response => {
                if(response.ok) {
                    alert('Conectando... O dispositivo irá reiniciar.');
                } else {
                    alert('Falha ao conectar. Tente novamente.');
                }
            });
        }
    </script>
</body>
</html>
    )";
}

bool WiFiManager::isConnected() {
    return WiFi.status() == WL_CONNECTED;
}

String WiFiManager::getLocalIP() {
    return WiFi.localIP().toString();
}

String WiFiManager::getGateway() {
    return WiFi.gatewayIP().toString();
}

String WiFiManager::getSSID() {
    return WiFi.SSID();
} 