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

    y_center_sensor = (y_min + y_max) // 2
    x_center_sensor = (x_max + x_min) // 2

    y_center_item = y1 + y_min + (h // 2)
    x_center_item = x1 + x_min + (w // 2)

    quater = 0

    delta_x = x_center_sensor - x_center_item
    delta_y = y_center_sensor - y_center_item
    if delta_x > 0:
        if delta_y > 0:
            quater = 2
        else:
            quater = 3
    else:
        if delta_y > 0:
            quater = 1
        else:
            quater = 4
    
    cv2.line(frame, (x_center_sensor, y_center_sensor), (x_center_item, y_center_item), (0, 255, 255), 2)
    return quater