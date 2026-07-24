import { useState } from "react";
import { FaChevronDown, FaChevronUp } from "react-icons/fa";
import "./Accordion.css";

function Accordion({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="accordion card">

      <div
        className="accordion-header"
        onClick={() => setOpen(!open)}
      >
        <h3>{title}</h3>

        {open ? <FaChevronUp /> : <FaChevronDown />}
      </div>

      {open && (
        <div className="accordion-body">
          {children}
        </div>
      )}

    </div>
  );
}

export default Accordion;