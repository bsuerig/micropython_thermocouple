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
            return None, "Keine SPI-Daten"

        raw = struct.unpack(">I", data)[0]

        # Verdrahtungsfehler: ein nicht antwortender Chip liefert nur 0 oder nur 1
        if raw == 0:
            return None, "Keine Antwort: nur 0 (VIN/GND oder SO->MISO pruefen)"
        if raw == 0xFFFFFFFF:
            return None, "Keine Antwort: nur 1 (CS/SCK/SO-Verdrahtung pruefen)"
        # Bit 3 und Bit 15 sind beim MAX31855 immer 0
        if raw & 0x8008:
            return None, "Ungueltiger Datenframe (Verdrahtung/Takt pruefen)"

        # Fehlerbits prüfen (Bit 0: OC, Bit 1: SCG, Bit 2: SCV)
        if raw & 0x7:
            faults = [name for bit, name in ((1, "Thermoelement offen/nicht angeschlossen"),
                                             (2, "Thermoelement Kurzschluss an GND"),
                                             (4, "Thermoelement Kurzschluss an VCC"))
                      if raw & bit]
            return None, ", ".join(faults)

        # 14-Bit Temperaturwert isolieren (Bit 31 bis 18)
        temp_raw = (raw >> 18) & 0x3FFF
        if raw & 0x80000000: # Vorzeichenbit
            temp_raw -= 16384

        return temp_raw * 0.25, "OK"

    def read_temp(self):
        return self.read()[0]