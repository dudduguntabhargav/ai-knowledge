# AI Knowledge Platform

A ChatGPT-like document Q&A system that allows users to upload documents and ask questions about them using advanced Retrieval-Augmented Generation (RAG) technology.

## Features

- **Document Upload & Processing**: Upload PDF, DOCX, TXT, and MD files
- **Intelligent Q&A**: Ask questions about your documents and get accurate, context-aware answers
- **Real-time Streaming**: Token-by-token response streaming for a ChatGPT-like experience
- **User Authentication**: Secure JWT-based authentication with session management
- **Chat History**: Persistent conversation tracking per user
- **Multi-Document Support**: Manage and query multiple documents
- **Vector Search**: Powered by ChromaDB for fast semantic search
- **GPT-4 Integration**: Uses OpenAI GPT-4o-mini for high-quality responses

## Architecture

This is a three-tier microservices architecture:

```
Frontend (React)          Port 5173
    ↓
Go Backend (API Gateway)  Port 8080
    ↓
Python RAG Service        Port 8000
    ↓
MongoDB + ChromaDB + OpenAI
```

### Tech Stack

**Frontend:**
- React 19
- Vite 5
- Tailwind CSS 3
- React Router 6
- Axios

**Backend (API Gateway):**
- Go 1.25.2
- Gin Framework
- JWT Authentication
- MongoDB Driver

**AI Service:**
- Python 3.10+
- FastAPI
- LangChain
- ChromaDB
- OpenAI API

**Databases:**
- MongoDB (user data, sessions, chat history)
- ChromaDB (vector embeddings)

## Prerequisites

Before running the application, ensure you have the following installed:

- **Node.js** 18 or higher
- **Go** 1.25.2 or higher
- **Python** 3.10 or higher
- **MongoDB** running on `localhost:27017`
- **OpenAI API Key** (get one from [OpenAI Platform](https://platform.openai.com))

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-knowledge
```

### 2. Set Up Environment Variables

**Backend Go Service (`backend/.env`):**
```env
APP_PORT=8080
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_knowledge
JWT_SECRET=your-secret-key-here
PYTHON_AI_URL=http://localhost:8000
```

**Python RAG Service (`backend/python_service/.env`):**
```env
OPENAI_API_KEY=sk-proj-your-key-here
MONGO_URI=mongodb://localhost:27017
```

**Frontend (`frontend/.env`):**
```env
VITE_API_URL=http://localhost:8080/api/v1
```

### 3. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Go Backend:**
```bash
cd backend
go mod tidy
```

**Python Service:**
```bash
cd backend/python_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

You need to run all three services simultaneously in separate terminal windows:

### Terminal 1 - Frontend

```bash
cd frontend
npm run dev
```

Access at: http://localhost:5173

### Terminal 2 - Go Backend

```bash
cd backend
go run cmd/server/main.go
```

Runs on: http://localhost:8080

### Terminal 3 - Python RAG Service

```bash
cd backend/python_service
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app:app --reload --port 8000
```

Runs on: http://localhost:8000

## Usage

1. **Register/Login**: Create an account or login at http://localhost:5173
2. **Upload Document**: Click the upload button to add PDF, DOCX, TXT, or MD files
3. **Ask Questions**: Type your questions about the uploaded documents
4. **Get Answers**: Receive AI-generated answers with source citations
5. **View History**: Access your chat history and uploaded documents

## API Endpoints

### Public Endpoints
- `POST /api/v1/register` - Register new user
- `POST /api/v1/login` - User login

### Protected Endpoints (JWT Required)
- `POST /api/v1/logout` - Logout user
- `GET /api/v1/me` - Get current user info
- `POST /api/v1/upload` - Upload document
- `POST /api/v1/query` - Query documents (non-streaming)
- `POST /api/v1/query-stream` - Query with streaming response
- `POST /api/v1/upload-and-query` - Upload and query in one request
- `GET /api/v1/conversations` - Get chat history
- `DELETE /api/v1/conversations` - Clear chat history
- `GET /api/v1/documents` - List uploaded documents

## Project Structure

```
ai-knowledge/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── context/       # Context providers
│   │   └── pages/         # Page components
│   └── package.json
│
├── backend/               # Go backend
│   ├── cmd/server/        # Entry point
│   ├── internal/
│   │   ├── handler/       # HTTP handlers
│   │   ├── service/       # Business logic
│   │   ├── repository/    # Database layer
│   │   ├── middleware/    # Auth, CORS, etc.
│   │   └── models/        # Data models
│   ├── python_service/    # Python RAG service
│   │   ├── app.py         # FastAPI app
│   │   ├── rag_pipeline.py # RAG logic
│   │   └── vectorstore/   # ChromaDB storage
│   └── go.mod
│
└── README.md
```

## Key Features Explained

### RAG (Retrieval-Augmented Generation)
The system uses RAG to provide accurate answers:
1. Documents are split into chunks and converted to embeddings
2. User queries are matched against relevant chunks using vector search
3. Retrieved context is sent to GPT-4o-mini for answer generation
4. Answers include source citations for transparency

### Streaming Responses
Regular queries use Server-Sent Events (SSE) to stream responses token-by-token, providing a real-time ChatGPT-like experience.

### Authentication Flow
- JWT tokens with 24-hour expiry
- Session tracking in MongoDB for immediate logout capability
- Password hashing with bcrypt
- Protected routes via middleware

## Development

### Frontend Commands
```bash
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Commands
```bash
go run cmd/server/main.go              # Run server
go build -o bin/server cmd/server/main.go   # Build binary
go mod tidy                            # Update dependencies
```

### Python Service Commands
```bash
uvicorn app:app --reload --port 8000   # Development mode
uvicorn app:app --port 8000 --workers 4  # Production mode
```

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongod` or use Docker: `docker run -d -p 27017:27017 mongo`

**OpenAI API Error:**
- Verify your API key is correctly set in `backend/python_service/.env`
- Check your OpenAI account has sufficient credits

**Streaming Not Working:**
- This is expected for file upload queries (they use non-streaming endpoint)
- Regular queries without file uploads should stream responses

**Port Already in Use:**
- Check if another process is using ports 5173, 8080, or 8000
- Kill the process or change ports in environment files

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
