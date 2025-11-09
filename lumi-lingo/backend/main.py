from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="LumiLingo API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data structures
class Exercise(BaseModel):
    id: int
    type: str
    question: str
    options: Optional[List[str]] = None
    answer: str
    language: str

class UserProgress(BaseModel):
    user_id: str
    exercise_id: int
    completed: bool
    score: Optional[int] = None

# Sample in-memory data (will be replaced with database)
sample_exercises = [
    Exercise(
        id=1,
        type="multiple_choice",
        question="What is 'hello' in French?",
        options=["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
        answer="Bonjour",
        language="French"
    ),
    Exercise(
        id=2,
        type="translation",
        question="Translate to French: 'Good morning'",
        answer="Bonjour",
        language="French"
    )
]

sample_progress = []

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to LumiLingo API"}

@app.get("/exercises", response_model=List[Exercise])
async def get_exercises():
    return sample_exercises

@app.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: int):
    for exercise in sample_exercises:
        if exercise.id == exercise_id:
            return exercise
    return {"error": "Exercise not found"}

@app.post("/progress")
async def update_progress(progress: UserProgress):
    # In a real app, this would save to a database
    sample_progress.append(progress)
    return {"message": "Progress updated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
