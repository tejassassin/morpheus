import math 
from ultralytics import YOLO
import cv2
import socketio


def init(sio):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    cap.set(3, 640)
    cap.set(4, 480)
    global shared_variable
    
    model = YOLO("yolo-Weights/yolov8n.pt")
    classNames = ["person","bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                "teddy bear", "hair drier", "toothbrush"
                ]


    while True:
        items = [] 
        success, img = cap.read()
        
        #Detect objects
        results = model(img, verbose=False)

        for r in results:
            boxes = r.boxes

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values
                
                confidence = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                if(classNames[cls] == "person"): # ignore person as we are doing face detection
                    continue
                
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                org = [x1, y1-10]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = .8
                color = (0, 255, 0)
                thickness = 2

                cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)
                if(classNames[cls] == "person"): #ignore person as we are doing face detection
                    continue
                items.append({classNames[cls]:[x2-x1, y2-y1]})
                
        #Detect Faces                
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h),(255, 0, 255), 3)
            org = [x, y-10]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = .8
            color = (0, 255, 0)
            thickness = 2
            cv2.putText(img,'human', org, font, fontScale, color, thickness)
            items.append({'human':[x+w/2,y+h/2]})

        sio.emit('items', {'message': items})
            
        key = cv2.waitKey(1)
        cv2.imshow('Webcam', img)

        
        if key == ord('q'):
            break


if __name__ == "__main__":
    sio = socketio.Client()

    @sio.event
    def connect():
        print('Connected to server')

    @sio.event
    def disconnect():
        print('Disconnected from server')

    sio.connect('http://localhost:5000')

    init(sio)