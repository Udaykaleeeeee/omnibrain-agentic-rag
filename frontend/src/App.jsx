import "./App.css";
import "react-toastify/dist/ReactToastify.css";
import ChatInterface from "./components/ChatInterface";
import { ToastContainer } from "react-toastify";
import { useState } from "react";

import Navbar from "./components/Navbar";
import Header from "./components/Header";
import UploadSection from "./components/UploadSection";
import AIProcessing from "./components/AIProcessing";
import RecentDocuments from "./components/RecentDocuments";
import DocumentInsights from "./components/DocumentInsights";
import StatusCard from "./components/StatusCard";

function App() {
  const [selectedDocument, setSelectedDocument] = useState(null);
  return (
    <div className="app">
      <div className="container">

        <Navbar />

        <Header />

        <section id="upload">
          <UploadSection />
        </section>
        <section id="chat">
          <ChatInterface />
        </section>

        <section id="pipeline">
          <AIProcessing />
        </section>

       <section id="documents">
  <RecentDocuments
    selectedDocument={selectedDocument}
    setSelectedDocument={setSelectedDocument}
  />
</section>

<section id="overview">
  <DocumentInsights
    selectedDocument={selectedDocument}
  />
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