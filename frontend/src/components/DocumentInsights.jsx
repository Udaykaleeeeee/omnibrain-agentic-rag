import Accordion from "./Accordion";
import {
  FaFilePdf,
  FaLayerGroup,
  FaSearch,
  FaCheckCircle,
  FaFileAlt,
} from "react-icons/fa";

import "./DocumentInsights.css";

function DocumentInsights() {
  return (
    <Accordion title="Document Overview">

      <div className="overview-grid">

        <div className="overview-card">

          <FaFilePdf />

          <h2>Resume.pdf</h2>

          <p>Selected Document</p>

        </div>

        <div className="overview-card">

          <FaFileAlt />

          <h2>14</h2>

          <p>Total Pages</p>

        </div>

        <div className="overview-card">

          <FaSearch />

          <h2>2</h2>

          <p>OCR Pages</p>

        </div>

        <div className="overview-card">

          <FaLayerGroup />

          <h2>38</h2>

          <p>Chunks Created</p>

        </div>

        <div className="overview-card">

          <FaCheckCircle />

          <h2>Ready</h2>

          <p>Status</p>

        </div>

      </div>

    </Accordion>
  );
}

export default DocumentInsights;