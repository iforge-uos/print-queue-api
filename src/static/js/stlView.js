import React from 'react';
import { StlViewer } from "react-stl-viewer";
import { BrowserRouter as Router, useLocation, useSearchParams } from "react-router-dom";


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
    //TODO Add failsafes
    let query = useQuery()
    let useShadows = query.get('shadows').toLowerCase() == 'true';
    return (
        <div>
            <StlViewer
                className="stlviewer align-items-center row mx-auto"
                orbitControls
                shadows={useShadows}
                url={query.get("stl_url")}
            />
            
        </div>
    );
}
