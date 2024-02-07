import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from teensy_controller import TeensyController

class AmplifierController:
    def __init__(self, master):
        self.master = master
        master.title("Amplifier Controller")
        
        self.configure_styles()
        
        self.setup_port_selection_gui(master)
        self.setup_global_parameters_gui(master)
        self.setup_channel_parameters_gui(master)
        self.setup_send_controls_gui(master)
        self.setup_system_status_gui(master)
        
        self.teensy_controller = None
        # Placeholder for teensy_controller
        # self.try_connect_teensy()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#85C1E9")
        style.configure("TLabel", background="#85C1E9", foreground="black", font=("Times New Roman", 12, "bold"))
        style.configure("TEntry", background="#AED6F1", foreground="black", font=("Times New Roman", 11))
        style.configure("TCombobox", background="#7FB3D5", foreground="black", font=("Times New Roman", 11))
        style.configure("TText", background="#7FB3D5", foreground="black", font=("Times New Roman", 11))
        style.configure("TButton", font=("Times New Roman", 12, "bold"), background="#52BE80", foreground="black")

    def setup_port_selection_gui(self, master):
        self.port_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.port_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.port_label = ttk.Label(self.port_frame, text="Select Port:", foreground="black")
        self.port_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.port_frame, textvariable=self.port_var, values=self.get_serial_ports(), state="readonly")
        self.port_dropdown.grid(row=0, column=1, pady=(0, 20), sticky="ew")

        self.refresh_button = ttk.Button(self.port_frame, text="Refresh Ports", command=self.refresh_ports, style="TButton")
        self.refresh_button.grid(row=0, column=2, padx=5, pady=(0, 20))

        self.connect_button = ttk.Button(self.port_frame, text="Connect", command=self.try_connect_teensy, style="TButton")
        self.connect_button.grid(row=0, column=3, padx=5, pady=(0, 20))

    def setup_global_parameters_gui(self, master):
        self.global_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.global_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Global parameter labels and entries
        labels_texts_units = [("Ultrasound Frequency (kHz):", "kHz"), ("Duty Cycle (%):", "%"), ("PRF (Hz):", "Hz")]
        for i, (text, unit) in enumerate(labels_texts_units):
            label = ttk.Label(self.global_frame, text=text, foreground="black")
            label.grid(row=i*2, column=0, pady=(0, 10), sticky="w")
            entry = ttk.Entry(self.global_frame, style="TEntry")
            entry.grid(row=i*2+1, column=0, pady=(0, 20), sticky="ew")
            self.set_entry_text(entry, "Text Here")

            update_label = ttk.Label(self.global_frame, text=f"Update {text}", foreground="black")
            update_label.grid(row=i*2, column=1, pady=(0, 10), sticky="w")
            update_entry = ttk.Entry(self.global_frame, style="TEntry")
            update_entry.grid(row=i*2+1, column=1, pady=(0, 20), sticky="ew")
            self.set_Update_entry_text(update_entry, "New Values")

    def setup_channel_parameters_gui(self, master):
        self.channel_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.channel_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Existing channel-specific parameter labels and entries
        self.channel_label = ttk.Label(self.channel_frame, text="Channel:", foreground="black")
        self.channel_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.channel_var = tk.StringVar()
        self.channel_dropdown = ttk.Combobox(self.channel_frame, textvariable=self.channel_var, values=list(range(1, 22)), state="readonly")
        self.channel_dropdown.grid(row=1, column=0, pady=(0, 20), sticky="ew")

        labels_texts_units = [("Amplitude (mA):", "mA"), ("Phase (degrees):", "degrees")]
        for i, (text, unit) in enumerate(labels_texts_units):
            label = ttk.Label(self.channel_frame, text=text, foreground="black")
            label.grid(row=(i+1)*2, column=0, pady=(0, 10), sticky="w")
            entry = ttk.Entry(self.channel_frame, style="TEntry")
            entry.grid(row=(i+1)*2+1, column=0, pady=(0, 20), sticky="ew")
            self.set_entry_text(entry, "Text Here")

            update_label = ttk.Label(self.channel_frame, text=f"Update {text}", foreground="black")
            update_label.grid(row=(i+1)*2, column=1, pady=(0, 10), sticky="w")
            update_entry = ttk.Entry(self.channel_frame, style="TEntry")
            update_entry.grid(row=(i+1)*2+1, column=1, pady=(0, 20), sticky="ew")
            self.set_Update_entry_text(update_entry, "New Values")

        # New section for channel range updates
        self.channel_range_label = ttk.Label(self.channel_frame, text="Channel Range:", foreground="black")
        self.channel_range_label.grid(row=0, column=2, padx=(10, 0), pady=(0, 10), sticky="w")

        self.start_channel_var = tk.StringVar()
        self.end_channel_var = tk.StringVar()
        self.start_channel_dropdown = ttk.Combobox(self.channel_frame, textvariable=self.start_channel_var, values=list(range(1, 22)), state="readonly")
        self.end_channel_dropdown = ttk.Combobox(self.channel_frame, textvariable=self.end_channel_var, values=list(range(1, 22)), state="readonly")
        self.start_channel_dropdown.grid(row=1, column=2, padx=(10, 0), pady=(0, 20), sticky="ew")
        self.end_channel_dropdown.grid(row=1, column=3, padx=(10, 0), pady=(0, 20), sticky="ew")

        self.channel_range_label = ttk.Label(self.channel_frame, text="to", foreground="black")
        self.channel_range_label.grid(row=1, column=2, padx=(45, 2), pady=(0, 20), sticky="e")

        # Assuming the range applies the same amplitude and phase to all channels in the range
        range_labels_texts = ["Range Amplitude:", "Range Phase:"]
        for i, text in enumerate(range_labels_texts):
            range_label = ttk.Label(self.channel_frame, text=text, foreground="black")
            range_label.grid(row=(i+1)*2, column=2, columnspan=2, padx=(10, 0), pady=(0, 10), sticky="w")
            range_entry = ttk.Entry(self.channel_frame, style="TEntry")
            range_entry.grid(row=(i+1)*2+1, column=2, columnspan=2, padx=(10, 0), pady=(0, 20), sticky="ew")
            self.set_entry_text(range_entry, "New Values")

        # Button for applying the range update
        self.apply_range_button = ttk.Button(self.channel_frame, text="Apply to Range", style="TButton")
        self.apply_range_button.grid(row=6, column=2, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="ew")
        # You'll need to bind this button to a function that applies the parameters to the range of channels


    def setup_send_controls_gui(self, master):
        self.send_button_frame = ttk.Frame(master, style="TFrame")
        self.send_button_frame.grid(row=3, column=0, pady=20, sticky="ew")

        self.send_button = ttk.Button(self.send_button_frame, text="Send Controls", command=self.send_controls, style="TButton")
        self.send_button.pack(expand=False)

    def setup_system_status_gui(self, master):
        self.status_frame = ttk.Frame(master, padding="20", style="TFrame")
        self.status_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.system_status_label = ttk.Label(self.status_frame, text="System Status:", foreground="black")
        self.system_status_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.system_status_text = tk.Text(self.status_frame, height=5, width=75, wrap="word")
        self.system_status_text.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        self.system_status_text.insert(tk.END, "System is OK.")
        self.system_status_text.configure(state='disabled')

    def update_channel_range(self):
        """Updates the parameters for all channels within the selected range."""
        start_channel = int(self.start_channel_var.get())
        end_channel = int(self.end_channel_var.get())
        
        # Validate the channel range
        if start_channel >= end_channel:
            messagebox.showerror("Range Error", "Start channel must be less than end channel.")
            return
        
        # Example logic to update channels in range
        amplitude = self.range_amplitude_entry.get()  # Assuming you've stored the Entry widget as an attribute
        phase = self.range_phase_entry.get()  # Assuming you've stored the Entry widget as an attribute
        
        # You would iterate over the range and update each channel here
        for channel in range(start_channel, end_channel + 1):
            print(f"Updating channel {channel} with amplitude {amplitude} and phase {phase}")
            # Add actual logic to update the channel parameters
            
        messagebox.showinfo("Update Successful", f"Channels {start_channel} to {end_channel} updated.")

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        self.port_dropdown['values'] = self.get_serial_ports()

    def try_connect_teensy(self):
        """Attempt to connect to the Teensy device and handle exceptions."""
        selected_port = self.port_var.get()
        try:
            self.teensy_controller = TeensyController(selected_port)  # Pass the selected port to the controller
            messagebox.showinfo("Connection Status", f"Successfully connected to {selected_port}")
            self.update_system_status("Connected to Teensy.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.update_system_status(f"Connection failed: {e}")

    def set_entry_text(self, entry_widget, text):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)

    def set_Update_entry_text(self, entry_widget, text):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)

    def send_controls(self):
        """Send control settings to the Teensy based on the GUI inputs."""
        if not self.teensy_controller:
            messagebox.showerror("Operation Error", "Not connected to Teensy.")
            return
        
        # Example of sending a command, adapt according to your needs
        try:
            # Here, you'd gather the parameters from your GUI elements like self.frequency_entry.get()
            # and then call the appropriate method on teensy_controller, e.g.,
            # self.teensy_controller.set_global_parameters(frequency, duty_cycle, prf)
            # For demonstration, we'll just print to the console
            print("Sending controls to Teensy...")
            # Assuming we're sending a dummy command, replace this with actual control logic
            # self.teensy_controller.program_channel(channel, phase, amplitude)
            
            self.update_system_status("Controls sent successfully.")
        except Exception as e:
            messagebox.showerror("Sending Error", str(e))
            self.update_system_status(f"Error sending controls: {e}")

    def update_system_status(self, message):
        """Update the system status text box."""
        self.system_status_text.configure(state='normal')
        self.system_status_text.delete(1.0, tk.END)
        self.system_status_text.insert(tk.END, message)
        self.system_status_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = AmplifierController(root)
    root.mainloop()
