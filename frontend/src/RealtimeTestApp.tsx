import { useState } from "react";
import RealtimeDashboard from "./components/RealtimeDashboard";

function RealtimeTestApp() {
  const [facadeId, setFacadeId] = useState("1");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f0f2f5" }}>
      <div
        style={{
          padding: "20px",
          backgroundColor: "white",
          borderBottom: "1px solid #dee2e6",
          marginBottom: "0",
        }}
      >
        <h1 style={{ margin: "0 0 15px 0" }}>Test Realtime Dashboard Endpoint</h1>

        <div
          style={{
            display: "flex",
            gap: "20px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <div>
            <label style={{ marginRight: "8px", fontSize: "14px" }}>Fachada ID:</label>
            <input
              type="text"
              value={facadeId}
              onChange={e => setFacadeId(e.target.value)}
              style={{
                padding: "6px 10px",
                border: "1px solid #ced4da",
                borderRadius: "4px",
                width: "80px",
              }}
            />
          </div>

          <div>
            <label style={{ marginRight: "8px", fontSize: "14px" }}>
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={e => setAutoRefresh(e.target.checked)}
                style={{ marginRight: "4px" }}
              />
              Auto-refresh
            </label>
          </div>

          {autoRefresh && (
            <div>
              <label style={{ marginRight: "8px", fontSize: "14px" }}>
                Intervalo (ms):
              </label>
              <input
                type="number"
                value={refreshInterval}
                onChange={e => setRefreshInterval(Number(e.target.value))}
                min="1000"
                step="1000"
                style={{
                  padding: "6px 10px",
                  border: "1px solid #ced4da",
                  borderRadius: "4px",
                  width: "100px",
                }}
              />
            </div>
          )}
        </div>

        <div
          style={{
            marginTop: "15px",
            padding: "10px",
            backgroundColor: "#e7f3ff",
            borderRadius: "4px",
            fontSize: "13px",
          }}
        >
          <strong>Endpoint a probar:</strong>
          <code>http://127.0.0.1:8000/api/dashboard/realtime/{facadeId}</code>
        </div>
      </div>

      <RealtimeDashboard
        facadeId={facadeId}
        autoRefresh={autoRefresh}
        refreshInterval={refreshInterval}
      />
    </div>
  );
}

export default RealtimeTestApp;
