# Scream-Operated Door 🚪🔊

### Overview
This project was created for the Terrible Ideas Hackathon, where it won 1st place. The "Scream-Operated Door" uses audio input to detect pitch from the laptop microphone and control a servo motor. Scream at a high pitch to open the door and scream at a low pitch to close the door.

### Features
- Detects audio frequency from a laptop microphone.
- Controls a servo motor based on high and low-pitched frequencies.
- Built with fun and creative problem-solving in mind!

### Technologies Used
- Python
- Audio processing libraries (e.g., `pyaudio`)
- Servo motor control (e.g., with `RPi.GPIO` if using a Raspberry Pi)

### How It Works
1. The microphone captures audio input.
2. The program analyzes the audio frequency.
3. If the frequency is above a certain threshold, the door opens.
4. If the frequency is below a different threshold, the door closes.
