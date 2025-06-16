import numpy as np
import cv2
import tflite_runtime.interpreter as tflite

TFLITE_PATH = "/home/abjorny/Django-wss/main/mobilenet_model.tflite"
IMAGE_SIZE = (224, 224)
lab = ['1', '21', '22', '23', '24', '31', '32', '34', '41', '51', '52', '53', '54']

interpreter = tflite.Interpreter(model_path=TFLITE_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def create_color_masks(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    sum_rgb = r + g + b + 1e-7
    
    r_norm, g_norm, b_norm = r/sum_rgb, g/sum_rgb, b/sum_rgb
    
    red_mask = ((r_norm > 0.45) & (g_norm < 0.35) & (b_norm < 0.35)).astype(np.float32)
    blue_mask = ((b_norm > 0.45) & (r_norm < 0.35)).astype(np.float32)
    green_mask = ((g_norm > 0.4) & (r_norm < 0.35) & (b_norm < 0.35)).astype(np.float32)
    white_mask = ((r > 0.8) & (g > 0.8) & (b > 0.8)).astype(np.float32)
    black_mask = ((r < 0.2) & (g < 0.2) & (b < 0.2)).astype(np.float32)
    
    return np.stack([red_mask, blue_mask, green_mask, white_mask, black_mask], axis=-1)

def preprocess_image(img):
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32) / 255.0
    
    masks = create_color_masks(img)
    return masks[np.newaxis, ...] 



def predict(img):
    input_data = preprocess_image(img)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    class_id = np.argmax(output)
    confidence = round(float(np.max(output)), 2)
    return lab[class_id], confidence
