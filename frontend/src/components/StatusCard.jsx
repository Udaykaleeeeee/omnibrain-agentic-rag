import { useEffect, useState } from "react";
import { FaServer } from "react-icons/fa";
import "./StatusCard.css";
import { checkBackend } from "../services/api";

function StatusCard() {
  const [status, setStatus] = useState("Checking...");
  const [online, setOnline] = useState(false);

  useEffect(() => {
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
        console.error(error);
        setStatus("Backend Offline");
        setOnline(false);
      }
    };

    fetchStatus();
  }, []);

  return (
    <div className="status-card card">
      <div className="status-left">
        <div className="status-icon">
          <FaServer />
        </div>

        <div>
          <h3>Backend Status</h3>
          <p>{status}</p>
        </div>
      </div>

      <div
        className="status-badge"
        style={{
          background: online ? "#DCFCE7" : "#FEE2E2",
          color: online ? "#15803D" : "#DC2626",
        }}
      >
        {online ? "Online" : "Offline"}
      </div>
    </div>
  );
}

export default StatusCard;