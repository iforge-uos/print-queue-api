import React from 'react';
import ReactDOM from 'react-dom';
import {StlViewer} from "react-stl-viewer";

const url = "https://storage.googleapis.com/ucloud-v3/ccab50f18fb14c91ccca300a.stl"


function App() {
    return (
        <StlViewer
            class ="stlviewer align-items-center row mx-auto"
            orbitControls
            shadows
            url={url}
        />
    );
}

ReactDOM.render(<App />, document.getElementById('react-root'));