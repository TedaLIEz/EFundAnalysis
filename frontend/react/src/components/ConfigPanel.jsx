function ConfigPanel({
  backendUrl,
  setBackendUrl,
  isConnected,
  onConnect,
  onDisconnect,
  onReset,
  onHealthCheck,
}) {
  return (
    <div className="config-panel">
      <input
        type="text"
        value={backendUrl}
        onChange={(e) => setBackendUrl(e.target.value)}
        placeholder="Backend API URL"
        disabled={isConnected}
      />
      <button
        className="btn-connect"
        onClick={onConnect}
        disabled={isConnected}
      >
        Connect
      </button>
      <button
        className="btn-disconnect"
        onClick={onDisconnect}
        disabled={!isConnected}
      >
        Disconnect
      </button>
      <button
        className="btn-reset"
        onClick={onReset}
        disabled={!isConnected}
      >
        Reset Chat
      </button>
      <button className="btn-health" onClick={onHealthCheck}>
        Health Check
      </button>
    </div>
  );
}

export default ConfigPanel;
