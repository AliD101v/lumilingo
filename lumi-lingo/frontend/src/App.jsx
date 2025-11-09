import React, { useState, useEffect } from 'react'

function App() {
  const [exercises, setExercises] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Fetch exercises from backend
    const fetchExercises = async () => {
      try {
        const response = await fetch('http://localhost:8000/exercises')
        if (!response.ok) {
          throw new Error('Failed to fetch exercises')
        }
        const data = await response.json()
        setExercises(data)
        setLoading(false)
      } catch (err) {
        setError(err.message)
        setLoading(false)
      }
    }

    fetchExercises()
  }, [])

  if (loading) return <div className="loading">Loading exercises...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="app">
      <header className="app-header">
        <h1>LumiLingo - Language Learning App</h1>
      </header>
      <main className="app-main">
        <h2>Exercises</h2>
        {exercises.length > 0 ? (
          <div className="exercises-list">
            {exercises.map(exercise => (
              <div key={exercise.id} className="exercise-card">
                <h3>{exercise.question}</h3>
                <p>Language: {exercise.language}</p>
                {exercise.type === 'multiple_choice' && exercise.options && (
                  <div className="options">
                    <p>Options:</p>
                    <ul>
                      {exercise.options.map((option, index) => (
                        <li key={index}>{option}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <p>Answer: {exercise.answer}</p>
              </div>
            ))}
          </div>
        ) : (
          <p>No exercises available.</p>
        )}
      </main>
    </div>
  )
}

export default App
