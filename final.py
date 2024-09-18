from threading import Thread
from get_pitch import get_current_note, q
import time
from analysis import TargetAudioDetector, ZigZagTracker
from motor import connect_to_serial, list_serial_ports, ServoMotor
import random





PORT = "/dev/cu.usbserial-11240"

ff = lambda: get_current_note(volume_thresh=35)
t = Thread(target=ff)
t.daemon = True
t.start()
finished = False


#
## OPTIONS
#

ZIGZAG_ON = False
PUNISHMENT_ON = True


# FREQUENCIES

# 0: Easy Man
# 1: Medium Man
# 2: Hard Man

# 3: Easy Woman
# 4: Medium Woman
# 5: Hard Woman

DIFFICULTIES = [
    [120, 500], 
    [200, 700], 
    [85, 800],

    [300, 800],
    [300, 900],
    [160, 1000]]

DIFFICULTY_INDEX = 1

LOW_FREQ = DIFFICULTIES[DIFFICULTY_INDEX][0]
HIGH_FREQ = DIFFICULTIES[DIFFICULTY_INDEX][1]

ZIGZAG_LOW = 125
ZIGZAG_HIGH = 450

# DEGREES
PUNISHMENT_DEGREE_DEFAULT = 90
PUNISHMENT_DEGREE_1 = 0
PUNISHMENT_DEGREE_2 = 180

OPEN_DOOR_DEGREE = 50
CLOSED_DOOR_DEGREE = 150

# PUNISHMENT COOLDOWN TIME
COUNTDOWN_TIME = 8

MIN_VOLUME_START = 80

def print_message():
    print(f"Low: {LOW_FREQ}")
    print(f"High: {HIGH_FREQ}")

    # print(f"Low Zigzag: {ZIGZAG_LOW}")
    # print(f"High Zigzag: {ZIGZAG_HIGH}")

analyze_n_samples = 10
detector_close = TargetAudioDetector(
    target = LOW_FREQ,
    tolerance = 10,
    min_valid_counts = 5,
)

detector_open = TargetAudioDetector(
    target = HIGH_FREQ,
    tolerance = 10,
    min_valid_counts = 5,
)

zz_detector = ZigZagTracker(
    zz_low=ZIGZAG_LOW,
    zz_high=ZIGZAG_HIGH,
    tolerance=20,
    n_jumps_to_stop=3,
    min_valid_counts=5,
)

door_motor = ServoMotor(prefix='t',angle_len=3)
punish_motor = ServoMotor(prefix='p',angle_len=3)

detectors = [detector_open, detector_close]
freq_data = []

print(list_serial_ports())

serial = connect_to_serial(PORT,baud_rate=9600)


started = False


print_message()

done_before = -1



door_motor.send_command(serial,angle=CLOSED_DOOR_DEGREE)
punish_motor.send_command(serial,angle=PUNISHMENT_DEGREE_DEFAULT)
# time.sleep(2)



print("READY TO TAKE MESSAGES")
paused = True

freqs = []
zz_freqs = []
total_time = time.time()
start_time = time.time()
while not(finished):
    # if time.time() - total_time > 30:
    #     break
    if not(paused):
        countdown_reached = time.time() - start_time
        if countdown_reached >= COUNTDOWN_TIME and PUNISHMENT_ON:
            # print("PUNISHED!!!")

            if done_before != -1:
                if done_before == 0:
                    punish_motor.send_command(serial, PUNISHMENT_DEGREE_2)
                else:
                    punish_motor.send_command(serial, PUNISHMENT_DEGREE_1)
            else:
                if random.randint(0,1):
                    done_before = 0
                    punish_motor.send_command(serial, PUNISHMENT_DEGREE_1)
                
                    

                else:
                    done_before = 1
                    punish_motor.send_command(serial, PUNISHMENT_DEGREE_2)

            time.sleep(6)
            punish_motor.send_command(serial, PUNISHMENT_DEGREE_DEFAULT)
            zz_freqs = []
            freqs = []

            paused = True

    if q.empty():
        continue
    b = q.get() 

    if paused:
        triggered_volume = b["Volume"] >= MIN_VOLUME_START
        # print(b["Frequency"], b["Volume"], paused, triggered_volume)

        if triggered_volume:
            start_time = time.time()
            paused = False
            print("START SCREAMING!!!!")
    else:
        print(int(b["Frequency"]))
        freq_data.append(b['Frequency'])
        zz_freqs.append(b['Frequency'])
        _, _, b = detector_open.analyze_data(freq_data)
        _, _, b2 = detector_close.analyze_data(freq_data)
        b3 = zz_detector.analyze_data(zz_freqs)

        if b:
            print('Open door!')
            paused = True
            freq_data = []

            door_motor.send_command(serial,angle=OPEN_DOOR_DEGREE)

            time.sleep(3)
        elif b2:
            print('Close door!')
            paused = True
            freq_data = []

            door_motor.send_command(serial,angle=CLOSED_DOOR_DEGREE)

            time.sleep(3)
        elif b3 and ZIGZAG_ON:
            print('ZZ count up!', zz_detector.zz_counts)
            time.sleep(1)
            zz_freqs = []
            if zz_detector.is_zz_triggered():
                print('ZZ prank!')
                paused = True
                zz_freqs = []

                # door_motor.send_command(serial,angle=90)

                time.sleep(3)


import matplotlib.pyplot as plt
fig, ax = plt.subplots(1)
ax.plot(freq_data)
plt.show()

    # if paused:
    #     continue


    # if (time.time() - start_time >= 10) and started:
    #     print("PUNISHED!!!")
    #     started = False
    #     start_time = time.time()
    # if not(q.empty()):
    #     b = q.get()  
    #     if (b["Volume"] >= min_volume_start) and not(started):
    #         start_time = time.time()
    #         print("Triggered by", b["Volume"])
    #         started = True
    #     if started:
    #         freq_data.append(float(b['Frequency'])) 
    #         print(b["Frequency"], b["Volume"])

    #     # if len(freq_data) >= 100:
    #     #     finished = True



print("STOPPED")
