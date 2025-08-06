import Camera from "./components/Camera/Camera"


function App() {

  return (
    <>
      <div class="container-navigator">
        <div class="navigrator active" data-value="container-camera">Камера</div>
      </div>

      <div id="container-camera">
         <Camera />
      </div>

    </>
  )
}

export default App
