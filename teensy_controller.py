# File: teensy_controller.py
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
            raise Exception("Device not found.")

    @staticmethod
    def find_teensy_port():
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "Arduino" in port.description:  # Adjust based on your device description
                return port.device
        return None

    def program_channel(self, mega_id, channel, signal_params):
        """Program a specific channel with parameters for multiple signals."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        channel_params = {
            "type": "channel_params",
            "mega_id": mega_id,
            "channel": channel,
            "signals": signal_params  # List of signal parameters
        }
        self.serial_port.write(json.dumps(channel_params).encode())


    def set_global_parameters(self, frequency, duty_cycle, prf):
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        global_params = {
            "type": "global_params",
            "frequency": frequency,
            "duty_cycle": duty_cycle,
            "prf": prf
        }
        self.serial_port.write(json.dumps(global_params).encode())

    def stop_ultrasound(self):
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        stop_message = {"type": "stop"}
        self.serial_port.write(json.dumps(stop_message).encode())

    @staticmethod
    def get_serial_ports():
        return [port.device for port in serial.tools.list_ports.comports()]
