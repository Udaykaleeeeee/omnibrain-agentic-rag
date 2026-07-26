import "./RecentDocuments.css";

import {
  FaFilePdf,
  FaArrowRight,
  FaClock,
} from "react-icons/fa";

function RecentDocuments() {

  const documents = [
    {
      name: "Resume.pdf",
      pages: 14,
      time: "2 mins ago",
      status: "Ready",
    },
    {
      name: "Research Paper.pdf",
      pages: 28,
      time: "Yesterday",
      status: "Processing",
    },
  ];

  return (

    <section className="recent-documents card fade">

      <div className="recent-header">

        <div>

          <h2>

            Recent Documents

          </h2>

          <p>

            Recently processed knowledge sources.

          </p>

        </div>

        <button>

          View All

          <FaArrowRight />

        </button>

      </div>

      <div className="document-list">

        {documents.map((doc, index) => (

          <div
            className="document-card"
            key={index}
          >

            <div className="document-left">

              <div className="pdf-icon">

                <FaFilePdf />

              </div>

              <div>

                <h3>

                  {doc.name}

                </h3>

                <span>

                  PDF • {doc.pages} Pages

                </span>

              </div>

            </div>

            <div className="document-right">

              <div className="time">

                <FaClock />

                {doc.time}

              </div>

              <span
                className={
                  doc.status === "Ready"
                    ? "ready"
                    : "processing"
                }
              >

                {doc.status}

              </span>

            </div>

          </div>

        ))}

      </div>

    </section>

  );
}

export default RecentDocuments;