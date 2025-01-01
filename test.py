from smbus2 import SMBus

def scan_i2c_bus(bus_number):
    """
    Scansione del bus I²C per rilevare dispositivi connessi.
    
    :param bus_number: Numero del bus I²C (es. 1 per Raspberry Pi)
    """
    print(f"Scanning I²C bus {bus_number}...")
    try:
        with SMBus(bus_number) as bus:
            devices = []
            for address in range(0x03, 0x78):  # Indirizzi validi per I²C
                try:
                    bus.write_quick(address)
                    devices.append(hex(address))
                except OSError:
                    # Ignora errori di scrittura per indirizzi non validi
                    pass
            if devices:
                print(f"Devices found: {', '.join(devices)}")
            else:
                print("No devices found.")
    except Exception as e:
        print(f"Error scanning I²C bus: {e}")

if __name__ == "__main__":
    # Scansione del bus I²C numero 1
    scan_i2c_bus(1)
