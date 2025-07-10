import React, { useState, useEffect } from 'react';
import { Search, Users, Activity, Filter, BarChart3, Table, AlertCircle } from 'lucide-react';

const FHIRNLPInterface = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [examples, setExamples] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    minAge: '',
    maxAge: '',
    gender: '',
    condition: ''
  });

  // Example queries for suggestions
  const exampleQueries = [
    "Show me all diabetic patients over 50",
    "Find female patients with hypertension",
    "List patients under 30 with depression",
    "Show male patients with heart disease over 65",
    "Get all active asthma patients"
  ];

  useEffect(() => {
    setExamples(exampleQueries);
  }, []);

  const handleQueryChange = (value) => {
    setQuery(value);
    
    // Generate suggestions based on input
    if (value.length > 2) {
      const matchingSuggestions = exampleQueries.filter(ex => 
        ex.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(matchingSuggestions);
    } else {
      setSuggestions([]);
    }
  };

  const processQuery = async (queryText = query) => {
    if (!queryText.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // In a real app, this would call your backend API
      // For demo purposes, we'll simulate the API response
      const simulatedResponse = await simulateAPICall(queryText);
      setResults(simulatedResponse);
    } catch (err) {
      setError('Error processing query: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const simulateAPICall = async (queryText) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Extract basic info from query for demo
    const hasAge = queryText.match(/\b(?:over|under|above|below)\s+(\d+)\b/i);
    const hasGender = queryText.match(/\b(male|female|men|women)\b/i);
    const hasCondition = queryText.match(/\b(diabetic|diabetes|hypertension|depression|heart disease|asthma)\b/i);
    
    // Generate mock data based on query
    const mockPatients = [];
    const numPatients = Math.floor(Math.random() * 10) + 5;
    
    for (let i = 0; i < numPatients; i++) {
      const age = hasAge ? 
        (queryText.includes('over') ? Math.floor(Math.random() * 30) + parseInt(hasAge[1]) : 
         Math.floor(Math.random() * parseInt(hasAge[1])) + 20) :
        Math.floor(Math.random() * 60) + 20;
      
      const gender = hasGender ? 
        (hasGender[1].toLowerCase().includes('male') ? 'male' : 'female') :
        Math.random() > 0.5 ? 'male' : 'female';
      
      const names = {
        male: ['John', 'Michael', 'David', 'Chris', 'Robert'],
        female: ['Jane', 'Sarah', 'Lisa', 'Amanda', 'Jennifer']
      };
      
      const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'];
      
      mockPatients.push({
        id: `patient-${i + 1}`,
        name: `${names[gender][Math.floor(Math.random() * names[gender].length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`,
        age,
        gender,
        condition: hasCondition ? hasCondition[1] : 'General',
        lastVisit: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      });
    }

    return {
      original_query: queryText,
      extracted_intent: {
        action: 'show',
        resource_type: 'Patient',
        filters: {
          ...(hasAge && { age: { operator: queryText.includes('over') ? '>' : '<', value: parseInt(hasAge[1]) } }),
          ...(hasGender && { gender: hasGender[1].toLowerCase().includes('male') ? 'male' : 'female' }),
          ...(hasCondition && { condition: hasCondition[1] })
        }
      },
      fhir_response: {
        resourceType: 'Bundle',
        total: mockPatients.length,
        entry: mockPatients.map(p => ({ resource: p }))
      }
    };
  };

  const getChartData = () => {
    if (!results?.fhir_response?.entry) return null;
    
    const patients = results.fhir_response.entry.map(e => e.resource);
    
    // Age distribution
    const ageGroups = {
      '20-30': 0,
      '31-40': 0,
      '41-50': 0,
      '51-60': 0,
      '61-70': 0,
      '71+': 0
    };
    
    patients.forEach(patient => {
      const age = patient.age;
      if (age <= 30) ageGroups['20-30']++;
      else if (age <= 40) ageGroups['31-40']++;
      else if (age <= 50) ageGroups['41-50']++;
      else if (age <= 60) ageGroups['51-60']++;
      else if (age <= 70) ageGroups['61-70']++;
      else ageGroups['71+']++;
    });
    
    return Object.entries(ageGroups).map(([range, count]) => ({
      range,
      count
    }));
  };

  const getGenderData = () => {
    if (!results?.fhir_response?.entry) return null;
    
    const patients = results.fhir_response.entry.map(e => e.resource);
    const genderCounts = { male: 0, female: 0 };
    
    patients.forEach(patient => {
      genderCounts[patient.gender]++;
    });
    
    return Object.entries(genderCounts).map(([gender, count]) => ({
      gender: gender.charAt(0).toUpperCase() + gender.slice(1),
      count
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI-Powered FHIR Query Interface
          </h1>
          <p className="text-gray-600">
            Ask questions about patient data in natural language
          </p>
        </div>

        {/* Query Input */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => handleQueryChange(e.target.value)}
              placeholder="e.g., Show me all diabetic patients over 50"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && processQuery()}
            />
          </div>
          
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="mt-2 bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-600 mb-2">Suggestions:</p>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(suggestion);
                    setSuggestions([]);
                  }}
                  className="block w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => processQuery()}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? (
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {loading ? 'Processing...' : 'Search'}
            </button>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>

          {/* Example Queries */}
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {examples.map((example, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(example);
                    processQuery(example);
                  }}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Query Analysis */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Query Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Original Query:</p>
                  <p className="font-medium">{results.original_query}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Extracted Intent:</p>
                  <p className="font-medium capitalize">{results.extracted_intent.action} {results.extracted_intent.resource_type}</p>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Age Distribution */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Age Distribution
                </h3>
                <div className="space-y-2">
                  {getChartData()?.map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-16 text-sm text-gray-600">{item.range}</div>
                      <div className="flex-1 bg-gray-200 rounded-full h-4">
                        <div 
                          className="bg-blue-500 h-4 rounded-full transition-all duration-500"
                          style={{ width: `${(item.count / Math.max(...getChartData().map(d => d.count))) * 100}%` }}
                        />
                      </div>
                      <div className="w-8 text-sm text-gray-700">{item.count}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gender Distribution */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Gender Distribution
                </h3>
                <div className="space-y-2">
                  {getGenderData()?.map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-16 text-sm text-gray-600">{item.gender}</div>
                      <div className="flex-1 bg-gray-200 rounded-full h-4">
                        <div 
                          className={`h-4 rounded-full transition-all duration-500 ${
                            item.gender === 'Male' ? 'bg-blue-500' : 'bg-pink-500'
                          }`}
                          style={{ width: `${(item.count / results.fhir_response.total) * 100}%` }}
                        />
                      </div>
                      <div className="w-8 text-sm text-gray-700">{item.count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Patient Table */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Table className="h-5 w-5" />
                Patient Results ({results.fhir_response.total} found)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Name</th>
                      <th className="text-left py-3 px-4">Age</th>
                      <th className="text-left py-3 px-4">Gender</th>
                      <th className="text-left py-3 px-4">Condition</th>
                      <th className="text-left py-3 px-4">Last Visit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.fhir_response.entry.map((entry, index) => (
                      <tr key={index} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{entry.resource.name}</td>
                        <td className="py-3 px-4">{entry.resource.age}</td>
                        <td className="py-3 px-4 capitalize">{entry.resource.gender}</td>
                        <td className="py-3 px-4">{entry.resource.condition}</td>
                        <td className="py-3 px-4">{entry.resource.lastVisit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FHIRNLPInterface;