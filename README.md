# Multichannel Power Amplifier

The Multichannel Power Amplifier project is designed to control and manage multiple channels of an amplifier for ultrasound applications. It consists of two primary components: the Teensy microcontroller code (`teensy_controller.py`) and a graphical user interface (`amplifier_controller_gui.py`) for easy interaction and control.

## Features

- **Automatic Port Detection:** Automatically detects and connects to the Teensy device.
- **Channel Programming:** Allows for the programming of each channel with specific signal parameters.
- **Global Parameters Configuration:** Users can set global parameters such as ultrasound frequency, duty cycle, and pulse repetition frequency (PRF).
- **GUI for Easy Management:** A user-friendly graphical interface to manage connections, parameters, and controls.

## Installation

To get started with the Multichannel Power Amplifier, clone this repository to your local machine using:

git clone https://github.com/yourusername/Multichannel-Power-Amplifier.git


### Requirements

- Python 3.x
- `pyserial` for serial communication
- `tkinter` for the GUI

You can install the required packages using pip:

pip install pyserial tk


## Usage

### Teensy Controller

The `teensy_controller.py` script is responsible for the direct interaction with the Teensy microcontroller. It handles the connection, signal parameter programming, global parameter settings, and stopping the ultrasound.

### Amplifier Controller GUI

The `amplifier_controller_gui.py` script provides a graphical user interface for controlling the amplifier. It allows users to:

- Connect to the Teensy device.
- Set global ultrasound parameters.
- Program each channel with specific signal parameters.
- Monitor the system status.
- Stop the ultrasound output.

To run the GUI, execute:

python amplifier_controller_gui.py


## Contributing

Contributions to the Multichannel Power Amplifier project are welcome. Please ensure to follow the coding standards and submit pull requests for review.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
