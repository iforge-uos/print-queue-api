import React from 'react';
import { StlViewer } from "react-stl-viewer";
import { BrowserRouter as Router, useLocation } from "react-router-dom";


function useQuery() {
    const { search } = useLocation();
    return React.useMemo(() => new URLSearchParams(search), [search]);
}

export default function STLViewerBase() {
    return (
      <Router>
        <App />
      </Router>
    );
}

function App() {
    let query = useQuery()
    return (
        <StlViewer
            className="stlviewer align-items-center row mx-auto"
            orbitControls
            //shadows
            url={query.get("stl_url")}
        />
    );
}
