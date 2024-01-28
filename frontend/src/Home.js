import React, { useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";
import "./App.css";
import bt from "./images/bt.jpg";
import morpheus from "./images/morpheus.jpg";
import neo from "./images/neo.png";
import send1 from "./images/send1.png";
import static_mic1 from "./images/static_mic1.gif";
import dancing_mic1 from "./images/dancing_mic1.gif";
import { DataContext } from "./context/DataProvider";

export default function Home() {
  const [messages, setMesssages] = useState([]);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");

  const { customCharacteristic, setCustomCharacteristic } =
    useContext(DataContext);

  let socket = "";

  useEffect(() => {
    socket = io("http://localhost:5000");
    socket.on("server_message", (data) => {
      console.log("Received message from server:", data.message);
      const result = writeCharacteristic(data.message);
      console.log(customCharacteristic, "socket");
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const connectToDevice = async () => {
    try {
      const device = await navigator.bluetooth.requestDevice({
        acceptAllDevices: true,
        optionalServices: ["0000ffe0-0000-1000-8000-00805f9b34fb"],
      });

      const server = await device.gatt.connect();
      const service = await server.getPrimaryService(
        "0000ffe0-0000-1000-8000-00805f9b34fb"
      );
      let tmp = await service.getCharacteristic(
        "0000ffe1-0000-1000-8000-00805f9b34fb"
      );
      setCustomCharacteristic(tmp);
      console.log("Connected to bluetooth device successfully");
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const submitForm = (event) => {
    event.preventDefault(); // Prevents the default form submission behavior
    var input = document.getElementById("input").value;
    sendRequest(input);
  };

  const sendRequest = (input) => {
    setTranscript("");
    setMesssages([...messages, { image: neo, message: input }]);

    var formData = new FormData();
    formData.append("input", input);

    fetch("http://localhost:5000/submit_form", {
      method: "POST",
      body: formData,
      mode: "no-cors",
    })
      .then((response) => {
        console.log("Form submitted");
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const writeCharacteristic = async (input) => {
    try {
      let command = input[0];
      let n = parseInt(input.substring(1));

      console.log("Command:", command);
      console.log("Execute command for ", n, " * (0.45) secs");
      n = n * 0.45; //When turning left and right the time duration should be in multiples of 0.5s

      const encoder = new TextEncoder("utf-8");
      let valueToWrite = encoder.encode(command);

      console.log(customCharacteristic);
      if (customCharacteristic) {
        console.log(customCharacteristic);
        await customCharacteristic.writeValue(valueToWrite);
      }

      setTimeout(async () => {
        valueToWrite = encoder.encode("s");
        if (customCharacteristic) {
          await customCharacteristic.writeValue(valueToWrite); //Run after n steps are completed
        }
      }, n * 1000);

      return true;
    } catch (error) {
      console.error("Error writing to characteristic:", error);
      return false;
    }
  };

  useEffect(() => {
    let timeout;

    if (listening) {
      const recognition = new window.webkitSpeechRecognition(); // For Safari compatibility
      recognition.continuous = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setListening(true);
      };

      recognition.onresult = (event) => {
        const current = event.resultIndex;
        const tmptranscript = event.results[current][0].transcript;
        setTranscript(tmptranscript);
        // Reset the timeout on speech recognition
        clearTimeout(timeout);
        timeout = setTimeout(async () => {
          console.log(transcript);
          recognition.stop();
          setListening(false);
          sendRequest(tmptranscript);
        }, 2000); // Stop listening if no speech for 3 seconds
      };

      recognition.onend = () => {
        setListening(false);
        console.log("speech ended");
      };

      recognition.onerror = (event) => {
        console.error("Error occurred in recognition: ", event.error);
        setListening(false);
      };

      recognition.start();
    }

    return () => clearTimeout(timeout); // Clear the timeout on component unmount or dependency change
  }, [listening]);

  const startListening = () => {
    setListening(true);
  };

  return (
    <div className="home">
      <div className="chatlist">
        <div className="chat">
          <div
            className="chat_img"
            style={{
              backgroundImage: `url(${morpheus})`,
              backgroundSize: "contain",
              backgroundRepeat: "no-repeat",
              backgroundPosition: "center",
            }}
          ></div>
          <div className="chat_msg">
            Hi, I am Morpheus, a robot powered by AI. Click on
            <img
              onClick={() => connectToDevice()}
              src={bt}
              style={{
                backgroundSize: "contain",
                width: "25px",
                height: "25px",
                margin: "0 5px",
                marginBottom: "-5px",
                cursor: "pointer",
              }}
            />
            to connect with me.
          </div>
        </div>

        {messages.map((msg, ind) => {
          return (
            <div className="chat" key={ind}>
              <div
                className="chat_img"
                style={{
                  backgroundImage: `url(${msg.image})`,
                  backgroundSize: "contain",
                  backgroundRepeat: "no-repeat",
                  backgroundPosition: "center",
                }}
              ></div>
              <div className="chat_msg">{msg.message}</div>
            </div>
          );
        })}
      </div>

      <form id="myForm" onSubmit={submitForm}>
        <input
          type="text"
          id="input"
          name="input"
          required
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
        />
        <div
          onClick={() => setListening(true)}
          className="micbtn"
          style={{
            width: "50px",
            backgroundImage: `url(${listening ? dancing_mic1 : static_mic1})`,
            backgroundSize: "contain",
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center",
            cursor: "pointer",
          }}
        ></div>
        <button
          className="sendbtn"
          style={{
            width: "40px",
            marginTop: "-5px",
            backgroundImage: `url(${send1})`,
            backgroundSize: "contain",
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center",
            backgroundColor: "black",
            outline: "0",
            border: "none",
            cursor: "pointer",
          }}
        ></button>
      </form>
    </div>
  );
}
