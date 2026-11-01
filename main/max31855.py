import time
import struct

class MAX31855:
    def __init__(self, spi, cs_pin):
        self.spi = spi
        self.cs = cs_pin
        self.cs.init(cs_pin.OUT, value=1)

    def read(self):
        """Return (temperature, status); temperature is None unless status is 'OK'."""
        self.cs.value(0)
        data = self.spi.read(4)
        self.cs.value(1)

        if len(data) != 4:
            return None, "No SPI data"

        raw = struct.unpack(">I", data)[0]

        # Verdrahtungsfehler: ein nicht antwortender Chip liefert nur 0 oder nur 1
        if raw == 0:
            return None, "No response: all zeros (check VIN/GND or SO->MISO)"
        if raw == 0xFFFFFFFF:
            return None, "No response: all ones (check CS/SCK/SO wiring)"
        # Bit 3 und Bit 15 sind beim MAX31855 immer 0
        if raw & 0x8008:
            return None, "Invalid data frame (check wiring/clock)"

        # Fehlerbits prüfen (Bit 0: OC, Bit 1: SCG, Bit 2: SCV)
        if raw & 0x7:
            faults = [name for bit, name in ((1, "Thermocouple open/not connected"),
                                             (2, "Thermocouple short to GND"),
                                             (4, "Thermocouple short to VCC"))
                      if raw & bit]
            return None, ", ".join(faults)

        # 14-Bit Temperaturwert isolieren (Bit 31 bis 18)
        temp_raw = (raw >> 18) & 0x3FFF
        if raw & 0x80000000: # Vorzeichenbit
            temp_raw -= 16384

        return temp_raw * 0.25, "OK"

    def read_temp(self):
        return self.read()[0]