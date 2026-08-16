import "./SupportedFormats.css";
import { FaFilePdf, FaFileWord, FaFileAlt } from "react-icons/fa";

function SupportedFormats() {

    return(

        <div className="formats card">

            <h3>

                Supported Formats

            </h3>

            <div className="format-list">

                <div className="format">

                    <FaFilePdf/>

                    <span>PDF</span>

                </div>

                <div className="format">

                    <FaFileWord/>

                    <span>DOCX</span>

                </div>

                <div className="format">

                    <FaFileAlt/>

                    <span>TXT</span>

                </div>

            </div>

        </div>

    )

}

export default SupportedFormats;