import React from 'react';
import { GCodeViewer } from "react-gcode-viewer";
import { useLocation } from "react-router-dom";


function useQuery() {
    const { search } = useLocation();
    return React.useMemo(() => new URLSearchParams(search), [search]);
}


let GCodeRenderer = () => {
    let query = useQuery();
    var fprop = {
        gridWidth: 2,
        gridHeight: 2
    }
    return (
        <div>
            <GCodeViewer
                className="viewer align-items-center row mx-auto"
                orbitControls
                quality={0.7}
                floorProps={fprop}
                layerColor={'cyan'}
                url={query.get("gcode_url")}
            />
        </div>
    );

}

export default GCodeRenderer;