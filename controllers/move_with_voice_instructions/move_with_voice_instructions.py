"""move_with_voice_instructions controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import speech_recognition as sr
import threading
import time
import numpy as np
import math
import random


r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

CommandSet = []

Input = []

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


def detect_running_type():
    respond = ""
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        respond = r.recognize_google(audio)
    except:
        pass

    print(respond)

    for i in respond.split(' '):
        if (i == "online") | (i == "optimizing"):
            return "Training"
        elif(i == "teaching") | (i == "learning") | (i == "running"):
            return "Running"


def wait_for_command(CommandSet, Input):
    print("Starting Recording!")

    respond = ""
    while(len(CommandSet) == 0):
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
            elif(i == "stop"):
                CommandSet.append("Stop")


def wait_for_command_once(CommandSet, Input):
    print("Starting Recording!")

    respond = ""
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
            Input.append(3)
        elif(i == "left"):
            Input.append(1)
        elif(i == "right"):
            Input.append(2)
        elif(i == "stop"):
            CommandSet.append("Stop")


def move_based_on_command_set(CommandSet, lp, rp):
    if(len(CommandSet) != 0):
        command = CommandSet.pop(0)
        # print(command)
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

    return lp, rp


def move_based_on_command_set_with_state_and_face(CommandSet, lp, rp, facing, current_state):

    W_ = {1: 3, 2: 1}
    N_ = {1: 4, 2: 2}
    E_ = {1: 1, 2: 3}
    S_ = {1: 2, 2: 4}
    Heading = {1: ("N", N_), 2: ("E", E_), 3: ("S", S_), 4: ("W", W_)}

    if(len(CommandSet) != 0):
        command = CommandSet.pop(0)
        # print(command)
        if(command == "TurnLeft"):
            print("Turning Left")
            lp -= 10
            rp += 10
            facing = Heading[facing][1][1]
        elif(command == "TurnRight"):
            print("Turning Right")
            lp += 10
            rp -= 10
            facing = Heading[facing][1][2]
        elif(command == "GoAhead"):
            print("Going Ahead")
            lp += 40
            rp += 40
            if(facing == 1):
                current_state = (current_state[0]-1, current_state[1])
            elif(facing == 2):
                current_state = (current_state[0], current_state[1]+1)
            elif(facing == 3):
                current_state = (current_state[0]+1, current_state[1])
            elif(facing == 4):
                current_state = (current_state[0], current_state[1]-1)

    return lp, rp, facing, current_state


def human_guide_learning(Input):

    # Learning Parameters
    W_ = {1: 3, 2: 1}
    N_ = {1: 4, 2: 2}
    E_ = {1: 1, 2: 3}
    S_ = {1: 2, 2: 4}
    Heading = {1: ("N", N_), 2: ("E", E_), 3: ("S", S_), 4: ("W", W_)}

    Action = {1: "left", 2: "right", 3: "ahead"}

    Start_Heading = 3

    Start_State = (2, 0)
    Target_State = (3, 3)

    face = Start_Heading

    Not_reach_reward = -1
    Reach_reward = 100

    RealMap = [[[1, 0, 0, 1], [1, 1, 0, 0], [1, 0, 0, 1], [1, 1, 0, 0]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [0, 1, 1, 0], [0, 1, 0, 1]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [1, 1, 0, 0], [0, 1, 0, 1]],
               [[0, 0, 1, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 1, 0]]]

    KnownMap = [[False for i in range(4)] for j in range(4)]

    Qtable = [[0 for i in range(4)] for j in range(16)]

    PS = [[0 for i in range(4)] for j in range(16)]

    S = []

    for s in Input:
        if s == 3:
            S.append(face)
        else:
            face = Heading[face][1][s]

    state = Start_State
    KnownMap[state[0]][state[1]] = True
    reward = 0

    while(len(S) != 0):
        action = S.pop(0)
        PS[state[0]*4+state[1]+1][action-1] += 1

        # Perform Action
        if(action == 1):
            new_state = (state[0]-1, state[1])
        elif(action == 2):
            new_state = (state[0], state[1]+1)
        elif(action == 3):
            new_state = (state[0]+1, state[1])
        elif(action == 4):
            new_state = (state[0], state[1]-1)

        if(new_state == Target_State):
            print("Reach target!")
            reward += Reach_reward
        else:
            reward += Not_reach_reward

        Qtable[state[0]*4+state[1]+1][action-1] += reward

        state = new_state

        # Update Map
        KnownMap[state[0]][state[1]] = True

    np.save("PS.npy", PS)
    np.save("qt.npy", Qtable)


def offline_optimizing():
    # Learning Parameters
    W_ = {1: 3, 2: 1}
    N_ = {1: 4, 2: 2}
    E_ = {1: 1, 2: 3}
    S_ = {1: 2, 2: 4}
    Heading = {1: ("N", N_), 2: ("E", E_), 3: ("S", S_), 4: ("W", W_)}

    Action = {1: "left", 2: "right", 3: "ahead"}

    Start_Heading = 3

    Start_State = (2, 0)
    Target_State = (3, 3)

    face = Start_Heading

    Not_reach_reward = -1
    Reach_reward = 100

    RealMap = [[[1, 0, 0, 1], [1, 1, 0, 0], [1, 0, 0, 1], [1, 1, 0, 0]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [0, 1, 1, 0], [0, 1, 0, 1]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [1, 1, 0, 0], [0, 1, 0, 1]],
               [[0, 0, 1, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 1, 0]]]

    Offline_start_state = Start_State
    offstate = Offline_start_state

    t = 3
    e = math.e
    B = 0.8

    PS = np.load("PS.npy").tolist()
    Qtable = np.load("qt.npy").tolist()

    for n in range(3):
        reward = 0
        offstate = Offline_start_state
        while(offstate != Target_State):
            print(offstate)

            move_choice = []

            wall = RealMap[offstate[0]][offstate[1]]
            print(wall)
            for j in range(len(wall)):
                if wall[j] == 0:
                    move_choice.append(j)

            print(move_choice)

            pq_sum = 0
            p_set = {}

            for k in move_choice:
                pq_sum += math.pow(e, Qtable[offstate[0]*4+offstate[1]+1][k]/t)

            for k in move_choice:
                pq_k = math.pow(
                    e, Qtable[offstate[0]*4+offstate[1]+1][k]/t)/pq_sum
                pb_k = math.pow(B, PS[offstate[0]*4+offstate[1]+1][k])/(math.pow(B, PS[offstate[0]*4+offstate[1]+1][k])
                                                                        + math.pow(1-B, PS[offstate[0]*4+offstate[1]+1][k]))
                p_set.update({k: pq_k*pb_k})

            p_sum = sum(p_set.values())

            for k in move_choice:
                p_set.update({k: p_set[k]/p_sum})

            r = random.random()*sum(p_set.values())
            for i in range(len(p_set)):
                if list(p_set.values())[i] >= r:
                    break
                else:
                    r -= list(p_set.values())[i]

            next_action = list(p_set.keys())[i]+1

            # Perform Action
            if(next_action == 1):
                new_state = (offstate[0]-1, offstate[1])
            elif(next_action == 2):
                new_state = (offstate[0], offstate[1]+1)
            elif(next_action == 3):
                new_state = (offstate[0]+1, offstate[1])
            elif(next_action == 4):
                new_state = (offstate[0], offstate[1]-1)

            if(new_state == Target_State):
                reward += Reach_reward
            else:
                reward += Not_reach_reward

            Qtable[offstate[0]*4+offstate[1]+1][next_action-1] += reward

            offstate = new_state

    np.save("PS.npy", PS)
    np.save("qt.npy", Qtable)


def get_next_step_from_online(CommandSet, Input, onstate, facing):
    # Learning Parameters
    W_ = {1: 3, 2: 1}
    N_ = {1: 4, 2: 2}
    E_ = {1: 1, 2: 3}
    S_ = {1: 2, 2: 4}
    Heading = {1: ("N", N_), 2: ("E", E_), 3: ("S", S_), 4: ("W", W_)}

    Action = {1: "left", 2: "right", 3: "ahead"}

    Start_Heading = 3

    Start_State = (2, 0)
    Target_State = (3, 3)

    Not_reach_reward = -1
    Reach_reward = 100

    RealMap = [[[1, 0, 0, 1], [1, 1, 0, 0], [1, 0, 0, 1], [1, 1, 0, 0]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [0, 1, 1, 0], [0, 1, 0, 1]],
               [[0, 1, 0, 1], [0, 0, 0, 1], [1, 1, 0, 0], [0, 1, 0, 1]],
               [[0, 0, 1, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 1, 0]]]

    t = 3
    e = math.e
    B = 0.8

    PS = np.load("PS.npy").tolist()
    Qtable = np.load("qt.npy").tolist()

    reward = 0

    S = []
    face = facing

    for s in Input:
        if s == 3:
            S.append(face)
        else:
            face = Heading[face][1][s]

    if len(S) != 0:
        action = S.pop(0)
        PS[onstate[0]*4+onstate[1]+1][action-1] += 1
    while(len(Input) != 0):
        i = Input.pop(0)
        if i == 3:
            break

    else:
        move_choice = []

        wall = RealMap[onstate[0]][onstate[1]]
        print(wall)
        for j in range(len(wall)):
            if wall[j] == 0:
                move_choice.append(j)

        print(move_choice)

        pq_sum = 0
        p_set = {}

        for k in move_choice:
            pq_sum += math.pow(e, Qtable[onstate[0]*4+onstate[1]+1][k]/t)

        for k in move_choice:
            pq_k = math.pow(e, Qtable[onstate[0]*4+onstate[1]+1][k]/t)/pq_sum
            pb_k = math.pow(B, PS[onstate[0]*4+onstate[1]+1][k])/(math.pow(B, PS[onstate[0]*4+onstate[1]+1][k])
                                                                  + math.pow(1-B, PS[onstate[0]*4+onstate[1]+1][k]))
            p_set.update({k: pq_k*pb_k})

        p_sum = sum(p_set.values())

        for k in move_choice:
            p_set.update({k: p_set[k]/p_sum})

        r = random.random()*sum(p_set.values())
        for i in range(len(p_set)):
            if list(p_set.values())[i] >= r:
                break
            else:
                r -= list(p_set.values())[i]

        action = list(p_set.keys())[i]+1

    # Perform Action
    if(action == 1):
        new_state = (onstate[0]-1, onstate[1])
    elif(action == 2):
        new_state = (onstate[0], onstate[1]+1)
    elif(action == 3):
        new_state = (onstate[0]+1, onstate[1])
    elif(action == 4):
        new_state = (onstate[0], onstate[1]-1)

    if(new_state == Target_State):
        reward += 100
    else:
        reward -= 1

    print(action)
    print("new_state:", new_state)

    Qtable[onstate[0]*4+onstate[1]+1][action-1] += reward

    onstate = new_state

    return action, new_state


def update_command_set(CommandSet, action, facing):
    if(facing == 1):
        if(action == 1):
            CommandSet.append("GoAhead")
        elif(action == 2):
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 3):
            CommandSet.append("TurnRight")
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 4):
            CommandSet.append("TurnLeft")
            CommandSet.append("GoAhead")
    elif(facing == 2):
        if(action == 2):
            CommandSet.append("GoAhead")
        elif(action == 3):
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 4):
            CommandSet.append("TurnRight")
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 1):
            CommandSet.append("TurnLeft")
            CommandSet.append("GoAhead")
    elif(facing == 3):
        if(action == 3):
            CommandSet.append("GoAhead")
        elif(action == 4):
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 1):
            CommandSet.append("TurnRight")
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 2):
            CommandSet.append("TurnLeft")
            CommandSet.append("GoAhead")
    elif(facing == 4):
        if(action == 4):
            CommandSet.append("GoAhead")
        elif(action == 1):
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 2):
            CommandSet.append("TurnRight")
            CommandSet.append("TurnRight")
            CommandSet.append("GoAhead")
        elif(action == 3):
            CommandSet.append("TurnLeft")
            CommandSet.append("GoAhead")


if __name__ == "__main__":
    print("Please speak out the type of task")

    Type = detect_running_type()
    if(Type == "Running"):

        wait_for_command(CommandSet, Input)

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
                if(len(CommandSet) != 0):
                    if(CommandSet[0] != "Stop"):
                        lp, rp = move_based_on_command_set(CommandSet, lp, rp)
                    else:
                        break
                else:
                    wait_for_command(CommandSet, Input)

            lmotor.setPosition(lp)
            rmotor.setPosition(rp)

            #  motor.setPosition(10.0)
            pass

        # Enter here exit cleanup code.

        print("finish!")
        human_guide_learning(Input)
        print("PS and Qtable saved!")

        offline_optimizing()

    else:
        current_state = (2, 0)
        facing = 3
        t = 0
        while robot.step(timestep) != -1:
            # Read the sensors:
            # Enter here functions to read sensor data, like:
            #  val = ds.getValue()

            # Process sensor data here.

            # Enter here functions to send actuator commands, like:
            t += 1
            if(t % 240 == 0):

                if(len(Input) == 0) & (len(CommandSet) == 0):
                    wait_for_command_once(CommandSet, Input)

                if(len(CommandSet) != 0):

                    if(CommandSet[0] != "Stop"):
                        lp, rp, facing, current_state = move_based_on_command_set_with_state_and_face(
                            CommandSet, lp, rp, facing, current_state)
                    else:
                        break
                else:
                    action, new_state = get_next_step_from_online(
                        CommandSet, Input, current_state, facing)
                    print(action, new_state)
                    update_command_set(CommandSet, action, facing)
                    t += 200
                    print(CommandSet)

            lmotor.setPosition(lp)
            rmotor.setPosition(rp)

            #  motor.setPosition(10.0)
            pass

        # Enter here exit cleanup code.

        print("finish!")

        print("PS and Qtable saved!")

        offline_optimizing()
