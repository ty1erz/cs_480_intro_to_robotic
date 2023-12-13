#Work by Philip Liu, Tyler Zhang, using given introduction's code
import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.camera import Camera
from viam.components.base import Base

import time


async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='mkr339zox9c625b9apmowk8x8tryzd2e',
      api_key_id='e2ea0e1c-ee55-40ba-ba4c-7ac9e0fc6ea6'
    )
    return await RobotClient.at_address('my-main.5ykmma3q7t.viam.cloud', opts)


#recognize the sign
def recog(detections):
    if not detections:
        print("nothing detected :(")
        return -1
        
    largest_area = 0
    largest = {"x_max": 0, "x_min": 0, "y_max": 0, "y_min": 0, "class_name": None, "confidence":0}
    
    #get the largest box
    for d in detections:
        a = (d.x_max - d.x_min) * (d.y_max-d.y_min)
        if a > largest_area and d.confidence > 0.5:
            largest_area = a
            largest = d
    
    #too far
    if largest_area<30000:
        print("too far")
        return -2
    
    print(largest)
    
    if largest.class_name == 'left_turn':
        return 0  #turn left
    elif largest.class_name == 'right_turn':
        return 1  #turn right
    elif largest.class_name == 'u_turn':
        return 2  #turn back
    else:
        return -1
    
def leftOrRight(detections, midpoint):
    largest_area = 0
    largest = {"x_max": 0, "x_min": 0, "y_max": 0, "y_min": 0}
    if not detections:
        print("nothing detected :(")
        return -1
    for d in detections:
        a = (d.x_max - d.x_min) * (d.y_max-d.y_min)
        if a > largest_area:
            a = largest_area
            largest = d
    centerX = largest.x_min + largest.x_max/2
    if centerX < midpoint-midpoint/6:
        return 0  # on the left
    if centerX > midpoint+midpoint/6:
        return 2  # on the right
    else:
        return 1  # basically centered


async def main():
    spinNum = 5         # when turning, spin the motor this much
    straightNum = 100    # when going straight, spin motor this much
    numCycles = 200      # run the loop X times
    vel = 1200            # go this fast when moving motor

    # Connect to robot client and set up components
    robot = await connect()
    base = Base.from_robot(robot, "viam_base")
    camera_name = "cam"
    camera = Camera.from_robot(robot, camera_name)
    frame = await camera.get_image(mime_type="image/jpeg")

    # Grab the vision service for the detector
    my_detector = VisionClient.from_robot(robot, "ml_vision")

    # Main loop

    hasSpin=False
    
    for i in range(numCycles):
        detections = await my_detector.get_detections_from_camera(camera_name)

        answer = recog(detections)
        if answer == 0:
            print("Turn Left")
            await base.spin(70, vel)
            hasSpin=True
            
            
        if answer == 1:
            print("Turn Right")
            await base.spin(-70, vel)
            hasSpin=True
            
        if answer == 2:
            print("Turn Back")
            await base.spin(160, vel)
            hasSpin=True
            
        if answer < 0 :
            # if(hasSpin):
            #     pos=0
            #     while(pos!=1):
            #         detections = await my_detector.get_detections_from_camera(camera_name)
            #         pos = leftOrRight(detections, frame.size[0]/2)
            #         if pos == 0:
            #             print("left")
            #             await base.spin(spinNum, vel)     # CCW is positive
            #             await base.move_straight(straightNum, vel)
            #         if answer == 1:
            #             print("center")
            #             hasSpin=False
            #         if pos == 2:
            #             print("right")
            #             await base.spin(-spinNum, vel)
            await base.move_straight(straightNum, vel)

        


    await robot.close()

if __name__ == "__main__":
    print("Starting up... ")
    asyncio.run(main())
    print("Done.")