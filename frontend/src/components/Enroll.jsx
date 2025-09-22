import React, { useState } from 'react';
import axios from 'axios';
export default function Enroll(){
  const [name, setName] = useState('');
  const [roll, setRoll] = useState('');
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState('');
  const submit = async (e) => {
    e.preventDefault();
    if(!file) { setMsg('Select a photo'); return; }
    const fd = new FormData();
    fd.append('name', name); fd.append('roll', roll); fd.append('file', file);
    try{
      const res = await axios.post((import.meta.env.VITE_API_BASE||'http://localhost:8000') + '/enroll_student', fd);
      setMsg('Enrolled: ' + res.data.name);
    }catch(err){ setMsg(err.response?.data?.detail || err.message); }
  };
  return (
    <div>
      <h3>Enroll Student</h3>
      <form onSubmit={submit}>
        <input placeholder='Name' value={name} onChange={e=>setName(e.target.value)} /><br/>
        <input placeholder='Roll' value={roll} onChange={e=>setRoll(e.target.value)} /><br/>
        <input type='file' accept='image/*' capture='environment' onChange={e=>setFile(e.target.files[0])} /><br/>
        <button className='btn' type='submit'>Enroll</button>
      </form>
      {msg && <p>{msg}</p>}
    </div>
  )
}