
# Code for the Agent

from langchain.agents import initialize_agent
from langchain.llms import GooglePalm
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
import os
from flask_socketio import SocketIO
import time
import threading

command = ""

detected_items = []

def to_look(input="Watching"):
    global command 
    global detected_items
    command = ""
    line1 = ""
    line2 = ""
    
    for item in detected_items:
        for label in item:
            line1 += label + ', '
            coordinates = ','.join(map(str, item[label]))
            line2 += coordinates + ", "
        
    if len(detected_items) == 0:
        return "you don't see anything"
    else:
        return f"you see the following things {line1} at cordinates {line2} respectively"

tool_to_look = Tool(
    name="Watch",
    description="""
    The input for this tool is 'watching'.
    You can use this tool to watch what is in front of you only. If u need to look in a dirction other than front you need to turn first.
    If you are looking for something maybe dont look in the same direction again
    amd again and try changing directions.
    """,
    func=to_look,
)

def turn_left(n="1"):
    global command 
    command = "l" + n
    socketio.emit('server_message', {'message': f"{command}"})
    secs = int(int(n)/2)
    time.sleep(secs)
    print("\nsignal sent: ",command)
    return f"You have now turned to left {n} times."

tool_turn_left = Tool(
    name="Turn left",
    description="You can use this tool to turn left. The input 'n' is the number of turns.",
    func=turn_left,
)


def turn_right(n="1"):
    global command 
    command = "r" + n
    socketio.emit('server_message', {'message': f"{command}"})
    secs = int(int(n)/2)
    time.sleep(secs)
    print("\nsignal sent: ",command)
    
    return f"You have now turned to right {n} times."

tool_turn_right = Tool(
    name="Turn right",
    description="You can use this tool to turn right. The input 'n' is the number of turns.",
    func=turn_right,
)


def move_forward(n="1"):
    global command 
    command = "f" + n
    socketio.emit('server_message', {'message': f"{command}"})
    secs = int(int(n)/2)
    time.sleep(secs)
    
    print("\nsignal sent: ",command)
    return f"You have moved {n} steps forward."

tool_move_forward = Tool(
    name="Move forward",
    description="You can use this tool to move forward. The input is 'n' which represents the number of steps.",
    func=move_forward,
)


def move_backward(n="1"):
    global command 
    command = "b" + n
    socketio.emit('server_message', {'message': f"{command}"})
    secs = int(int(n)/2)
    time.sleep(secs)
    
    print("\nsignal sent: ",command)
    return f"You have moved {n} steps backward."

tool_move_backward = Tool(
    name="Move backward",
    description="You can use this tool to move backward. The input is 'n' which represents the number of steps.",
    func=move_backward,
)

GOOGLE_PALM_API = "YOUR_API_KEY"
llm = GooglePalm(google_api_key=GOOGLE_PALM_API, temperature=0.2, model="models/gemini-ultra")


# In case you want to use ChatGPT as the LLM
# OPENAI_API_KEY="YOUR_API_KEY"
# llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = OPENAI_API_KEY, )


toolkit = [
           tool_turn_left, 
           tool_turn_right, 
           tool_move_forward,
           tool_move_backward,
           tool_to_look, 
          ]

agent = initialize_agent(toolkit, 
                         llm, 
                         agent="zero-shot-react-description", 
                         verbose=True, 
                         return_intermediate_steps=True, 
                         max_iterations=10,
                         handle_parsing_errors=True,
                         )


## Flask app

from flask import Flask,   request
from flask_cors import CORS



app = Flask(__name__)

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

CORS(app)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    input = request.form.get('input')

    print("Prompt : ",input)
    response = agent(
        {
        "input": "You have access to bunch of tools but you may not need to use them. Think wisely and asnwer the following question. " + input
        }
    )
    print(response)
    return response['output']

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('items')
def handle_items(data):
    items = data['message']
    global detected_items
    detected_items = items
    # print(f"Received message from client: {items}")

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)




