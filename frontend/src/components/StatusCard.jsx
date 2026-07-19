import "./StatusCard.css";
import { FaServer } from "react-icons/fa";

function StatusCard() {
  return (
    <div className="status-card card">
      <div className="status-left">
        <div className="status-icon">
          <FaServer />
        </div>

        <div>
          <h3>Backend Status</h3>
          <p>Waiting for backend connection...</p>
        </div>
      </div>

      <div className="status-badge">
        Offline
      </div>
    </div>
  );
}

export default StatusCard;