
import React, { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch('http://localhost:5001/api/pipeline-data')
      .then(res => res.json())
      .then(setData);
  }, []);
  if (!data) return <div>Loading...</div>;
  return (
    <div style={{fontFamily: 'sans-serif', margin: 20}}>
      <h2>Genomics Pipeline Dashboard</h2>
      <h3>Inputs</h3>
      <ul>
        {data.inputs.map((f, i) => (
          <li key={i}>{f.filename} ({f.type}, {f.size})</li>
        ))}
      </ul>
      <h3>Outputs</h3>
      <ul>
        {data.outputs.map((f, i) => (
          <li key={i}>{f.filename} ({f.type}, {f.size})</li>
        ))}
      </ul>
      <h3>Pipeline Status</h3>
      <ol>
        {data.pipeline_status.map((s, i) => (
          <li key={i}>{s.stage}: <b>{s.status}</b></li>
        ))}
      </ol>
    </div>
  );
}
export default App;
