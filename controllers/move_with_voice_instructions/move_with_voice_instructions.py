"""move_with_voice_instructions controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import speech_recognition as sr


r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getMotor('motorname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)



if __name__=="__main__":

    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    while robot.step(timestep) != -1:
        # Read the sensors:
        # Enter here functions to read sensor data, like:
        #  val = ds.getValue()

        # Process sensor data here.

        # Enter here functions to send actuator commands, like:

        respond = ""

        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        try:
            respond = r.recognize_google(audio)
        except:
            respond = ""

        if "left" in respond:
            print("Turning Left")
        elif "right" in respond:
            print("Turning Right")
        elif "ahead" in respond:
            print("go ahead")
        elif "forward" in respond:
            print("go ahead")

        #  motor.setPosition(10.0)
        pass

    # Enter here exit cleanup code.
