import Camera from "./components/Camera/Camera";
import Stereo from "./components/Stereo/Stereo";
import { useState } from "react";

function App() {
  const [page, setPage] = useState("camera");

  const pages = {
    "camera": {
      value: <Camera />,
      text: "Камера",
    },
    "stereo": {
      value: <Stereo />,
      text: "Стерео",
    },
  };

  return (
    <>
      <div className="container-navigator">
        {Object.entries(pages).map(([key, { text }]) => (
          <div
            key={key}
            className={`navigator ${page === key ? "active" : ""}`}
            onClick={() => setPage(key)}
          >
            {text}
          </div>
        ))}
      </div>

      <div id="container-camera">
        {pages[page].value}
      </div>
    </>
  );
}

export default App;
