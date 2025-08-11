import cv2

def returnAngleItem(data, sensorData, frame):
    x_min = sensorData["x_min"]
    x_max = sensorData["x_max"]
    y_min = sensorData["y_min"]
    y_max = sensorData["y_max"]

    x1 =  data[0]
    y1 = data[1]
    w = data[2]
    h = data[3]

    shape = frame.shape
    height = shape[0]
    width = shape[1]

    y_center_frame = height // 2
    x_center_frame = width // 2

    y_center_item = y1 + y_min + (h // 2)
    x_center_item = x1 + x_min + (w // 2)

    quater = 0

    if x_center_item > x_center_frame:
        if y_center_item > y_center_frame:
            quater = 1
        else:
            quater = 4
    else:
        if y_center_item < y_center_frame:
            quater = 2
        else:
            quater = 3
    
    cv2.line(frame, (x_center_frame, y_center_frame), (x_center_item, y_center_item), (0, 255, 255), 2)
    return quater