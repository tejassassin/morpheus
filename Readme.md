
#Create virtual envirnoment and activate
<!-- in cmd -->
python -m venv venv
venv\Scripts\activate.bat   4

#Install necessary dependencies and 

#Run the backend 
python3 flask_app.py
python3 detection.py 

#frontend 
npm start


#How does it work?

The bluetooth module that is use to send signals to arduino UNO is HC08, it is a BLE (bluetooth low energy device) so u can only connect to it from chrome browser using Web Bluetooth API. So i looked into the source code of chrome for the exact javascript functions which allow to connect and write values to bluetooth. Once i was able to write bluetooth signals to arduino, next task was to connect it to the LLM (large language model).
LLMs and Open CV libraries run on python so i created a flask app. The prompt from the frontend is send to the flask app as a post request then a langchain agent gets initialised which breaks down the task in smaller subtasks. Langchain agents can use tools(nothing but functions) to complete these smaller subtasks and then combine the results to accomplish the overall task.
My LLM  has 5 tools (move_forward, move_backward, turn_left, turn_right, watch).
It uses these tool as and when needed and sends the signals to frontend via web sockets. Which finally get sent to arduino UNO using Web Bluetooth API.  
And when the LLM uses the 'watch' tool. It gets the objects and faces detected along with co ordinates via sockets from the detection app which use Open CV libraries like haarcascade and yolov8 for face and object detection respectively.