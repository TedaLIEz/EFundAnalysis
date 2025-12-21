import { useEffect, useRef, useLayoutEffect } from "react";

function ChatContainer({
  messages,
  currentStreamingMessage,
  isConnected,
  streamingContentElementRef,
}) {
  const chatContainerRef = useRef(null);
  const isStreamingRef = useRef(false);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, currentStreamingMessage]);

  // Sync streaming message content synchronously before browser paint
  // This ensures smooth streaming like dev_ui implementation
  useLayoutEffect(() => {
    if (currentStreamingMessage && streamingContentElementRef.current) {
      // Sync content from state to DOM (happens synchronously before paint)
      streamingContentElementRef.current.textContent =
        currentStreamingMessage.content;
      // Force a reflow to ensure the browser renders the update immediately
      void streamingContentElementRef.current.offsetHeight;
      isStreamingRef.current = true;
      // Scroll to bottom as content streams in
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop =
          chatContainerRef.current.scrollHeight;
      }
    } else if (!currentStreamingMessage) {
      isStreamingRef.current = false;
    }
  }, [currentStreamingMessage, streamingContentElementRef]);


  const getAvatar = (role) => {
    switch (role) {
      case "user":
        return "U";
      case "assistant":
        return "A";
      case "system":
        return "S";
      case "error":
        return "!";
      default:
        return "?";
    }
  };

  if (!isConnected && messages.length === 0) {
    return (
      <div className="chat-container" ref={chatContainerRef}>
        <div className="empty-state">Connect to the server to start chatting</div>
      </div>
    );
  }

  return (
    <div className="chat-container" ref={chatContainerRef}>
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.role}`}>
          <div className="message-avatar">{getAvatar(message.role)}</div>
          <div className="message-content">{message.content}</div>
        </div>
      ))}
      {currentStreamingMessage && (
        <div className="message assistant">
          <div className="message-avatar">A</div>
          <div
            className="message-content"
            ref={streamingContentElementRef}
            style={{ whiteSpace: "pre-wrap" }}
            suppressContentEditableWarning
            contentEditable={false}
          >
            <span className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatContainer;
