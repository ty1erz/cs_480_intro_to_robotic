# Object detection of self-driven rover

Github Link: `https://github.com/ty1erz/cs_480_intro_to_robotic`

## Table of Contents
- [Project Idea](#project-idea)
- [Data](#data)
- [Model](#model)
- [Code](#code)
- [Others](#others)

## Project Idea
### Overview
Our rover detects and classifies the self-maded signs and turn when the signs are closed enough with the fine-tuning object dectection model and kinamatic tuning.


## Data
### Data Source
- The data are captured using Data Capture feature from our webcam component

### Data Description
- The data include pictures of self-maded signs of `left_turn`, `right_turn`, and `u_turn`.
- Each class has around 15 pictures

### Data Preprocessing
- The bounding boxes were manually selected when constructing the dataset
- Here are some demostrastion of the dataset:

![Project Image](dataset.png)
*Screenshot of the dataset*
    

## Model
### Model Selection
- The object detection model we were using for the model is the built-in model in Viam and we fine-tuned it for our dataset.
- We initialy tried to use the pre-trained lite object dection model from tensorflow (`tflite`)since they are smaller, thus easier to compute. However, we discover that using `tflite` had extremely high error rate between `left_turn` and `right_turn` when the signs are closed. We suspected that the `tflite` might have some pre-processing for the image like horizontal flip that confused the model, therefore, we changed it back to the Viam built-in model.

### Training
- The training took around 8mins and the model size is 18.26MB.

### Evaluation
- After manually evalute the model, we decided that the performance is good enough. However, the latency is still high, further improvement can be done by shrinking down the model size.

## Code
### Repository
The code for executing the project is in `main.py`.

### Usage Instructions
- Once you upload the the code to your rover, you can start the project by executing `python3 main.py`.
- You need install the 'viam-sdk' for python api of the rover.
### Code Structure
- We used the code we did for the color detection. The main problems we met was fine tunning to get the desired object detected by the object detection model and make the rover do specific actions when it is close enough to the target, the traffic signs. This part is mainly included by the function 'recog'.

```python
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
    
    #too far or no suitable target
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
        return -1 #no label, illegal target
```

- We accessed the vision service for the detector to get:

```python
#position (bounding box) information of the detected object
"x_max" , "x_min", "y_max", "y_min"

#label name
"class_name"

#confidence in the labelling of the object
"confidence"
```
- And then use a for loop to traverse all detected objects. The largest object is usually the desired target. So we get the largest object. But sometimes even the largest object can be unwanted -- it is often a small part of the image wrongly detected by the model. So we need to ignore such small detected objects. Another task can also be done at the same time: ignore the detected traffic sign when the rover is too far away from the sign. So we used a if statement to do this job.

- Other parts of our code are simple. Use the returned value of the function to make the rover do corresponding actions.
## Others
- We found some possible problems with the rover's drive system. It doesn't go in a straight line very well and the steering angle has a large error. So what we used in the video was to manually place traffic signs in the direction the rover was going.

