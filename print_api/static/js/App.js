import React from 'react';
import { Routes, Route } from 'react-router-dom';
import STLRenderer from './stlView';
import GCodeRenderer from './gcodeView'


const App = () => {
    return (
        <Routes>
            <Route exact path='/view_gcode' element={<GCodeRenderer />} />
            <Route exact path='/view_stl' element={<STLRenderer />} />
        </Routes>
    );
}

export default App;