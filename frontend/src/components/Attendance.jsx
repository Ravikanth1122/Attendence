import React, { useState } from 'react';
import axios from 'axios';
export default function Attendance(){
  const [date, setDate] = useState('');
  const [data, setData] = useState(null);
  async function fetch(){ const r = await axios.get((import.meta.env.VITE_API_BASE||'http://localhost:8000') + '/attendance_by_date', { params: { query_date: date } }); setData(r.data); }
  return (
    <div>
      <h3>Attendance by Date</h3>
      <input type='date' value={date} onChange={e=>setDate(e.target.value)} /> <button onClick={fetch}>Get</button>
      {data && <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  )
}