# HRI-Navigation-in-Maze

Team member: 
    Hang Yu, Yuchen Yang, Ziyu Zhou

Usage: 
    Install Webots from https://cyberbotics.com/, Click on "Open Worlds..." and select "empty.wbt" in the directory to open the project.

How to run the simulator:
    There are two scenes for running the simulation. When you click on the start button, the system will wait for verbal instruction. If you say "Learning", then the robot will enter Human Guide Learning mode. Follow human instructions("Turn right", "Turn left", and "Go ahead".), update the Qtable and PS, and halt when user say "Stop!", the system will automatically run offline training after learning.
    When the user say "optimizing", the system will start to run online optimizing. It will wait for human input or generate a new move command based on Qtable and PS if no human input available. When the robot reach the target, it will run offline training too.