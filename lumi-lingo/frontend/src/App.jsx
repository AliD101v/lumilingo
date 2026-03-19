import React, { useState, useEffect } from 'react'

function App() {
  const [exercises, setExercises] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [csrfToken, setCsrfToken] = useState('')
  const [checkingAnswer, setCheckingAnswer] = useState(false)

  useEffect(() => {
    // Fetch CSRF token first
    const fetchCsrfToken = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/csrf-token`, {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setCsrfToken(data.csrf_token)
        }
      } catch (err) {
        console.error('Failed to fetch CSRF token:', err)
      }
    }

    // Fetch exercises from backend
    const fetchExercises = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/exercises`)
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

    fetchCsrfToken()
    fetchExercises()
  }, [])

  if (loading) return <div className="loading">Loading exercises...</div>
  if (error) return <div className="error">Error: {error}</div>

  // Handle answer selection for the first exercise
  const handleAnswerSelect = (answer) => {
    if (showFeedback) return; // Don't allow changing answer after submission
    
    setSelectedAnswer(answer);
  }

  // Submit the answer for the first exercise
  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null || !csrfToken) return;
    
    setCheckingAnswer(true);
    
    const firstExercise = exercises[0];
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/check-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify({
          exercise_id: firstExercise.id,
          user_answer: selectedAnswer
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to check answer')
      }
      
      const data = await response.json()
      
      setIsCorrect(data.is_correct);
      setShowFeedback(true);
      
      // Show explanation if answer is wrong and explanation is provided
      if (!data.is_correct && data.explanation) {
        setShowExplanation(true);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setCheckingAnswer(false);
    }
  }

  // Reset the exercise to allow re-attempt
  const handleResetExercise = () => {
    setSelectedAnswer(null);
    setShowFeedback(false);
    setIsCorrect(false);
    setShowExplanation(false);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>LumiLingo - Language Learning App</h1>
      </header>
      <main className="app-main">
        <h2>Exercises</h2>
        {exercises.length > 0 ? (
          <div className="exercises-list">
            {exercises.map((exercise, index) => (
              <div key={exercise.id} className="exercise-card">
                <h3>{exercise.question}</h3>
                <p>Language: {exercise.language}</p>
                
                {/* Only make the first exercise interactive */}
                {index === 0 && exercise.type === 'multiple_choice' && exercise.options ? (
                  <div className="interactive-exercise">
                    <div className="options">
                      <p>Options:</p>
                      <ul>
                        {exercise.options.map((option, index) => (
                          <li key={index}>
                            <button
                              className={`option-button ${selectedAnswer === option ? 'selected' : ''}
                                ${showFeedback && selectedAnswer === option ? (isCorrect ? 'correct' : 'incorrect') : ''}`}
                              onClick={() => handleAnswerSelect(option)}
                              disabled={showFeedback}
                            >
                              {option}
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {/* Feedback and explanation */}
                    {showFeedback && (
                      <div className={`feedback ${isCorrect ? 'correct' : 'incorrect'}`}>
                        <p>{isCorrect ? 'Correct! Well done.' : 'Incorrect. Try again!'}</p>
                        {showExplanation && exercise.explanation && (
                          <div className="explanation">
                            <p><strong>Explanation:</strong> {exercise.explanation}</p>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Submit button */}
                    {!showFeedback && (
                      <button 
                        className="submit-button"
                        onClick={handleSubmitAnswer}
                        disabled={selectedAnswer === null}
                      >
                        Submit Answer
                      </button>
                    )}
                    
                    {/* Reset button */}
                    {showFeedback && (
                      <button 
                        className="reset-button"
                        onClick={handleResetExercise}
                      >
                        Try Again
                      </button>
                    )}
                  </div>
                ) : index === 0 && exercise.type === 'multiple_choice' && exercise.options ? (
                  // Fallback for first exercise if it's multiple choice but without interactive logic
                  <div className="options">
                    <p>Options:</p>
                    <ul>
                      {exercise.options.map((option, index) => (
                        <li key={index}>{option}</li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  // For non-first exercises or non-multiple choice exercises
                  <>
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
                  </>
                )}
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
