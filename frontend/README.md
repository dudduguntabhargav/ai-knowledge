# AI Knowledge Platform - Frontend

A modern React frontend for the AI Knowledge Platform, featuring document upload and intelligent chat capabilities powered by RAG (Retrieval-Augmented Generation).

## Features

- 🔐 **Secure Authentication**: JWT-based login and registration
- 📤 **Document Upload**: Upload text documents to your knowledge base
- 💬 **AI Chat Interface**: Ask questions and get intelligent answers from your documents
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- 🔄 **Real-time Updates**: Instant feedback and smooth interactions
- 📱 **Responsive**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React Context API

## Prerequisites

- Node.js 18+ (recommended: Node 20+)
- npm or yarn
- Backend services running:
  - Go service on port 8080
  - Python service on port 8000

## Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` if needed (default values work for local development):
   ```env
   VITE_API_URL=http://localhost:8080/api/v1
   VITE_PYTHON_API_URL=http://localhost:8000
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── DocumentUpload.jsx
│   │   ├── ChatInterface.jsx
│   │   └── ProtectedRoute.jsx
│   ├── context/           # React Context providers
│   │   └── AuthContext.jsx
│   ├── pages/             # Page components
│   │   └── Dashboard.jsx
│   ├── services/          # API service layer
│   │   └── api.js
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles (Tailwind)
├── public/                # Static assets
├── .env                   # Environment variables
└── package.json           # Dependencies and scripts
```

## Usage

### 1. Register/Login

- Navigate to `http://localhost:5173`
- Create a new account or login with existing credentials
- You'll be redirected to the dashboard upon successful authentication

### 2. Upload Documents

- In the dashboard, use the upload section on the left
- Click to select a file or drag and drop
- Supported formats: TXT, PDF, MD, DOC, DOCX
- Click "Upload Document" to add it to your knowledge base

### 3. Chat with AI

- Use the chat interface on the right side of the dashboard
- Type your question in the input field
- The AI will search your uploaded documents and provide contextual answers
- Chat history is preserved for context-aware conversations

## Key Features Explained

### Authentication

- JWT tokens stored in localStorage
- Automatic token inclusion in API requests
- Automatic redirect to login on 401 errors
- Protected routes that require authentication

### Document Upload

- Multi-format support
- Real-time upload progress
- Success/error notifications
- Automatic vectorization in the backend

### AI Chat

- Real-time message display
- Loading indicators
- Source attribution for answers
- Auto-scroll to latest message
- Persistent chat history

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Go backend API URL | `http://localhost:8080/api/v1` |
| `VITE_PYTHON_API_URL` | Python RAG service URL | `http://localhost:8000` |

## Building for Production

```bash
# Create optimized production build
npm run build

# Preview the production build locally
npm run preview
```

The build output will be in the `dist/` directory.

## Deployment

### Deploy to Vercel, Netlify, or similar

1. Build the project:
   ```bash
   npm run build
   ```

2. Update environment variables in your hosting platform to point to your production backend URLs

3. Deploy the `dist/` directory

### Environment Variables for Production

Set these in your hosting platform:
```env
VITE_API_URL=https://your-backend-domain.com/api/v1
VITE_PYTHON_API_URL=https://your-python-service-domain.com
```

## Troubleshooting

### Backend Connection Issues

**Problem**: "Failed to fetch" or CORS errors

**Solution**:
- Ensure backend services are running
- Check `.env` file has correct URLs
- Verify CORS is enabled in the Go backend

### Authentication Not Working

**Problem**: Can't login or immediately logged out

**Solution**:
- Clear localStorage: `localStorage.clear()`
- Check backend JWT secret is configured
- Verify MongoDB is running

### Upload Not Working

**Problem**: Document upload fails

**Solution**:
- Check Python service is running on port 8000
- Verify file size is reasonable (<10MB)
- Check file format is supported

## API Integration

The frontend communicates with two backend services:

1. **Go Service** (Authentication):
   - `POST /api/v1/register` - User registration
   - `POST /api/v1/login` - User login
   - `POST /api/v1/logout` - User logout
   - `GET /api/v1/me` - Get current user

2. **Python Service** (RAG):
   - `POST /upload` - Upload document
   - `POST /query` - Query with AI

All authenticated requests include the JWT token in the `Authorization` header.

## Contributing

When adding new features:

1. Follow the existing project structure
2. Use Tailwind CSS for styling
3. Keep components small and focused
4. Use the AuthContext for authentication state
5. Handle errors gracefully with user-friendly messages

## License

MIT
