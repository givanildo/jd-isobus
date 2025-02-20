#include "JD_ISOBus.h"

JD_ISOBus::JD_ISOBus(uint8_t cs_pin) : _can(cs_pin) {
    memset(&_lastData, 0, sizeof(HarvestData));
}

bool JD_ISOBus::begin() {
    // Inicializa o MCP2515 com 250kbps
    if (_can.begin(MCP_ANY, CAN_250KBPS, MCP_8MHZ) == CAN_OK) {
        _can.setMode(MCP_NORMAL);
        return true;
    }
    return false;
}

bool JD_ISOBus::getMessage(CANMessage &msg) {
    uint32_t rxId;
    uint8_t len;
    uint8_t rxBuf[8];
    
    if (_can.readMsgBuf(&rxId, &len, rxBuf) == CAN_OK) {
        // Decodifica o ID CAN J1939
        msg.priority = (rxId >> 26) & MASK_3_BIT;
        msg.pgn = (rxId >> 8) & 0x3FFFF;
        msg.source = rxId & MASK_8_BIT;
        
        // Converte o payload para uint64_t
        msg.payload = 0;
        for(int i = 0; i < len && i < 8; i++) {
            msg.payload |= (uint64_t)rxBuf[i] << (i * 8);
        }
        
        msg.timestamp = millis();
        return true;
    }
    return false;
}

bool JD_ISOBus::parseMessage(const CANMessage &msg, HarvestData &data) {
    bool decoded = false;
    
    switch(msg.pgn) {
        case PGN_GRAIN_FLOW:
            decoded = decodeGrainFlow(msg, data);
            break;
            
        case PGN_HEADER_INFO:
            decoded = decodeHeaderInfo(msg, data);
            break;
    }
    
    if(decoded) {
        _lastData = data;
    }
    
    return decoded;
}

bool JD_ISOBus::decodeGrainFlow(const CANMessage &msg, HarvestData &data) {
    // Verifica se é a fonte correta (211 para John Deere)
    if(msg.source != 211) return false;
    
    // Pega o opcode dos primeiros 16 bits
    uint16_t opcode = msg.payload & 0xFFFF;
    
    // Se opcode for 2383, contém dados de fluxo e umidade
    if(opcode == 2383) {
        // Extrai fluxo de grãos (bits 16-31)
        uint16_t grainFlow = (msg.payload >> 16) & 0xFFFF;
        data.grainFlow = grainFlow * 0.01f; // Escala 0.01 kg/s
        
        // Extrai umidade (bits 32-47)
        uint16_t moisture = (msg.payload >> 32) & 0xFFFF;
        data.grainMoisture = moisture * 0.01f; // Escala 0.01%
        
        return true;
    }
    
    return false;
}

bool JD_ISOBus::decodeHeaderInfo(const CANMessage &msg, HarvestData &data) {
    // Verifica se é a fonte correta (211, 234 ou 242 para John Deere)
    if(msg.source != 211 && msg.source != 234 && msg.source != 242) return false;
    
    // Pega o opcode do primeiro byte
    uint8_t opcode = msg.payload & 0xFF;
    
    // Se opcode for 24, contém dados do cabeçote
    if(opcode == 24) {
        // Extrai largura em uso (bits 8-23)
        data.headerWidth = (msg.payload >> 8) & 0xFFFF;
        
        // Extrai número de linhas (bits 48-55)
        data.headerRows = (msg.payload >> 48) & 0xFF;
        
        // Extrai espaçamento entre linhas (bits 56-63)
        data.rowSpacing = (msg.payload >> 56) & 0xFF;
        
        return true;
    }
    
    return false;
} 