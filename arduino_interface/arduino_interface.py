import serial
import time

serport = "/dev/ttyACM0"

ser = serial.Serial(serport,115200)
ser.flushInput()

DEBUG = 1

def write_ser(data):
    ser.write(bytes(data, 'utf-8'))
    ser.flush()

def read_ser():
    return ser.readline().decode("utf-8")

def setup_connection():
    write_ser("A\n");
    write_ser("A\n");
    write_ser("A\n");
    write_ser("A\n");

    data = read_ser()
    arduinoRet = data.strip().split(' ')[-1]
    if DEBUG: print("Read from %s: --%s--"%(serport, data))

    if arduinoRet == 'A':
        return True
    else:
        return False

def send_actuate(lDir, lSpeed, rDir, rSpeed):
    outStr = "L:%c%d R:%c%d\n"%(lDir, lSpeed, rDir, rSpeed)
    write_ser(outStr)

if __name__ == '__main__':
    count = 0
    direction = 0
    if setup_connection():
        while True:
            count = (count + 1) % 10
            if count == 0:
                direction = (direction + 1) % 2
            lDir = '+' if direction == 1 else '-'
            rDir = '+' if direction == 0 else '-'

            send_actuate(lDir, 9-count, rDir, count)
            if DEBUG: time.sleep(.3)
            line = read_ser().strip()
            if DEBUG: print("Read from %s: %s"%(serport, line))
    else:
        print("Setup failed")
