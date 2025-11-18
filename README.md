# GOVERN.AI

AI-powered governance platform for contract management, compliance tracking, and intelligent reporting.

**Developed by Xylotech**

## 🚀 Features

- 🤖 **AI Copilot**: Natural language querying for contracts, compliance, reports, and dashboard with modern chat UI
- 📄 **Contract Management**: Upload, analyze, and track contracts with AI-powered risk assessment
- ✅ **Compliance Tracking**: Monitor regulatory compliance across multiple frameworks (GDPR, ISO, SOC2, HIPAA, etc.)
- 📊 **Intelligent Reporting**: Generate and download AI-powered reports in JSON and PDF formats
- 📈 **Dashboard Analytics**: Real-time insights and KPI tracking
- 🎨 **Modern UI/UX**: Glassmorphism effects, smooth animations, and responsive design
- 🔧 **Custom AI Models**: Support for local models (Ollama, HuggingFace) with Google Gemini fallback
- 🔊 **Text-to-Speech**: Read messages aloud with browser speech synthesis
- 📋 **Message Actions**: Copy, search, download, share, and print chat messages

## 🛠️ Tech Stack

### Frontend
- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- Firebase Authentication

### Backend
- FastAPI
- Python 3.10+
- SQLAlchemy
- SQLite/PostgreSQL
- Google Gemini AI / Custom Local Models (Ollama, HuggingFace)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/XyloTech/GOVERN.AI.git
cd GOVERN.AI
```

2. Backend Setup:
```bash
cd backend
pip install -r requirements.txt
python run.py
```

3. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Start the backend server (runs on http://localhost:8000)
2. Start the frontend development server (runs on http://localhost:3000)
3. Open your browser and navigate to the frontend URL
4. Use the AI Copilot to query contracts, compliance records, and generate reports

## 🎯 Key Features

### AI Copilot
- Natural language interface for querying all platform data
- Supports file uploads (PDF, DOCX, DOC, TXT)
- Context-aware responses with source citations
- Modern chat interface with glassmorphism effects
- Message actions: copy, speech, search, download, share, print

### Custom AI Models
- Support for local models via Ollama
- HuggingFace model integration
- Fine-tuning capabilities
- Automatic fallback to Google Gemini
- See `backend/CUSTOM_MODEL_SETUP.md` for setup instructions

### Modern UI/UX
- Glassmorphism design with backdrop blur
- Smooth slide-in animations
- Enhanced avatars with gradients
- Hover effects and micro-interactions
- Fully responsive design
- Dark theme with neon accents

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL (optional, SQLite used by default)
- Git

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/XyloTech/GOVERN.AI.git
cd GOVERN.AI
```

2. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

4. **Configure Environment Variables:**
   - Create `.env` file in `backend/` directory
   - Add `GEMINI_API_KEY=your_key_here` (optional, for Gemini fallback)
   - Add Firebase configuration in `frontend/.env.local`

## 🔧 Configuration

### Custom AI Models
To use local models instead of Google Gemini:

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Update `backend/app/core/config.py`:
   ```python
   USE_CUSTOM_MODEL = True
   CUSTOM_MODEL_TYPE = "ollama"
   CUSTOM_MODEL_NAME = "llama3"
   ```

See `backend/CUSTOM_MODEL_SETUP.md` for detailed instructions.

## 📖 Usage

1. Start the backend server (runs on http://localhost:8000)
2. Start the frontend development server (runs on http://localhost:3000)
3. Open your browser and navigate to http://localhost:3000
4. Sign in with Firebase Authentication
5. Use the AI Copilot to query contracts, compliance records, and generate reports

## 💳 Payment

After 5 free queries, users are prompted to upgrade for unlimited access via Razorpay integration.

## 📁 Project Structure

```
GOVERN.AI/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── scripts/      # Utility scripts
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/         # Next.js app directory
│   ├── components/  # React components
│   └── package.json
└── README.md
```

## 🤝 Contributing

This project is developed and maintained by Xylotech. For contributions, please contact the development team.

## 📄 License

Copyright © XyloTech. All rights reserved.

## 🌐 Powered by

**xylotech.in**

---

For detailed documentation, see:
- `SETUP.md` - Detailed setup instructions
- `backend/CUSTOM_MODEL_SETUP.md` - Custom model configuration
- `PROJECT_STRUCTURE.md` - Project architecture
