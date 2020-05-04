import speech_recognition as sr
from controller import Robot
import threading
import time

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

CommandSet=[]

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
MaxSpeed=6.28

lmotor=robot.getMotor('left wheel motor')
rmotor=robot.getMotor('right wheel motor')

class MoveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while(True):
            if(len(CommandSet)!=0):
                command=CommandSet.pop(0)
                print(command)
                if(command=="TurnLeft"):
                    self.turnleft()
                elif(command=="TurnRight"):
                    self.turnright()
                elif(command=="GoAhead"):
                    self.goahead()
    
    def turnleft(self):
        print("left!")
        rmotor.setVelocity(MaxSpeed)
        time.sleep(1.5)
        rmotor.setVelocity(0)

    def turnright(self):
        print("right!")
        lmotor.setVelocity(MaxSpeed)
        time.sleep(1.5)
        lmotor.setVelocity(0)
    
    def goahead(self):
        print("ahead!")
        lmotor.setVelocity(MaxSpeed)
        rmotor.setVelocity(MaxSpeed)
        time.sleep(7.5)
        lmotor.setVelocity(0)
        rmotor.setVelocity(0)


if __name__ == "__main__":
    move_thread=MoveThread()
    move_thread.turnleft()
    time.sleep(1)
    move_thread.goahead()
    time.sleep(1)
    move_thread.turnright()
    time.sleep(1)
    move_thread.goahead()
