try:
    import sim
except:
    print ('--------------------------------------------------------------')
    print ('"sim.py" could not be imported. This means very probably that')
    print ('either "sim.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "sim.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time

ground = [3, 3, 3]
black = [1, 1, 1]
red = [3, 1, 1]
blue = [1, 1, 3]
green = [1, 3, 1]
pink = [3, 1, 3]
yellow = [3, 3, 1]
turquoise = [1, 3, 3]
fuchsia = [3, 1, 2]
dgreen= [1, 2, 1]
test = [0, 0, 0]

speed = 0.1
clientID = 0

colours = {
    'black': black,
    'red': red,
    'blue': blue,
    'green': green,
    'pink': pink,
    'yellow': yellow,
    'turquoise': turquoise,
    'fuchsia': fuchsia,
    'dgreen': dgreen,
}

def colourSwap(direction, visionSensors, joints, nextColour):
    print("turning")
    if direction == "left":
        sim.simxSetJointTargetVelocity(clientID, joints[0], 0, sim.simx_opmode_oneshot)
        colourData = getColourData(visionSensors)
        while colourData[0] != nextColour:
            colourData = getColourData(visionSensors)
        time.sleep(.5)
        sim.simxSetJointTargetVelocity(clientID, joints[0], speed, sim.simx_opmode_oneshot)

    elif direction == "right":
        sim.simxSetJointTargetVelocity(clientID, joints[1], 0, sim.simx_opmode_oneshot)
        colourData = getColourData(visionSensors)
        while colourData[1] != nextColour:
            colourData = getColourData(visionSensors)
        time.sleep(.5)
        sim.simxSetJointTargetVelocity(clientID, joints[1], speed, sim.simx_opmode_oneshot)

def lineFollow(direction, joints):
    if direction == "left":
        sim.simxSetJointTargetVelocity(clientID, joints[0], 0, sim.simx_opmode_oneshot)
        time.sleep(.5)
        sim.simxSetJointTargetVelocity(clientID, joints[0], speed, sim.simx_opmode_oneshot)
    elif direction == "right":
        sim.simxSetJointTargetVelocity(clientID, joints[1], 0, sim.simx_opmode_oneshot)
        time.sleep(.5)
        sim.simxSetJointTargetVelocity(clientID, joints[1], speed, sim.simx_opmode_oneshot)

def startMotors(joints):
    sim.simxSetJointTargetVelocity(clientID, joints[0], speed, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, joints[1], speed, sim.simx_opmode_oneshot)

def colourCompare(c1, c2):
    for x in range(3):
        if c1[x] != c2[x]:
            return False
    return True

def getNextColour(currColour, destColour):
    if (currColour == green):
        return red
    if (currColour == red):
        if (destColour == green):
            return green
        elif (destColour == black):
            return black
        else:
            return blue
    if (currColour == black):
        if (destColour == green or destColour == red):
            return red
        else:
            return blue
    if (currColour == blue):
        if (destColour == green or destColour == red):
            return red
        elif (destColour == black):
            return black
        elif (destColour == pink):
            return pink
        else:
            return yellow
    if (currColour == pink):
        if (destColour == green or destColour == red or destColour == black or destColour == blue):
            return blue
        else:
            return yellow
    if (currColour == yellow):
        if (destColour == green or destColour == red or destColour == black or destColour == blue):
            return blue
        elif (destColour == pink):
            return pink
        elif (destColour == turquoise):
            return turquoise
        else:
            return fuchsia
    if (currColour == turquoise):
        if (destColour == dgreen or destColour == fuchsia):
            return fuchsia
        else:
            return yellow
    if (currColour == fuchsia):
        if (destColour == dgreen):
            return dgreen
        elif (destColour == turquoise):
            return turquoise
        else:
            return yellow

    if (currColour == dgreen):
        return fuchsia

def stop(joints):
    sim.simxSetJointTargetVelocity(clientID, joints[0], 0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(clientID, joints[1], 0, sim.simx_opmode_oneshot)
    time.sleep(1)

def getColourData(visionSensors):
    colourData = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    for x in range(4):
        result, response , data = sim.simxReadVisionSensor(clientID, visionSensors[x], sim.simx_opmode_blocking)
        if result >= 0:
            for j in range(3):
                if data[0][11+j] <= 0.35:
                    colourData[x][j] = 1
                elif data[0][11+j] <= 0.7:
                    colourData[x][j] = 2
                elif data[0][11+j] <= 1:
                    colourData[x][j] = 3
    return colourData


def main(destColour):
    print ('Program started')
    destColour = colours[destColour]
    currColour = green
    nextColour = getNextColour(currColour, destColour)

    sim.simxFinish(-1) # just in case, close all opened connections
    clientID=sim.simxStart('127.0.0.1',19998,True,True,5000,5) # Connect to CoppeliaSim
    if clientID!=-1:
        print ('Connected to remote API server')

        response, leftJoint = sim.simxGetObjectHandle(clientID, 'Left_joint', sim.simx_opmode_blocking)
        response, rightJoint = sim.simxGetObjectHandle(clientID, 'Right_joint', sim.simx_opmode_blocking)
        joints = [leftJoint, rightJoint]
        visionSensors = [leftJoint,leftJoint,leftJoint,leftJoint]
        response, visionSensors[0] = sim.simxGetObjectHandle(clientID, 'LeftSensor', sim.simx_opmode_blocking)
        response, visionSensors[1] = sim.simxGetObjectHandle(clientID, 'RightSensor', sim.simx_opmode_blocking)
        response, visionSensors[2] = sim.simxGetObjectHandle(clientID, 'LeftColourSensor', sim.simx_opmode_blocking)
        response, visionSensors[3] = sim.simxGetObjectHandle(clientID, 'RightColourSensor', sim.simx_opmode_blocking)

        startMotors(joints)

        while(currColour != destColour):
            colourData = getColourData(visionSensors)

            if colourCompare(colourData[2], nextColour):
                colourSwap("left", visionSensors, joints, nextColour)
                currColour = nextColour
                nextColour = getNextColour(currColour, destColour)
            elif colourCompare(colourData[3], nextColour):
                colourSwap("right", visionSensors, joints, nextColour)
                currColour = nextColour
                nextColour = getNextColour(currColour, destColour)

            if colourCompare(colourData[0], currColour):
                lineFollow("left", joints)
            if colourCompare(colourData[1], currColour):
                lineFollow("right", joints)
        print("done")
        stop(joints)

    else:
        print ('Failed connecting to remote API server')
        print ('Program ended')
