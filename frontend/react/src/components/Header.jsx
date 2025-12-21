function Header({ isConnected }) {
  return (
    <div className="header">
      <h1>FinWeave Chat</h1>
      <div className="connection-status">
        <span className={`status-indicator ${isConnected ? "connected" : ""}`}></span>
        <span>{isConnected ? "Connected" : "Disconnected"}</span>
      </div>
    </div>
  );
}

export default Header;
