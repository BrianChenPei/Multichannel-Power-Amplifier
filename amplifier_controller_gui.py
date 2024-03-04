import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports

class TeensyController:
    def __init__(self, port):
        self.port = port
        print(f"Connected to {port}")

    def program_channel(self, channel, signal_parameters):
        print(f"Channel {channel} programmed with {signal_parameters}")
    
    def stop_ultrasound(self):
        """Send a stop command to the Teensy."""
        if not self.serial_port:
            raise Exception("Serial port not initialized.")
        stop_message = {"type": "stop"}
        self.serial_port.write(json.dumps(stop_message).encode())

class AmplifierController:
    def __init__(self, master):
        self.master = master
        master.title("Amplifier Controller")
        
        self.configure_styles()
        
        self.setup_port_selection_gui(master)
        self.setup_global_parameters_gui(master)
        self.setup_channel_parameters_gui(master)
        #self.setup_send_controls_gui(master)
        self.setup_system_status_gui(master)
        self.setup_stop_button_gui(master)
        self.setup_mega_selection_gui(master)
        
        self.teensy_controller = None
        self.try_connect_teensy()

        # Store for initialized but not yet sent channel parameters
        self.initialized_parameters = {}

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#85C1E9")
        style.configure("TLabel", background="#85C1E9", foreground="black", font=("Times New Roman", 12, "bold"))
        style.configure("TEntry", background="#AED6F1", foreground="black", font=("Times New Roman", 11))
        style.configure("TCombobox", background="#7FB3D5", foreground="black", font=("Times New Roman", 11))
        style.configure("TButton", font=("Times New Roman", 12, "bold"), background="#52BE80", foreground="black")

    def setup_port_selection_gui(self, master):
        self.port_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.port_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.port_label = ttk.Label(self.port_frame, text="Select Port:", style="TLabel")
        self.port_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.port_frame, textvariable=self.port_var, values=self.get_serial_ports(), state="readonly", style="TCombobox")
        self.port_dropdown.grid(row=0, column=1, pady=(0, 20), sticky="ew")

        self.refresh_button = ttk.Button(self.port_frame, text="Refresh Ports", command=self.refresh_ports, style="TButton")
        self.refresh_button.grid(row=0, column=2, padx=5, pady=(0, 20))

        self.connect_button = ttk.Button(self.port_frame, text="Connect", command=self.try_connect_teensy, style="TButton")
        self.connect_button.grid(row=0, column=3, padx=5, pady=(0, 20))

    def setup_global_parameters_gui(self, master):
        self.global_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.global_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        global_parameters = [("Ultrasound Frequency (kHz):", "kHz"), ("Duty Cycle (%):", "%"), ("PRF (Hz):", "Hz")]
        for i, (text, unit) in enumerate(global_parameters):
            label = ttk.Label(self.global_frame, text=text, style="TLabel")
            label.grid(row=i, column=0, pady=(0, 10), sticky="w")
            entry = ttk.Entry(self.global_frame, style="TEntry")
            entry.grid(row=i, column=1, pady=(0, 20), sticky="ew")

    def setup_mega_selection_gui(self, master):
        self.mega_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.mega_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.mega_label = ttk.Label(self.mega_frame, text="Select Mega 2560:", style="TLabel")
        self.mega_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.mega_var = tk.StringVar()
        self.mega_dropdown = ttk.Combobox(self.mega_frame, textvariable=self.mega_var, values=list(range(1, 9)), state="readonly", style="TCombobox")
        self.mega_dropdown.grid(row=0, column=1, pady=(0, 20), sticky="ew")

    def setup_channel_parameters_gui(self, master):
        self.channel_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.channel_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.channel_label = ttk.Label(self.channel_frame, text="Channel:", style="TLabel")
        self.channel_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.channel_var = tk.StringVar()
        self.channel_dropdown = ttk.Combobox(self.channel_frame, textvariable=self.channel_var, values=list(range(1, 22)), state="readonly", style="TCombobox")
        self.channel_dropdown.grid(row=1, column=0, pady=(0, 20), sticky="ew")

        last_row_used_for_parameters = 3  # Adjust this based on your actual last row used for channel parameters

        self.signal_parameter_widgets = []
        for signal_number in range(1, 4):  # Assuming 3 signals per channel
            amplitude_label = ttk.Label(self.channel_frame, text=f"Signal {signal_number} Amplitude (mA):", style="TLabel")
            amplitude_label.grid(row=signal_number, column=1, pady=(0, 10), sticky="w")
            amplitude_entry = ttk.Entry(self.channel_frame, style="TEntry")
            amplitude_entry.grid(row=signal_number, column=2, pady=(0, 20), sticky="ew")

            phase_label = ttk.Label(self.channel_frame, text=f"Signal {signal_number} Phase (degrees):", style="TLabel")
            phase_label.grid(row=signal_number, column=3, pady=(0, 10), sticky="w")
            phase_entry = ttk.Entry(self.channel_frame, style="TEntry")
            phase_entry.grid(row=signal_number, column=4, pady=(0, 20), sticky="ew")

            self.signal_parameter_widgets.append((amplitude_entry, phase_entry))

        # Place the "Initialize Parameters" button
        self.initialize_button = ttk.Button(self.channel_frame, text="Initialize Parameters", command=self.initialize_parameters, style="TButton")
        self.initialize_button.grid(row=last_row_used_for_parameters + 1, column=0, pady=(10, 0), sticky="ew")

        # Place the "Send Initialized Controls" button next to the "Initialize Parameters" button
        self.send_initialized_button = ttk.Button(self.channel_frame, text="Send Initialized Controls", command=self.send_initialized_controls, style="TButton")
        # Place it in the same row but the next column
        self.send_initialized_button.grid(row=last_row_used_for_parameters + 1, column=1, pady=(10, 0), sticky="ew")


    def send_channel_parameters(self, mega_id, channel, phase, amplitude):
        try:
            if self.teensy_controller:  # Consider renaming this attribute to something more generic
                self.teensy_controller.program_channel(mega_id, channel, phase, amplitude)
                self.update_system_status(f"Mega {mega_id} Channel {channel} programmed.")
            else:
                self.update_system_status("Controller not connected.")
        except Exception as e:
            self.update_system_status(f"Failed to program channel: {e}")

    def setup_system_status_gui(self, master):
        self.status_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.status_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.system_status_label = ttk.Label(self.status_frame, text="System Status:", style="TLabel")
        self.system_status_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.system_status_text = tk.Text(self.status_frame, height=5, width=75, wrap="word", font=("Times New Roman", 11))
        self.system_status_text.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        self.system_status_text.insert(tk.END, "System is OK.")
        self.system_status_text.configure(state='disabled')

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        self.port_dropdown['values'] = self.get_serial_ports()

    def try_connect_teensy(self):
        selected_port = self.port_var.get()
        try:
            self.teensy_controller = TeensyController(selected_port)
            messagebox.showinfo("Connection Status", f"Successfully connected to {selected_port}")
            self.update_system_status("Connected to Teensy.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.update_system_status(f"Connection failed: {e}")

    def initialize_parameters(self):
        channel = self.channel_var.get()
        if not channel:
            messagebox.showerror("Initialization Error", "No channel selected.")
            return

        parameters = []
        for amplitude_entry, phase_entry in self.signal_parameter_widgets:
            amplitude = amplitude_entry.get()
            phase = phase_entry.get()
            parameters.append((amplitude, phase))

        self.initialized_parameters[channel] = parameters
        self.update_system_status(f"Parameters initialized for channel {channel} but not sent.")

    def send_initialized_controls(self):
        if not self.teensy_controller:
            messagebox.showerror("Operation Error", "Not connected to Teensy.")
            return

        for channel, parameters in self.initialized_parameters.items():
            self.teensy_controller.program_channel(channel, parameters)
            self.update_system_status(f"Sent initialized parameters to channel {channel}.")

        self.initialized_parameters.clear()

    def update_system_status(self, message):
        self.system_status_text.configure(state='normal')
        self.system_status_text.insert(tk.END, message + "\n")
        self.system_status_text.see(tk.END)
        self.system_status_text.configure(state='disabled')

    def setup_stop_button_gui(self, master):
        self.stop_button_frame = ttk.Frame(master, style="TFrame")
        self.stop_button_frame.grid(row=5, column=0, pady=10, sticky="ew")
        
        self.stop_button = ttk.Button(self.stop_button_frame, text="Stop", command=self.send_stop_command, style="TButton")
        self.stop_button.pack(expand=True)

    def send_stop_command(self):
        """Send a stop command to the Teensy."""
        try:
            if self.teensy_controller:
                self.teensy_controller.stop_ultrasound()
                self.update_system_status("Stop command sent.")
            else:
                self.update_system_status("Teensy not connected.")
        except Exception as e:
            self.update_system_status(f"Failed to send stop command: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AmplifierController(root)
    root.mainloop()
