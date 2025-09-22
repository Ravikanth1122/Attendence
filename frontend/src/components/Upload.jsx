import React, { useState } from 'react';
import axios from 'axios';
export default function Upload(){
  const [file, setFile] = useState(null);
  const [date, setDate] = useState('');
  const [resu, setResu] = useState(null);
  const submit = async (e) => {
    e.preventDefault();
    if(!file) return;
    const fd = new FormData(); fd.append('file', file); if(date) fd.append('date_str', date);
    try{
      const res = await axios.post((import.meta.env.VITE_API_BASE||'http://localhost:8000') + '/upload_class_photo', fd);
      setResu(res.data);
    }catch(err){ alert(err.response?.data?.detail || err.message); }
  };
  return (
    <div>
      <h3>Upload Class Photo</h3>
      <form onSubmit={submit}>
        <input type='file' accept='image/*' capture='environment' onChange={e=>setFile(e.target.files[0])} /><br/>
        <input type='date' value={date} onChange={e=>setDate(e.target.value)} /><br/>
        <button className='btn' type='submit'>Process</button>
      </form>
      {resu && <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(resu, null, 2)}</pre>}
    </div>
  )
}