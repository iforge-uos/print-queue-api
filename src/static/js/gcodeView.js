import React from 'react';
import { GCodeViewer } from "react-gcode-viewer";
import { useLocation } from "react-router-dom";


function useQuery() {
    const { search } = useLocation();
    return React.useMemo(() => new URLSearchParams(search), [search]);
}


let GCodeRenderer = () => {
    let query = useQuery();
    return (
        <div>
            <GCodeViewer
                className="viewer align-items-center row mx-auto"
                orbitControls
                url={query.get("gcode_url")}
            />
        </div>
    );

}

export default GCodeRenderer;