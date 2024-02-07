import unittest
from unittest.mock import MagicMock, patch
from teensy_controller import TeensyController
from amplifier_controller_gui import AmplifierController

class TestTeensyController(unittest.TestCase):

    @patch('serial.Serial')
    def setUp(self, mock_serial):
        # Mock the serial port for TeensyController tests
        self.mock_serial = mock_serial
        self.teensy = TeensyController(port='COM_TEST')

    def test_set_global_parameters_teensy(self):
        # Test setting global parameters on the TeensyController
        self.teensy.set_global_parameters(frequency=1e6, duty_cycle=50, prf=1000)
        expected_message = '{"type": "global_params", "frequency": 1000000.0, "duty_cycle": 50, "prf": 1000}'
        self.mock_serial.return_value.write.assert_called_with(expected_message.encode())

    # Add other TeensyController tests here...

class TestAmplifierControllerGUI(unittest.TestCase):

    def setUp(self):
        self.root = MagicMock()  # Mock the Tk root window
        self.teensy_controller_mock = MagicMock()  # Mock the TeensyController
        
        # Patch the TeensyController within AmplifierController to use the mock
        with patch('amplifier_controller_gui.TeensyController', return_value=self.teensy_controller_mock):
            self.app = AmplifierController(self.root)

    def test_set_global_parameters_gui(self):
        # Simulate GUI interactions and test global parameter settings
        self.app.update_frequency_entry.delete(0, 'end')
        self.app.update_frequency_entry.insert(0, "1e6")
        self.app.update_duty_cycle_entry.delete(0, 'end')
        self.app.update_duty_cycle_entry.insert(0, "50")
        self.app.update_prf_entry.delete(0, 'end')
        self.app.update_prf_entry.insert(0, "1000")
        
        self.app.send_controls()  # Trigger the method that sends the updated values
        
        # Verify that the TeensyController's method was called with expected arguments
        self.teensy_controller_mock.set_global_parameters.assert_called_once_with(frequency=1e6, duty_cycle=50, prf=1000)

    # Add other GUI tests here...

if __name__ == '__main__':
    unittest.main()
