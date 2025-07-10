# FHIR Natural Language Query UI

This frontend application provides a simple, user-friendly interface for querying healthcare data using natural language. It connects to a simulated FHIR backend and displays structured data results.

## Features

- Input field for natural language healthcare queries
- Auto-suggestion and auto-complete for queries (optional)
- Displays patient data and statistics in:
  - A dynamic chart (e.g., bar or pie)
  - A data table with patient name, age, and condition
- Responsive and clean UI built with React and TypeScript

## Technologies Used


- React
- TypeScript
- Chart.js or Recharts for data visualization
- Tailwind CSS or CSS Modules for styling (if applicable)
- Axios for HTTP requests (optional)

## Setup Instructions


1. **Install dependencies:**
   ```bash
   npm install
   npm run dev

2. **Run Docker:**

docker-compose down -v --remove-orphans
docker-compose build --no-cache
docker-compose up
