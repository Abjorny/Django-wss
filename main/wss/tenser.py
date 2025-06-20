import numpy as np
import cv2
import tflite_runtime.interpreter as tflite

TFLITE_PATH = "/home/abjorny/Django-wss/main/mobilenetv3_custom.tflite"
IMAGE_SIZE = (224, 224)
LABELS = ['1', '21', '22', '23', '24', '31', '32', '34', '41', '51', '52', '53', '54']

interpreter = tflite.Interpreter(model_path=TFLITE_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess_image(img):
    img = cv2.resize(img, IMAGE_SIZE)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0) 
    return img

def predict_image_classpredict(image_path):
    input_data = preprocess_image(image_path)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_index = np.argmax(output_data)
    predicted_class = LABELS[predicted_index]

    return int(predicted_class), 1.0
