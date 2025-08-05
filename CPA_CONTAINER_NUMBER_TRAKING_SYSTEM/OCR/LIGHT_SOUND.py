import serial  # Serial imported for Serial communication
import datetime
from datetime import datetime as dt
import time


def getSoundLight(status):
    Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    arduinoUnoSerial = serial.Serial('com10', 9600)
    print(Today + "    CONT STATUS = " + repr(status))

    try:
        # arduinoUnoSerial = serial.Serial('com', 9600)
        if (status == 1):

            # Create Serial port object called ArduinoUnoSerialData time.sleep(2)                                                             #wait for 2 secounds for the communication to get established
            # print(arduinoUnoSerial.readline())  # read the serial data and print it as line
            # print("You have new message from Arduino")

            arduinoUnoSerial.write(b'1')  # send 1 to the arduino's Data code
            print(Today + "    GREEN LED ON")
            time.sleep(5)
            arduinoUnoSerial.write(b'0')
            print(Today + "    GREEN LED OFF")

        else:
            # Create Serial port object called ArduinoUnoSerialData time.sleep(2)                                                             #wait for 2 secounds for the communication to get established
            # print(arduinoUnoSerial.readline())  # read the serial data and print it as line
            # print("You have new message from Arduino")

            arduinoUnoSerial.write(b'2')  # send 1 to the arduino's Data code
            print(Today + "    RED LED ON")
            time.sleep(10)
            arduinoUnoSerial.write(b'0')
            print(Today + "    RED LED OFF")


    except serial.serialutil.SerialException:
        arduinoUnoSerial.close()
        arduinoUnoSerial.open()

    arduinoUnoSerial.close()
