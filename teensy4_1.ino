#include <ArduinoJson.h>

void setup() {
  Serial.begin(115200); // Match the baud rate set in teensy_controller.py
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    StaticJsonDocument<256> doc; // Adjust size based on your needs
    DeserializationError error = deserializeJson(doc, input);

    if (error) {
      Serial.println("Error parsing JSON!");
      return;
    }

    const char* type = doc["type"]; // Get the command type

    if (strcmp(type, "global_params") == 0) {
      long frequency = doc["frequency"];
      int duty_cycle = doc["duty_cycle"];
      int prf = doc["prf"];
      // Apply global parameters...
      Serial.println("Global parameters set.");
    } 
    else if (strcmp(type, "channel_params") == 0) {
      int channel = doc["channel"];
      int phase = doc["phase"];
      int amplitude = doc["amplitude"];
      // Apply channel parameters...
      Serial.println("Channel parameters set.");
    }
    else if (strcmp(type, "channel_range_params") == 0) {
      int start_channel = doc["start_channel"];
      int end_channel = doc["end_channel"];
      int phase = doc["phase"];
      int amplitude = doc["amplitude"];
      
      // Apply range parameters to each channel in the range...
      for (int channel = start_channel; channel <= end_channel; channel++) {
        // Function to apply settings to each channel
        applyChannelSettings(channel, phase, amplitude);
      }
      
      Serial.println("Channel range parameters set.");
    }
    else if (strcmp(type, "start") == 0) {
      long duration = doc["duration"];
      // Start ultrasound...
      Serial.println("Ultrasound started.");
    }
    else if (strcmp(type, "status") == 0) {
      // Respond with status...
      Serial.println("{\"status\": \"OK\"}");
    }
    else {
      Serial.println("Unknown command.");
    }
  }
}

void applyChannelSettings(int channel, int phase, int amplitude) {
  // Dummy function to represent applying settings to a channel
  // Replace with actual code to adjust the channel settings
  Serial.print("Applying to channel ");
  Serial.print(channel);
  Serial.print(": Phase = ");
  Serial.print(phase);
  Serial.print(", Amplitude = ");
  Serial.println(amplitude);
}
