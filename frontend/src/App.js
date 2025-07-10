import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const exampleQueries = [
    'Show me all diabetic patients over 50',
    'Find female patients with hypertension',
    'List patients under 30 with depression',
    'Show male patients with heart disease over 65',
    'Get all active asthma patients',
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch('http://localhost:5050/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error('Backend error');
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('❌ Failed to fetch data. Please check if backend is running and CORS is enabled.');
    }
  };

  const renderPatientStats = () => {
    const entries = results?.fhir_response?.entry;
    if (!entries || !Array.isArray(entries)) return <p>No patient data available.</p>;

    const genderCounts = { Male: 0, Female: 0 };
    const ageGroups = { '20–30': 0, '31–40': 0, '41–50': 0, '51–60': 0, '61–70': 0, '71+': 0 };

    for (const entry of entries) {
      const patient = entry.resource;
      const gender = patient.gender;
      const age = patient.age;

      if (gender === 'male') genderCounts.Male++;
      if (gender === 'female') genderCounts.Female++;

      if (age >= 20 && age <= 30) ageGroups['20–30']++;
      else if (age <= 40) ageGroups['31–40']++;
      else if (age <= 50) ageGroups['41–50']++;
      else if (age <= 60) ageGroups['51–60']++;
      else if (age <= 70) ageGroups['61–70']++;
      else ageGroups['71+']++;
    }

    return (
      <div className="distribution">
        <h3>📊 Age Distribution</h3>
        {Object.entries(ageGroups).map(([range, count]) => (
          <div className="bar age-group" key={range}>
            <span style={{ width: `${count * 10}%` }}>{count}</span>
          </div>
        ))}

        <h3>🧬 Gender Distribution</h3>
        <div className="bar male">
          <span style={{ width: `${genderCounts.Male * 10}%` }}>{genderCounts.Male}</span>
        </div>
        <div className="bar female">
          <span style={{ width: `${genderCounts.Female * 10}%` }}>{genderCounts.Female}</span>
        </div>

        <div className="results">
          <h3>📋 Patient Results ({entries.length} found)</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th><th>Age</th><th>Gender</th><th>Condition</th><th>Last Visit</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => {
                const p = entry.resource;
                const name = `${p.name?.[0]?.given?.[0] || '—'} ${p.name?.[0]?.family || ''}`;
                return (
                  <tr key={i}>
                    <td>{name}</td>
                    <td>{p.age}</td>
                    <td>{p.gender}</td>
                    <td>{p.conditions?.[0]?.display || '—'}</td>
                    <td>{p.birthDate}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      <h1>AI-Powered FHIR Query Interface</h1>
      <p>Ask questions about patient data in natural language.</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          placeholder="Show me all diabetic patients over 50"
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">🔍 Search</button>
      </form>

      <div className="examples">
        <p><strong>Try these examples:</strong></p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {exampleQueries.map((ex, i) => (
            <button key={i} onClick={() => setQuery(ex)}>{ex}</button>
          ))}
        </div>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {results && (
        <>
          <div className="query-analysis">
            <h3>📝 Query Analysis</h3>
            <p><strong>Original Query:</strong> {results.original_query}</p>
            <p><strong>Extracted Intent:</strong> {results.extracted_intent?.action} {results.extracted_intent?.resource_type}</p>
          </div>

          {renderPatientStats()}
        </>
      )}
    </div>
  );
}

export default App;
