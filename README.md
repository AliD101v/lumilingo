# LumiLingo - Language Learning App

LumiLingo is a cross-platform language learning application that combines curated exercises with dynamically generated content using Large Language Models (LLMs). The app is designed to be portable across desktop, mobile, and web platforms.

## Features

- **Curated Exercises**: Predefined language learning content stored in a database
- **Dynamic Exercises**: LLM-generated exercises tailored to user proficiency and learning goals
- **Cross-Platform Support**: Available as web app and mobile application
- **User Progress Tracking**: Save and track user progress with adaptive learning paths

## Project Structure

```
lumi-lingo/
├── backend/          # Python FastAPI backend
│   ├── main.py       # API endpoints and business logic
│   └── requirements.txt  # Python dependencies
├── frontend/         # React frontend
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── package.json  # Node.js dependencies
└── docs/             # Documentation
```

## Technology Stack

- **Backend**: Python, FastAPI
- **Frontend**: React (web), React Native (mobile)
- **LLM Integration**: OpenAI API or Hugging Face Transformers
- **Database**: SQLite or PostgreSQL
- **Deployment**: Docker, PWA support

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING](CONTRIBUTING.md) guide for more information.
