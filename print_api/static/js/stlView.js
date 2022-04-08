import React from 'react';
import { StlViewer } from "react-stl-viewer";
import { useLocation } from "react-router-dom";


function useQuery() {
    const { search } = useLocation();
    return React.useMemo(() => new URLSearchParams(search), [search]);
}

let STLRenderer = () => {
    let query = useQuery()
    let useShadows = query.get('shadows').toLowerCase() == 'true';
    return (
        <StlViewer
            className="viewer align-items-center row mx-auto"
            orbitControls
            shadows={useShadows}
            showAxes
            url={query.get("stl_url")}
        />
    );
}

export default STLRenderer;
