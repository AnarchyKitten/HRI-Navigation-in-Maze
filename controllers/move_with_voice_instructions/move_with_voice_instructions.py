"""move_with_voice_instructions controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import speech_recognition as sr
import threading
import time
import numpy as np


r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

CommandSet = []

Input=[]

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

# Learning Parameters
W_={1:3,2:1}
N_={1:4,2:2}
E_={1:1,2:3}
S_={1:2,2:4}
Heading={1:("N",N_),2:("E",E_),3:("S",S_),4:("W",W_)}

Action={1:"left",2:"right",3:"ahead"}

Start_Heading=3

Start_State=(2,0)
Target_State=(3,3)

face=Start_Heading

Not_reach_reward=-1
Reach_reward=100



def wait_for_command(CommandSet,Input):
    print("Starting Recording!")


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
                Input.append(3)
            elif(i == "left"):
                CommandSet.append("TurnLeft")
                Input.append(1)
            elif(i == "right"):
                CommandSet.append("TurnRight")
                Input.append(2)
            elif(i=="stop"):
                CommandSet.append("Stop")

def move_based_on_command_set(CommandSet,lp,rp):
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

    return lp,rp


if __name__ == "__main__":

    wait_for_command(CommandSet,Input)

    # Main loop:
    # - perform simulation steps until Webots is stopping the controller
    t = 200
    while robot.step(timestep) != -1:
        # Read the sensors:
        # Enter here functions to read sensor data, like:
        #  val = ds.getValue()

        # Process sensor data here.

        # Enter here functions to send actuator commands, like:
        t += 1
        if(t % 240 == 0):
            if(len(CommandSet)!=0):
                if(CommandSet[0]!="Stop"):
                    lp,rp=move_based_on_command_set(CommandSet,lp,rp)
                else:
                    break
            else:
                wait_for_command(CommandSet,Input)





        lmotor.setPosition(lp)
        rmotor.setPosition(rp)

        #  motor.setPosition(10.0)
        pass

    # Enter here exit cleanup code.

    print("finish!")
    S=[]

    for s in Input:
        if s==3:
            S.append(face)
        else:
            face=Heading[face][1][s]

    RealMap=[[[1,0,0,1],[1,1,0,0],[1,0,0,1],[1,1,0,0]],
            [[0,1,0,1],[0,0,0,1],[0,1,1,0],[0,1,0,1]],
            [[0,1,0,1],[0,0,0,1],[1,1,0,0],[0,1,0,1]],
            [[0,0,1,1],[0,1,1,0],[0,0,1,1],[0,1,1,0]]]

    KnownMap=[[False for i in range(4)] for j in range(4)]

    Qtable=[[0 for i in range(4)] for j in range(16)]

    PS=[[0 for i in range(4)] for j in range(16)]

    state=Start_State
    KnownMap[state[0]][state[1]]=True
    reward=0

    while(len(S)!=0):
        action=S.pop(0)
        PS[state[0]*4+state[1]+1][action-1]+=1
        
        #Perform Action
        if(action==1):
            new_state=(state[0]-1,state[1])
        elif(action==2):
            new_state=(state[0],state[1]+1)
        elif(action==3):
            new_state=(state[0]+1,state[1])
        elif(action==4):
            new_state=(state[0],state[1]-1)

        
        if(new_state==Target_State):
            print("Reach target!")
            reward+=100
        else:
            reward-=1
            
        Qtable[state[0]*4+state[1]+1][action-1]+=reward
        
        state=new_state

        #Update Map
        KnownMap[state[0]][state[1]]=True
    
    np.save("PS.npy",PS)
    np.save("qt.npy",Qtable)


