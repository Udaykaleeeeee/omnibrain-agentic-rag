import "./App.css";
import "react-toastify/dist/ReactToastify.css";

import { ToastContainer } from "react-toastify";

import Navbar from "./components/Navbar";
import Header from "./components/Header";
import UploadSection from "./components/UploadSection";
import AIProcessing from "./components/AIProcessing";
import RecentDocuments from "./components/RecentDocuments";
import DocumentInsights from "./components/DocumentInsights";
import StatusCard from "./components/StatusCard";

function App() {
  return (
    <div className="app">
      <div className="container">

        <Navbar />

        <Header />

        <section id="upload">
          <UploadSection />
        </section>

        <section id="pipeline">
          <AIProcessing />
        </section>

        <section id="documents">
          <RecentDocuments />
        </section>

        <section id="overview">
          <DocumentInsights />
        </section>

        <section id="status">
          <StatusCard />
        </section>

      </div>

      <ToastContainer
        position="top-right"
        autoClose={3000}
        newestOnTop
        closeOnClick
        pauseOnHover
        draggable
        theme="light"
      />

    </div>
  );
}

export default App;