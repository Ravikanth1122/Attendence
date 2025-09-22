import React, { useEffect, useState } from 'react';
import axios from 'axios';
export default function Students(){
  const [list, setList] = useState([]);
  useEffect(()=>{ load() }, []);
  async function load(){ const r = await axios.get((import.meta.env.VITE_API_BASE||'http://localhost:8000') + '/students'); setList(r.data); }
  async function onDelete(id){ if(!confirm('Delete?')) return; await axios.delete((import.meta.env.VITE_API_BASE||'http://localhost:8000') + '/students/' + id); load(); }
  return (
    <div>
      <h3>Students</h3>
      <table><thead><tr><th>Name</th><th>Roll</th><th>Action</th></tr></thead>
        <tbody>{list.map(s=>(<tr key={s.id}><td>{s.name}</td><td>{s.roll}</td><td><button onClick={()=>onDelete(s.id)}>Delete</button></td></tr>))}</tbody>
      </table>
    </div>
  )
}