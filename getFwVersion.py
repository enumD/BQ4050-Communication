import smbus2
import time

# Config
I2C_BUS = 1
DEVICE_ADDRESS = 0x09

def send_command(bus, device_address, command, data=[]):
    try:
        packet = [command] + data
        bus.write_i2c_block_data(device_address, packet[0], packet[1:])
        print(f"Command sent: {packet}")
    except Exception as e:
        print(f"Error sending command: {e}")

def read_response(bus, device_address, command, length):
    try:
        response = bus.read_i2c_block_data(device_address, command, length)
        
        hex_response = [hex(value) for value in response]
        print(f"Response (in hex): {hex_response}")
        
        return response
    except Exception as e:
        print(f"Error reading response: {e}")
        return None


def main():
    with smbus2.SMBus(I2C_BUS) as bus:
    
        # Read Hardware Version
        send_command(bus, DEVICE_ADDRESS, 0x44, [0x03, 0x00])
        response = read_response(bus, DEVICE_ADDRESS, 0x44, 4)

        # Read Firmware Version
        send_command(bus, DEVICE_ADDRESS, 0x44, [0x02, 0x00])
        response = read_response(bus, DEVICE_ADDRESS, 0x44, 4)

        # If checksum
        send_command(bus, DEVICE_ADDRESS, 0x44, [0x04, 0x00])
        response = read_response(bus, DEVICE_ADDRESS, 0x44, 4)

if __name__ == "__main__":
    main()
