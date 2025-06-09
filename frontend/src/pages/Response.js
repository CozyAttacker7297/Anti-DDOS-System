import React, { useEffect, useState } from "react";
import axios from "axios";

const AttackLogs = () => {
  const [attackLogs, setAttackLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const ws = new WebSocket("http://localhost:5000/api/get-attack-logs");
  const wsStats = new WebSocket("ws://localhost:5000/ws/stats");

  // Handle WebSocket connection for attack logs
  useEffect(() => {
    ws.onopen = () => {
      console.log("WebSocket for attack logs connected");
      ws.send("get_attack_logs"); // Request to get attack logs from backend
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "new_log") {
        setAttackLogs((prevLogs) => [data.log, ...prevLogs]); // Add new log
      } else if (data.type === "deleted_log") {
        setAttackLogs((prevLogs) =>
          prevLogs.filter((log) => log.id !== data.logId) // Remove deleted log
        );
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket for attack logs disconnected");
    };

    return () => {
      ws.close();
    };
  }, []);

  // Handle WebSocket connection for stats updates
  useEffect(() => {
    wsStats.onopen = () => {
      console.log("WebSocket for stats connected");
      wsStats.send("get_stats"); // Request to get system stats from backend
    };

    wsStats.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Stats data:", data);
      // Handle stats data updates here
    };

    wsStats.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsStats.onclose = () => {
      console.log("WebSocket for stats disconnected");
    };

    return () => {
      wsStats.close();
    };
  }, []);

  // Fetch attack logs initially from backend
  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get("http://localhost:5000/api/get-attack-logs");
      setAttackLogs(response.data);
    } catch (error) {
      console.error("Error fetching attack logs:", error);
    } finally {
      setLoading(false);
    }
  };

  // Add a new attack log sample (POST request)
  const handleAddSample = async () => {
    try {
      setAdding(true);
      await axios.post("http://localhost:5000/api/add-sample");
    } catch (error) {
      console.error("Error adding sample attack log:", error);
    } finally {
      setAdding(false);
    }
  };

  // Delete an attack log (DELETE request)
  const handleDelete = async (logId) => {
    if (!window.confirm("Are you sure you want to delete this log?")) return;

    try {
      setDeletingId(logId);
      await axios.delete(`http://localhost:5000/api/attack-logs/${logId}`);
    } catch (error) {
      console.error("Error deleting attack log:", error);
    } finally {
      setDeletingId(null);
    }
  };

  useEffect(() => {
    fetchLogs(); // Fetch logs on initial load
  }, []);

  if (loading) {
    return <p>Loading attack logs...</p>;
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>Attack Logs</h2>

      <button
        onClick={handleAddSample}
        disabled={adding}
        style={{
          padding: "10px 20px",
          backgroundColor: "#3182ce",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: adding ? "not-allowed" : "pointer",
          marginBottom: "20px",
        }}
      >
        {adding ? "Adding..." : "Add Sample Log"}
      </button>

      {attackLogs.length === 0 ? (
        <p>No attack logs found.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ backgroundColor: "#f7fafc" }}>
            <tr>
              <th style={thTdStyle}>Timestamp</th>
              <th style={thTdStyle}>Type</th>
              <th style={thTdStyle}>Source IP</th>
              <th style={thTdStyle}>Target</th>
              <th style={thTdStyle}>Severity</th>
              <th style={thTdStyle}>Action</th>
              <th style={thTdStyle}>Delete</th>
            </tr>
          </thead>
          <tbody>
            {attackLogs.map((log) => (
              <tr key={log.id} style={{ backgroundColor: "#fff" }}>
                <td style={thTdStyle}>{new Date(log.timestamp).toLocaleString()}</td>
                <td style={thTdStyle}>{log.type}</td>
                <td style={thTdStyle}>{log.source_ip}</td>
                <td style={thTdStyle}>{log.target}</td>
                <td style={thTdStyle}>{log.severity}</td>
                <td style={thTdStyle}>{log.action}</td>
                <td style={thTdStyle}>
                  <button
                    onClick={() => handleDelete(log.id)}
                    disabled={deletingId === log.id}
                    style={{
                      backgroundColor: "#e53e3e",
                      color: "white",
                      border: "none",
                      padding: "6px 12px",
                      borderRadius: "4px",
                      cursor: deletingId === log.id ? "not-allowed" : "pointer",
                    }}
                  >
                    {deletingId === log.id ? "Deleting..." : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// Style for table cells and headers
const thTdStyle = {
  border: "1px solid #ccc",
  padding: "8px",
  textAlign: "left",
  fontSize: "14px",
};

export default AttackLogs;
