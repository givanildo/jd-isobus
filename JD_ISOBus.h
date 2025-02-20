#ifndef JD_ISOBUS_H
#define JD_ISOBUS_H

#include <Arduino.h>
#include <mcp_can.h>

// Máscaras para decodificação
#define MASK_2_BIT ((1 << 2) - 1)
#define MASK_3_BIT ((1 << 3) - 1) 
#define MASK_8_BIT ((1 << 8) - 1)

// PGNs John Deere
#define PGN_GRAIN_FLOW 61184
#define PGN_HEADER_INFO 65535

class JD_ISOBus {
public:
    JD_ISOBus(uint8_t cs_pin);
    bool begin();
    
    // Estrutura para armazenar dados decodificados
    struct CANMessage {
        uint32_t pgn;
        uint8_t source;
        uint8_t priority;
        uint64_t payload;
        uint32_t timestamp;
    };

    // Estrutura para dados de colheita
    struct HarvestData {
        float grainFlow;     // kg/s
        float grainMoisture; // %
        uint16_t headerWidth;  // mm
        uint8_t headerRows;    // count
        uint8_t rowSpacing;    // cm
    };

    bool getMessage(CANMessage &msg);
    bool parseMessage(const CANMessage &msg, HarvestData &data);

private:
    MCP_CAN _can;
    HarvestData _lastData;

    bool decodeGrainFlow(const CANMessage &msg, HarvestData &data);
    bool decodeHeaderInfo(const CANMessage &msg, HarvestData &data);
};

#endif 