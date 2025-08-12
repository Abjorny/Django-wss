import Camera from "./components/Camera/Camera"
import { useState } from "react"

function App() {
  const [page, setPage] = useState("camera");

  const pages = {
    "camera" : <Camera />
  }
  return (
    <>
      <div class="container-navigator">
        <div class="navigrator active" data-value="container-camera">Камера</div>
      </div>

      <div id="container-camera">
        {pages[page]}
      </div>

    </>
  )
}

export default App
