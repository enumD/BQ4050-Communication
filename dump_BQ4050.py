import crcmod
from smbus2 import SMBus
import time

# Configuration
I2C_BUS = 1  # I2C bus number
DEVICE_ADDRESS = 0x0B  # I2C address for BQ4050

# Function to calculate the CRC (PEC)
def calculate_crc(data):
    """
    Calculate the CRC-8 SMBus for the provided data.
    """
    crc8 = crcmod.predefined.mkCrcFun('crc-8')
    return crc8(bytes(data))

def send_command(bus, device_address, command, data=[]):
    """
    Sends an SMBus command with optional data and calculates the CRC.
    """
    try:
        # Build the packet with the command and data
        packet = [command] + data
        
        # Calculate the CRC
        crc = calculate_crc([device_address << 1] + packet)
        packet.append(crc)  # Add CRC to the packet
        
        # Send the packet to the device
        bus.write_i2c_block_data(device_address, packet[0], packet[1:])
        print(f"Command sent: {packet}")
    except Exception as e:
        print(f"Error sending command: {e}")

def read_response(bus, device_address, length):
    """
    Reads an SMBus response and verifies the CRC.
    """
    try:
        # Read the data from the device (add 1 to also read the CRC)
        response = bus.read_i2c_block_data(device_address, 0, length + 1)
        
        # Separate the data and the received CRC
        data = response[:-1]
        received_crc = response[-1]
        
        # Calculate the expected CRC
        crc = calculate_crc([device_address << 1 | 1] + data)
        
        # Verify the CRC
        if crc == received_crc:
            print(f"Valid response: {data}")
            return data
        else:
            print(f"CRC error: expected {crc}, received {received_crc}")
            return None
    except Exception as e:
        print(f"Error reading response: {e}")
        return None

def main():
    # Initialize the I²C bus
    with SMBus(I2C_BUS) as bus:
        # Ask the user to input the command in hexadecimal format
        command_input = input("Enter the command in hexadecimal format (e.g., 0a 02 00): ")
        
        # Convert the string into a list of bytes
        command_bytes = [int(byte, 16) for byte in command_input.split()]
        
        # Send the command (0x00 is the initial command, you can modify it as needed)
        print("Sending command...")
        send_command(bus, DEVICE_ADDRESS, 0x00, command_bytes)
        time.sleep(1)
        
        # Read the response (e.g., 6 bytes + CRC)
        print("Reading response...")
        response = read_response(bus, DEVICE_ADDRESS, 6)
        
        if response:
            # Print the received data
            print(f"Received data: {response}")
        else:
            print("Error reading the response.")

if __name__ == "__main__":
    main()
