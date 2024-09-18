import serial.tools.list_ports
import time
from dataclasses import dataclass

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = []
    for port in ports:
        available_ports.append(port.device)
    return available_ports
    
def connect_to_serial(port, baud_rate=9600):
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"Connected to {port} at {baud_rate} baud rate.")
        return ser
    except serial.SerialException as e:
        print(f"Failed to connect to {port}: {e}")
        return None

@dataclass
class ServoMotor:
    prefix: str
    angle_len: int = 3
    
    def get_command(self, angle: float):
        a_cmd = str(angle)
        if len(a_cmd) < self.angle_len:
            a_cmd = '0'*abs(len(a_cmd)-self.angle_len) + a_cmd
        cmd = f'{self.prefix}{a_cmd}\n'
        return cmd
    
    def send_command(self, serial: serial.Serial, angle: float):
        command = self.get_command(angle)
        serial.write(command.encode()) 
