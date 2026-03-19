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
│   ├── pyproject.toml    # Python dependencies (managed by uv)
│   └── uv.lock         # Locked dependencies
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

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Node.js 16+
- npm 8+

### Backend Setup

```bash
cd backend
uv sync  # Install dependencies from pyproject.toml
uv run python main.py  # Run with uv
```

To install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or using pip:
pip install uv
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
