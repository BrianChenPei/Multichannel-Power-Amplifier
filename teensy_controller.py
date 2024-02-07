import serial
import serial.tools.list_ports
import json

class TeensyController:
    def __init__(self, port=None, baud_rate=115200):
        self.serial_port = None
        self.port = port if port is not None else self.find_teensy_port()
        if self.port:
            try:
                self.serial_port = serial.Serial(self.port, baud_rate, timeout=1)
                print(f"Connected to {self.port}")
            except serial.SerialException as e:
                raise Exception(f"Failed to open serial port: {e}")
        else:
            raise Exception("Teensy device not found.")

    @staticmethod
    def find_teensy_port():
        """Attempt to find the port where the Teensy is connected based on its description."""
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            # Adjust this condition based on your Teensy's description
            if "Teensy" in port.description or "USB Serial" in port.description:
                return port.device
        return None

    def set_global_parameters(self, frequency, duty_cycle, prf):
        """Send global ultrasound parameters to the Teensy."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        global_params = {"type": "global_params", "frequency": frequency, "duty_cycle": duty_cycle, "prf": prf}
        self.serial_port.write(json.dumps(global_params).encode())

    def program_channel(self, channel, phase, amplitude):
        """Program a specific channel with phase and amplitude settings."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        channel_params = {"type": "channel_params", "channel": channel, "phase": phase, "amplitude": amplitude}
        self.serial_port.write(json.dumps(channel_params).encode())

    def start_ultrasound(self, duration):
        """Start ultrasound emission for a given duration."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        start_message = {"type": "start", "duration": duration}
        self.serial_port.write(json.dumps(start_message).encode())

    def check_status(self):
        """Check and return the status from the Teensy."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        self.serial_port.write(json.dumps({"type": "status"}).encode())
        status = self.serial_port.readline().decode().strip()
        if status:
            return json.loads(status)
        return {"status": "No response"}

# Example usage code (if run as a standalone script)
if __name__ == "__main__":
    try:
        teensy = TeensyController()  # Attempt to auto-detect and connect
        # Example of setting global parameters, adjust as needed
        teensy.set_global_parameters(frequency=1e6, duty_cycle=50, prf=1000)
        print("Teensy initialized and global parameters set.")
    except Exception as e:
        print(str(e))
