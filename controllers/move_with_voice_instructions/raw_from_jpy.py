import random
import math


#####Main#####

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

Input=[3,1,3,1,3,2,3,2,3,1,3]

Not_reach_reward=-1
Reach_reward=100

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
        reward+=100
    else:
        reward-=1
        
    Qtable[state[0]*4+state[1]+1][action-1]+=reward
    
    state=new_state

    #Update Map
    KnownMap[state[0]][state[1]]=True

#####Offline Optimizing#####

Offline_start_state=Start_State
offstate=Offline_start_state

t=3
e=math.e
B=0.8

for n in range(3):
    reward=0
    offstate=Offline_start_state
    while(offstate!=Target_State):
        print(offstate)

        move_choice=[]

        wall=RealMap[offstate[0]][offstate[1]]
        print(wall)
        for j in range(len(wall)):
            if wall[j]==0:
                move_choice.append(j)

        
        print(move_choice)

        pq_sum=0
        p_set={}


        for k in move_choice:
            pq_sum+=math.pow(e,Qtable[offstate[0]*4+offstate[1]+1][k]/t)

        for k in move_choice:
            pq_k=math.pow(e,Qtable[offstate[0]*4+offstate[1]+1][k]/t)/pq_sum
            pb_k=math.pow(B,PS[offstate[0]*4+offstate[1]+1][k])/(math.pow(B,PS[offstate[0]*4+offstate[1]+1][k])
            +math.pow(1-B,PS[offstate[0]*4+offstate[1]+1][k]))
            p_set.update({k:pq_k*pb_k})

        p_sum=sum(p_set.values())

        for k in move_choice:
            p_set.update({k:p_set[k]/p_sum})

        r=random.random()*sum(p_set.values())
        for i in range(len(p_set)):
            if list(p_set.values())[i]>=r:
                break
            else:
                r-=list(p_set.values())[i]

        next_action=list(p_set.keys())[i]+1

        #Perform Action
        if(next_action==1):
            new_state=(offstate[0]-1,offstate[1])
        elif(next_action==2):
            new_state=(offstate[0],offstate[1]+1)
        elif(next_action==3):
            new_state=(offstate[0]+1,offstate[1])
        elif(next_action==4):
            new_state=(offstate[0],offstate[1]-1)
            
        if(new_state==Target_State):
            reward+=100
        else:
            reward-=1

        Qtable[offstate[0]*4+offstate[1]+1][next_action-1]+=reward

        offstate=new_state
    

#####Online Optimizing#####

Online_start_state=Start_State
onstate=Online_start_state

#take human input
human_input=[3]
reward=0

while(onstate!=Target_State):
    if len(human_input)!=0:
        action=human_input.pop(0)
        PS[onstate[0]*4+onstate[1]+1][action-1]+=1
        
    else:
        move_choice=[]

        wall=RealMap[onstate[0]][onstate[1]]
        print(wall)
        for j in range(len(wall)):
            if wall[j]==0:
                move_choice.append(j)

        
        print(move_choice)

        pq_sum=0
        p_set={}


        for k in move_choice:
            pq_sum+=math.pow(e,Qtable[onstate[0]*4+onstate[1]+1][k]/t)

        for k in move_choice:
            pq_k=math.pow(e,Qtable[onstate[0]*4+onstate[1]+1][k]/t)/pq_sum
            pb_k=math.pow(B,PS[onstate[0]*4+onstate[1]+1][k])/(math.pow(B,PS[onstate[0]*4+onstate[1]+1][k])
            +math.pow(1-B,PS[onstate[0]*4+onstate[1]+1][k]))
            p_set.update({k:pq_k*pb_k})

        p_sum=sum(p_set.values())

        for k in move_choice:
            p_set.update({k:p_set[k]/p_sum})

        r=random.random()*sum(p_set.values())
        for i in range(len(p_set)):
            if list(p_set.values())[i]>=r:
                break
            else:
                r-=list(p_set.values())[i]

        action=list(p_set.keys())[i]+1
        
    #Perform Action
    if(action==1):
        new_state=(onstate[0]-1,onstate[1])
    elif(action==2):
        new_state=(onstate[0],onstate[1]+1)
    elif(action==3):
        new_state=(onstate[0]+1,onstate[1])
    elif(action==4):
        new_state=(onstate[0],onstate[1]-1)

    if(new_state==Target_State):
        reward+=100
    else:
        reward-=1
        
    print(action)
    print("new_state:",new_state)

    Qtable[onstate[0]*4+onstate[1]+1][action-1]+=reward

    onstate=new_state