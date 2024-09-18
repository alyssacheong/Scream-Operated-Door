import aubio
import numpy as np
import pyaudio

import time
import argparse

import queue

import music21 

parser = argparse.ArgumentParser()
parser.add_argument("-input", required=False, type=int, help="Audio Input Device")
args = parser.parse_args()

if not (args.input) and args.input != 0:
    print("No input device specified. Printing list of input devices now: ")
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print("Device number (%i): %s" % (i, p.get_device_info_by_index(i).get('name')))
    print("Run this program with -input 1, or the number of the input you'd like to use.")
    exit()

# PyAudio object.
p = pyaudio.PyAudio()

# Open stream.
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, input=True, input_device_index=0, frames_per_buffer=4096)
time.sleep(1)

# Aubio's pitch detection.
pDetection = aubio.pitch("default", 4096, 4096//4, 44100)
# Set unit.
pDetection.set_unit("Hz")
pDetection.set_tolerance(0.3)
pDetection.set_silence(-40)

q = queue.Queue()

def get_current_note(volume_thresh=3, printOut=False):
    """Returns the Note Currently Played on the q object when audio is present
    
    Keyword arguments:

    volume_thresh -- the volume threshold for input. defaults to 0.01
    printOut -- whether or not to print to the terminal. defaults to False
    """
    current_pitch = music21.pitch.Pitch()

    while True:

        data = stream.read(1024, exception_on_overflow=False)
        samples = np.frombuffer(data,
                                dtype=aubio.float_type)

        pitch = pDetection(samples)[0]
    
        # Compute the energy (volume) of the
        # current frame.
        volume = np.sum(samples**2)/len(samples) * 100

        if pitch and volume > volume_thresh:  # adjust with your mic!
            current_pitch.frequency = pitch
        else:
            continue
        
        if printOut:
            print(volume)
        else:
            q.put({'Frequency': current_pitch.frequency, 'Volume': volume})

if __name__ == '__main__':
    get_current_note(volume_thresh=3, printOut=True)