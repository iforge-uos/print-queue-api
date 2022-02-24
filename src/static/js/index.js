import React from 'react';
import ReactDOM from 'react-dom';
import {StlViewer} from "react-stl-viewer";

const url = "https://storage.googleapis.com/ucloud-v3/ccab50f18fb14c91ccca300a.stl"
const _param = "pepis";

function App(param) {
    console.log(param);
    return (
        <StlViewer
            className ="stlviewer align-items-center row mx-auto"
            orbitControls
            //shadows
            url={url}
        />
    );
}

ReactDOM.render(<App param = {_param}/>, document.getElementById('react-root'));