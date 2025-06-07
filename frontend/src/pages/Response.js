import React, { useEffect, useState } from "react";
import { getAttackLogs } from "../services/api";
import axios from "axios";

export default function Response() {
  const [attackLogs, setAttackLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  async function fetchLogs() {
    try {
      setLoading(true);
      const data = await getAttackLogs();
      console.log("Backend connected successfully", data);
      setAttackLogs(data);
    } catch (error) {
      console.error("Failed to fetch attack logs", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLogs();
  }, []);

  async function handleAddSample() {
    try {
      setAdding(true);
      await axios.post("http://localhost:8000/api/add-sample");
      await fetchLogs(); // refresh list after adding
    } catch (error) {
      console.error("Failed to add sample attack log", error);
    } finally {
      setAdding(false);
    }
  }

  async function handleDelete(logId) {
    if (!window.confirm("Are you sure you want to delete this attack log?")) return;
    try {
      setDeletingId(logId);
      await axios.delete(`http://localhost:8000/api/attack-logs/${logId}`);
      await fetchLogs(); // refresh list after deletion
    } catch (error) {
      console.error("Failed to delete attack log", error);
    } finally {
      setDeletingId(null);
    }
  }

  const thTdStyle = {
    border: "1px solid #ccc",
    padding: "8px",
    textAlign: "left",
  };

  if (loading) return <p>Loading attack logs...</p>;

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif" }}>
      <h2 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "16px" }}>
        Response Management
      </h2>

      <button
        onClick={handleAddSample}
        disabled={adding}
        style={{
          marginBottom: "16px",
          padding: "10px 20px",
          backgroundColor: "#3182ce",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: adding ? "not-allowed" : "pointer",
        }}
      >
        {adding ? "Adding Sample..." : "Add Sample Attack Log"}
      </button>

      {attackLogs.length === 0 ? (
        <p>No attack logs found.</p>
      ) : (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead style={{ backgroundColor: "#f7fafc" }}>
            <tr>
              <th style={thTdStyle}>Timestamp</th>
              <th style={thTdStyle}>Type</th>
              <th style={thTdStyle}>Source IP</th>
              <th style={thTdStyle}>Target</th>
              <th style={thTdStyle}>Severity</th>
              <th style={thTdStyle}>Action Taken</th>
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
}
