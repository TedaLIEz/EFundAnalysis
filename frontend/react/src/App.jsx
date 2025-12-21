import { useState, useEffect, useRef } from "react";
import { flushSync } from "react-dom";
import { io } from "socket.io-client";
import ChatContainer from "./components/ChatContainer";
import Header from "./components/Header";
import ConfigPanel from "./components/ConfigPanel";
import InputContainer from "./components/InputContainer";
import "./App.css";

const getBackendUrl = () => {
  // Check for environment variable (set in Azure App Service)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Auto-detect for production
  if (window.location.hostname !== "localhost") {
    return `${window.location.protocol}//${window.location.hostname}:5001`;
  }
  // Default for local development
  return "http://localhost:5001";
};

function App() {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [waitingForResponse, setWaitingForResponse] = useState(false);
  const [backendUrl, setBackendUrl] = useState(getBackendUrl());
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState(null);
  const streamTimeoutRef = useRef(null);
  const streamingMessageRef = useRef(null);
  const streamingContentElementRef = useRef(null);

  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect();
      }
      if (streamTimeoutRef.current) {
        clearTimeout(streamTimeoutRef.current);
      }
    };
  }, [socket]);

  const connect = () => {
    if (socket) {
      socket.disconnect();
    }

    const newSocket = io(backendUrl, {
      transports: ["websocket", "polling"],
      reconnection: false,
    });

    newSocket.on("connect", () => {
      console.log("Connected to server");
      setIsConnected(true);
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from server");
      setIsConnected(false);
      setWaitingForResponse(false);
      if (streamTimeoutRef.current) {
        clearTimeout(streamTimeoutRef.current);
      }
      setCurrentStreamingMessage(null);
    streamingMessageRef.current = null;
    streamingContentElementRef.current = null;
    });

    newSocket.on("connected", (data) => {
      console.log("Connection confirmed:", data);
      addMessage("system", data.message || "连接成功！可以开始聊天了。");
    });

    newSocket.on("response", (data) => {
      console.log("Received response chunk:", data);

      const msgType = data.type || "assistant";
      const message = data.message;
      const isDone = data.done === true;

      if (msgType === "user") {
        addMessage("user", message);
      } else if (msgType === "assistant") {
        if (isDone) {
          console.log("Stream completed (done signal)");
          completeStreamingMessage();
        } else if (message) {
          appendToStreamingMessage(message);
        }
      } else if (msgType === "system") {
        completeStreamingMessage();
        addMessage("system", message);
      }
    });

    newSocket.on("error", (data) => {
      console.error("Error from server:", data);
      completeStreamingMessage();
      addMessage("error", data.message || "An error occurred");
      setWaitingForResponse(false);
    });

    newSocket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      alert(`Failed to connect: ${error.message}`);
      setIsConnected(false);
    });

    setSocket(newSocket);
  };

  const disconnect = () => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
    }
    setIsConnected(false);
    setWaitingForResponse(false);
    if (streamTimeoutRef.current) {
      clearTimeout(streamTimeoutRef.current);
    }
    setCurrentStreamingMessage(null);
    streamingMessageRef.current = null;
    streamingContentElementRef.current = null;
  };

  const addMessage = (role, content) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role,
        content,
      },
    ]);
  };

  const appendToStreamingMessage = (chunk) => {
    if (!chunk) {
      return;
    }

    // Use flushSync to ensure immediate DOM updates for smooth streaming
    flushSync(() => {
      setCurrentStreamingMessage((prev) => {
        // If no streaming message exists, create one
        const newMessage = !prev
          ? {
              id: Date.now(),
              content: chunk,
            }
          : {
              ...prev,
              content: prev.content + chunk,
            };
        // Keep ref in sync with state
        streamingMessageRef.current = newMessage;
        return newMessage;
      });
    });

    // Note: DOM updates will be handled by useLayoutEffect in ChatContainer
    // for synchronous updates before browser paint

    // Reset timeout - if no chunks arrive for 1000ms, consider stream complete
    if (streamTimeoutRef.current) {
      clearTimeout(streamTimeoutRef.current);
    }
    streamTimeoutRef.current = setTimeout(() => {
      console.log("Stream completed (timeout)");
      completeStreamingMessage();
    }, 1000);
  };

  const completeStreamingMessage = () => {
    if (streamTimeoutRef.current) {
      clearTimeout(streamTimeoutRef.current);
      streamTimeoutRef.current = null;
    }
    const messageToComplete = streamingMessageRef.current;
    setCurrentStreamingMessage(null);
    streamingMessageRef.current = null;
    streamingContentElementRef.current = null;
    if (messageToComplete && messageToComplete.content) {
      addMessage("assistant", messageToComplete.content);
    }
    setWaitingForResponse(false);
  };

  const sendMessage = (messageText) => {
    if (!messageText.trim() || !isConnected || !socket || waitingForResponse) {
      return;
    }

    // Reset streaming state for new message
    if (streamTimeoutRef.current) {
      clearTimeout(streamTimeoutRef.current);
      streamTimeoutRef.current = null;
    }
    setCurrentStreamingMessage(null);
    streamingMessageRef.current = null;
    streamingContentElementRef.current = null;

    // Add user message to chat
    addMessage("user", messageText);

    // Show waiting state
    setWaitingForResponse(true);

    // Send message via SocketIO
    socket.emit("json", { data: messageText });
  };

  const resetChat = () => {
    if (!isConnected || !socket) {
      return;
    }

    if (streamTimeoutRef.current) {
      clearTimeout(streamTimeoutRef.current);
      streamTimeoutRef.current = null;
    }
    setCurrentStreamingMessage(null);
    streamingMessageRef.current = null;
    streamingContentElementRef.current = null;
    socket.emit("reset");
    setMessages([]);
  };

  const checkHealth = async () => {
    try {
      const response = await fetch(`${backendUrl}/health`);
      const data = await response.json();
      addMessage("system", `Health check: ${JSON.stringify(data)}`);
    } catch (error) {
      addMessage("error", `Health check error: ${error.message}`);
    }
  };

  // Update messages when streaming message changes
  useEffect(() => {
    if (currentStreamingMessage) {
      // This will be handled by the streaming logic
    }
  }, [currentStreamingMessage]);

  return (
    <div className="app">
      <Header isConnected={isConnected} />
      <ConfigPanel
        backendUrl={backendUrl}
        setBackendUrl={setBackendUrl}
        isConnected={isConnected}
        onConnect={connect}
        onDisconnect={disconnect}
        onReset={resetChat}
        onHealthCheck={checkHealth}
      />
      <ChatContainer
        messages={messages}
        currentStreamingMessage={currentStreamingMessage}
        isConnected={isConnected}
        streamingContentElementRef={streamingContentElementRef}
      />
      <InputContainer
        onSendMessage={sendMessage}
        disabled={!isConnected || waitingForResponse}
      />
    </div>
  );
}

export default App;
