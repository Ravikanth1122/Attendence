import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Enroll from './components/Enroll';
import Upload from './components/Upload';
import Students from './components/Students';
import Attendance from './components/Attendance';

export default function App(){
  return (
    <BrowserRouter>
      <div className="container">
        <nav style={{display:'flex', gap:12, marginBottom:12}}>
          <Link to="/">Home</Link>
          <Link to="/enroll">Enroll</Link>
          <Link to="/upload">Upload Photo</Link>
          <Link to="/students">Students</Link>
          <Link to="/attendance">Attendance</Link>
        </nav>
        <div className="card">
          <Routes>
            <Route path="/" element={<div><h2>Face Attendance</h2><p>Use the nav to enroll students, upload a class photo and view attendance.</p></div>} />
            <Route path="/enroll" element={<Enroll/>} />
            <Route path="/upload" element={<Upload/>} />
            <Route path="/students" element={<Students/>} />
            <Route path="/attendance" element={<Attendance/>} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}