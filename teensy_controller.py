import serial
import serial.tools.list_ports
import json

class TeensyController:
    def __init__(self, port=None, baud_rate=115200):
        self.serial_port = None
        self.port = port if port is not None else self.find_teensy_port()
        self.initialized_parameters = {}  # For storing initialized parameters
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
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
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
    
    def stop_ultrasound(self):
        """Send a stop command to the Teensy."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        stop_message = {"type": "stop"}
        self.serial_port.write(json.dumps(stop_message).encode())

    def store_initialized_parameters(self, channel, phase, amplitude):
        """Store parameters for a specific channel without sending them to the Teensy."""
        self.initialized_parameters[channel] = {"phase": phase, "amplitude": amplitude}

    def send_stored_parameters(self):
        """Send all stored (initialized) parameters to the Teensy."""
        for channel, params in self.initialized_parameters.items():
            self.program_channel(channel, params["phase"], params["amplitude"])
        self.initialized_parameters.clear()  # Clear after sending

if __name__ == "__main__":
    try:
        teensy = TeensyController()  # Attempt to auto-detect and connect
        # Example of storing and then sending parameters
        teensy.store_initialized_parameters(channel=1, phase=90, amplitude=50)
        print("Parameters stored.")
        teensy.send_stored_parameters()
        print("Stored parameters sent.")
    except Exception as e:
        print(str(e))