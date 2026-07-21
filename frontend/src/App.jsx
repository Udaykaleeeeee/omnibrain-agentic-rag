import "./App.css";

import Header from "./components/Header";
import StatusCard from "./components/StatusCard";
import SupportedFormats from "./components/SupportedFormats";
import UploadSection from "./components/UploadSection";

function App() {
  return (
    <div className="app">
      <Header />
      <div className="sections">
        <StatusCard />
        <SupportedFormats />
        <UploadSection />
      </div>
    </div>
  );
}

export default App;