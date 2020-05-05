"""move_with_voice_instructions controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import speech_recognition as sr
import threading
import time


r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

CommandSet = []

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
MaxSpeed = 6.28

lmotor = robot.getMotor('left wheel motor')
rmotor = robot.getMotor('right wheel motor')

lmotor.setPosition(0)
rmotor.setPosition(0)

lp = 0
rp = 0


if __name__ == "__main__":

    print("Starting thread!")

    print("Start!")

    respond = ""
    while(len(CommandSet)==0):
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            respond = r.recognize_google(audio)
        except:
            pass

        print(respond)

        for i in respond.split(' '):
            if (i == "ahead") | (i == "forward"):
                CommandSet.append("GoAhead")
            elif(i == "left"):
                CommandSet.append("TurnLeft")
            elif(i == "right"):
                CommandSet.append("TurnRight")

    CommandSet.append("TurnLeft")
    CommandSet.append("TurnLeft")
    CommandSet.append("GoAhead")
    CommandSet.append("TurnLeft")
    CommandSet.append("GoAhead")
    CommandSet.append("TurnRight")
    CommandSet.append("GoAhead")
    CommandSet.append("TurnLeft")
    CommandSet.append("GoAhead")

    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    t = 0
    while robot.step(timestep) != -1:
        # Read the sensors:
        # Enter here functions to read sensor data, like:
        #  val = ds.getValue()

        # Process sensor data here.

        # Enter here functions to send actuator commands, like:
        t += 1
        if(t % 240 == 0):
            if(len(CommandSet) != 0):
                command = CommandSet.pop(0)
                #print(command)
                if(command == "TurnLeft"):
                    print("Turning Left")
                    lp -= 10
                    rp += 10

                elif(command == "TurnRight"):
                    print("Turning Right")
                    lp += 10
                    rp -= 10
                elif(command == "GoAhead"):
                    print("Going Ahead")
                    lp += 40
                    rp += 40

        lmotor.setPosition(lp)
        rmotor.setPosition(rp)

        #  motor.setPosition(10.0)
        pass

    # Enter here exit cleanup code.
