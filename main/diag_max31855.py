"""MAX31855 diagnostic: print the raw 32-bit frame and decode every field.

Run on the board:  import diag_max31855
Stop with Ctrl+C. Pins match main.py.
"""

import machine
import time

SENSOR_SCK = 18
SENSOR_MISO = 19
SENSOR_MOSI = 16
SENSOR_CS = 17

spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0,
                  sck=machine.Pin(SENSOR_SCK), miso=machine.Pin(SENSOR_MISO),
                  mosi=machine.Pin(SENSOR_MOSI))
cs = machine.Pin(SENSOR_CS, machine.Pin.OUT, value=1)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def diagnose(data):
    word = int.from_bytes(data, "big")
    print("bytes:", " ".join("%02x" % b for b in data), "| bits:", "{:032b}".format(word))
    if word == 0:
        print("  -> alles 0: MISO haengt auf GND / MAX31855 ohne Spannung / SO nicht verbunden")
    elif word == 0xFFFFFFFF:
        print("  -> alles 1: MISO floatet/Pull-up, CS oder SCK nicht verbunden, kein Chip antwortet")
    if word & 0x10000:
        faults = [n for bit, n in ((1, "OC offen"), (2, "SCG Kurzschluss GND"), (4, "SCV Kurzschluss VCC"))
                  if word & bit]
        print("  FAULT-Bit gesetzt:", ", ".join(faults) or "unbekannt")
    if word & 0x8 or word & 0x8000:
        print("  Reserved-Bits gesetzt (Bit 3/15) -> Frame ungueltig, Verdrahtung/Takt pruefen")
    thermo = signed((word >> 18) & 0x3FFF, 14) * 0.25
    internal = signed((word >> 4) & 0xFFF, 12) * 0.0625
    print("  Thermoelement: %.2f C | Referenzstelle (Chip): %.2f C" % (thermo, internal))


while True:
    cs.value(0)
    time.sleep_us(10)
    data = spi.read(4)
    cs.value(1)
    diagnose(data)
    time.sleep(1)
