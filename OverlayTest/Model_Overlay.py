"""
Script for running YOLO model with overlay detection
"""
import cv2
import numpy as np
import threading
import json
import time
from shapely.geometry import Polygon

net = cv2.dnn.readNet('yolov3_2_5_2021.weights', 'yolov3_testing.cfg')

classes = []
with open('coco_custom.names', 'r') as f:
    classes = f.read().splitlines()

# cap = cv2.VideoCapture('Emergency 2 (Aaron).mov')  # name of video file here
cap = cv2.VideoCapture(0)


# overlay_file = 'emergency_1_aaron_image_overlay.json'
overlay_file = 'webcam_test_overlay_2.json'

#  Frames per second in the video
frame_rate = 30

#  Dictionary of Region objects
Regions = {}

#  Font for overlay text
font = cv2.FONT_HERSHEY_PLAIN

#  Confidence threshold for model detection
threshold = 0.1

#  "True" = Using Region Overlap, "False" = Point Containment
overlap_type = True

#  Shrinks image size by entered factor
resize_factor = 1


#  Class for Region data
class Region:
    def __init__(self, name_):
        self.name = name_
        self.point_list = []
        self.numpy_point_list = None
        self.intersected = False

    def add_point(self, x_, y_):
        self.point_list.append((x_, y_))


#  Populating regions with data from JSON file
with open(overlay_file) as json_file:
    data = json.load(json_file)
    for reg_json in data["data"]:
        reg = Region(reg_json["name"])
        for point_json in reg_json["points"]:
            reg.add_point(float(point_json["x"]), float(point_json["y"]))
        Regions[reg.name] = reg

_, img = cap.read()
init_height, init_width, _ = img.shape


#  Scaling point data in Regions to fit image size
for region in Regions:
    for i in range(len(Regions[region].point_list)):
        point = Regions[region].point_list[i]
        p = list(point)
        p[0] = p[0]*init_width
        p[1] = p[1]*init_height
        Regions[region].point_list[i] = tuple(p)
    points = np.array(Regions[region].point_list)
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))
    Regions[region].numpy_point_list = pts


def model():
    global img, cap
    # _, img = cap.read()
    img_copy = img
    '''height, width, _ = img_copy.shape
    blob = cv2.dnn.blobFromImage(img_copy, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > threshold:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)

                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, threshold, 0.4)

    temp_boxes = []

    detected_regions = []

    if len(indexes) > 0:
        for i in indexes.flatten():
            temp_boxes.append(boxes[i])
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = (0, 255 * confidences[i] / (1 - threshold) - 255 * threshold / (1 - threshold),
                     -255 * confidences[i] / (1 - threshold) + 255 / (1 - threshold))
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), color, 2)
            cv2.putText(img_copy, label + " " + confidence, (x, y+20), font, 2, (255, 255, 255), 2)

            #  For each detected hand, loops through every region to check for overlap
            for region in Regions:
                p = Polygon(Regions[region].point_list)
                q = Polygon([(x, y), (x+w, y), (x, y+h), (x+w, y+h)])
                if overlap_type:
                    if p.intersects(q):
                        Regions[region].intersected = True
                        detected_regions.append(region)
                else:
                    if p.contains(q.centroid):
                        Regions[region].intersected = True
                        detected_regions.append(region)

    #  Drawing polygon for each region
    for region in Regions:
        if Regions[region].intersected:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        cv2.polylines(img_copy, [Regions[region].numpy_point_list], True, color, 2)
        Regions[region].intersected = False

    img_copy = cv2.resize(img_copy, (int(width/resize_factor), int(height/resize_factor)))

    sub_img = img_copy[0:int((len(detected_regions) + 1)*22), 0:150]
    black_rect = np.ones(sub_img.shape, dtype=np.uint8) * 0
    res = cv2.addWeighted(sub_img, 0.25, black_rect, 0.5, 1.0)
    img_copy[0:int((len(detected_regions) + 1)*22), 0:150] = res

    text_color = (255, 255, 255)
    text_thickness = 2
    cv2.putText(img_copy, "Active: ", (0, 20), font, 1.3, text_color, text_thickness)
    y_pos = 40
    for region in detected_regions:
        cv2.putText(img_copy, region, (0, y_pos), font, 1.3, text_color, text_thickness)
        y_pos += 20
    '''
    cv2.imshow('Image', img_copy)
    key = cv2.waitKey(1)


def frame_flow():
    global img, cap
    print("frame_flow 0")
    while True:
        time.sleep(1/(frame_rate*3)) # *1.85)) # 1.3))
        _, img = cap.read()

    cap.release()
    cv2.destroyAllWindows()


def main():
    t1 = threading.Thread(target=frame_flow)
    t1.start()

    while True:
        model()


main()
