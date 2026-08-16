import { useEffect, useState } from "react";
import { FaServer, FaCircle } from "react-icons/fa";
import "./StatusCard.css";
import { checkBackend } from "../services/api";

function StatusCard() {
  const [status, setStatus] = useState("Checking...");
  const [online, setOnline] = useState(false);
  const [lastChecked, setLastChecked] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const response = await checkBackend();

      if (response.data.status === "Running") {
        setStatus("Backend Online");
        setOnline(true);
      } else {
        setStatus("Backend Offline");
        setOnline(false);
      }
    } catch (error) {
      console.error("Health Check Failed:", error);
      setStatus("Backend Offline");
      setOnline(false);
    } finally {
      setLoading(false);
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    fetchStatus();

    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-card card">
      <div className="status-left">
        <div className="status-icon">
          <FaServer />
        </div>

        <div>
          <h3>Backend Status</h3>

          <p>{loading ? "Checking backend..." : status}</p>

          {!loading && (
            <small>Last checked: {lastChecked}</small>
          )}
        </div>
      </div>

      <div
        className={`status-badge ${online ? "online" : "offline"}`}
      >
        <FaCircle className="status-dot" />
        {online ? "Online" : "Offline"}
      </div>
    </div>
  );
}

export default StatusCard;