import "./AIProcessing.css";

import {
  FaUpload,
  FaFileAlt,
  FaSearch,
  FaMagic,
  FaLayerGroup,
  FaBrain,
  FaDatabase,
  FaComments,
} from "react-icons/fa";

const steps = [
  {
    icon: <FaUpload />,
    title: "Upload",
    description: "Receive document",
  },
  {
    icon: <FaFileAlt />,
    title: "Parse",
    description: "Extract text",
  },
  {
    icon: <FaSearch />,
    title: "OCR",
    description: "Scan images",
  },
  {
    icon: <FaMagic />,
    title: "Clean",
    description: "Normalize content",
  },
  {
    icon: <FaLayerGroup />,
    title: "Chunk",
    description: "Split knowledge",
  },
  {
    icon: <FaBrain />,
    title: "Embed",
    description: "Generate vectors",
  },
  {
    icon: <FaDatabase />,
    title: "Store",
    description: "Save to Qdrant",
  },
  {
    icon: <FaComments />,
    title: "Ready",
    description: "Search & Retrieval",
  },
];

function AIProcessing() {
  return (
    <section className="pipeline-section card">

      <div className="pipeline-heading">

        <span>AI Processing Workflow</span>

        <h2>

          How OmniBrain Understands Your Documents

        </h2>

        <p>

          Every uploaded document passes through multiple AI-powered stages
          before becoming part of your searchable knowledge base.

        </p>

      </div>

      <div className="workflow">

        {steps.map((step, index) => (

          <div
            className="workflow-step"
            key={index}
          >

            <div className="workflow-icon">

              {step.icon}

            </div>

            <div className="workflow-content">

              <h3>{step.title}</h3>

              <p>{step.description}</p>

            </div>

            {index !== steps.length - 1 && (

              <div className="workflow-line"></div>

            )}

          </div>

        ))}

      </div>

    </section>
  );
}

export default AIProcessing;