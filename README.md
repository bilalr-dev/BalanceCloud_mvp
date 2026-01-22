# BalanceCloud MVP v1

**A Zero-Trust Gateway-Based Multi-Cloud Storage Aggregator**

BalanceCloud is a secure, gateway-based system that aggregates fragmented cloud storage (Google Drive, OneDrive, etc.) with pre-upload encryption at the gateway level. Files are encrypted before leaving the gateway, ensuring cloud providers never see unencrypted data.

**Version:** 1.0.0  
**Last Updated:** 2026-01-22  
**Status:** ✅ MVP Complete - Production Ready

---

## 🎯 Project Overview

BalanceCloud provides a unified interface for managing files across multiple cloud storage providers while maintaining strict security through:

- **Zero-Trust Architecture**: All files encrypted before leaving the gateway
- **Pre-Upload Encryption**: AES-256-GCM encryption at the gateway level
- **Multi-Cloud Support**: Aggregates storage from Google Drive, OneDrive
- **Chunked Storage**: Files split into 10MB encrypted chunks
- **Automatic Cloud Sync**: Files automatically uploaded to connected cloud accounts
- **Storage Quota Management**: Per-user storage limits with usage tracking

---

## 🏗️ Architecture

```
User Browser → React Frontend → FastAPI Gateway → Encryption Service → Cloud Providers
                                      ↓
                                PostgreSQL (Metadata)
                                Redis (Rate Limiting)
                                Local Storage (Encrypted Chunks)
```

### Key Components

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI (Python 3.11+) with async SQLAlchemy
- **Database**: PostgreSQL 15+ for metadata storage
- **Cache**: Redis for rate limiting
- **Encryption**: AES-256-GCM with chunk-level encryption
- **Cloud Integration**: Google Drive & OneDrive OAuth2
- **Infrastructure**: Docker Compose orchestration

---

## 📚 For Developers

**New to this project?** Start here:

### 🚀 Quick Start
- 📖 **[Docker Setup Guide](docs/guides/DOCKER_SETUP_GUIDE.md)** - Complete guide to run backend with Docker (⭐ **Start here for new developers**)
- 📋 **[Developer Contract](docs/api/DEVELOPER_CONTRACT.md)** - API contract and integration guidelines
- ⚡ **[Quick API Reference](docs/guides/QUICK_API_REFERENCE.md)** - Quick API endpoint reference

### 📖 Documentation
- 📚 **[Documentation Index](docs/README.md)** - All documentation organized by category
- 🏗️ **[Technical Documentation](docs/architecture/TECHNICAL_DOCUMENTATION.md)** - Technical choices, difficulties, bottlenecks
- 🔐 **[Encryption Architecture](docs/architecture/ENCRYPTION_ARCHITECTURE.md)** - Encryption design and implementation
- 👥 **[Team Workflow](docs/team/TEAM_WORKFLOW.md)** - Contract-based development workflow

### 🐛 Frontend
- 📝 **[Frontend Code Review](docs/frontend/FRONTEND_CODE_REVIEW.md)** - Frontend issues and fixes needed

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (version 20.10 or later)
- **Docker Compose** (version 2.0 or later)
- **Git**

### Backend Setup (Docker - Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd balancecloud/mvp_v1

# Copy environment file
cp .env.example .env

# Edit .env and set required variables:
# - DATABASE_URL
# - SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY
# - DEFAULT_STORAGE_QUOTA_BYTES
# - OAuth credentials (optional)

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check health
curl http://localhost:8000/api/health
```

**📖 For detailed setup instructions, see [Docker Setup Guide](docs/guides/DOCKER_SETUP_GUIDE.md)**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## ✅ Current Status

### ✅ Phase 1: Backend Infrastructure (Completed)
- [x] PostgreSQL database setup
- [x] Redis for rate limiting
- [x] Alembic migrations
- [x] Docker Compose orchestration
- [x] Environment variable configuration

### ✅ Phase 2: Authentication & Security (Completed)
- [x] JWT authentication
- [x] Password hashing (bcrypt)
- [x] Rate limiting middleware
- [x] Security headers middleware
- [x] CORS configuration

### ✅ Phase 3: File Management (Completed)
- [x] File upload with chunked encryption
- [x] File download with decryption
- [x] Folder management
- [x] Storage quota management
- [x] Storage usage tracking

### ✅ Phase 4: Cloud Integration (Completed)
- [x] Google Drive OAuth2 integration
- [x] OneDrive OAuth2 integration
- [x] Automatic cloud upload
- [x] Cloud storage usage tracking
- [x] Cloud account management

### ✅ Phase 5: Frontend (Completed)
- [x] React + TypeScript setup
- [x] Authentication pages (Login/Register)
- [x] File management UI
- [x] Cloud accounts management UI
- [x] Storage usage display

---

## 🛠️ Tech Stack

### Frontend
- **React 18+** with TypeScript
- **Vite** for build tooling
- **Zustand** for state management
- **Axios** for HTTP client
- **React Router** for navigation

### Backend
- **FastAPI** (Python 3.11+)
- **SQLAlchemy 2.0** with async support
- **Alembic** for database migrations
- **Pydantic V2** for validation
- **cryptography** library for encryption
- **asyncpg** for PostgreSQL async driver
- **httpx** for HTTP client

### Infrastructure
- **PostgreSQL 15+** for metadata
- **Redis** for rate limiting
- **Docker** and **Docker Compose**

---

## 📁 Project Structure

```
mvp_v1/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration, database
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── middleware/        # Rate limiting, security
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── store/             # Zustand stores
│   │   └── types/             # TypeScript types
│   └── package.json
├── docs/                      # Documentation
│   ├── guides/                # How-to guides
│   ├── architecture/          # Architecture docs
│   ├── api/                   # API documentation
│   └── frontend/              # Frontend docs
├── contracts/                 # Team contracts
├── docker-compose.yml         # Docker orchestration
└── .env.example               # Environment template
```

---

## 🔐 Security Features

1. **Encryption at Rest**: OAuth tokens and encryption keys encrypted in database
2. **Encryption in Transit**: All communication over HTTPS (production)
3. **Pre-Upload Encryption**: Files encrypted before leaving gateway
4. **Chunk-Level Encryption**: Each chunk has unique IV and encryption key
5. **Zero Client Trust**: Frontend never receives encryption keys
6. **Token Security**: OAuth tokens encrypted before database storage
7. **Rate Limiting**: Redis-based rate limiting to prevent abuse

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_encryption_comprehensive.py

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

### Manual Testing

See [Testing Guide](docs/guides/TESTING_GUIDE.md) for comprehensive testing instructions.

---

## 📝 Configuration

### Required Environment Variables

See `.env.example` for all required variables. Key variables:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing key
- `ENCRYPTION_KEY` - Master encryption key
- `DEFAULT_STORAGE_QUOTA_BYTES` - Default storage quota per user

### Optional Environment Variables

- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - For Google Drive integration
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET` - For OneDrive integration
- `REDIS_URL` - Redis connection URL
- `CORS_ORIGINS` - Allowed CORS origins

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check all required environment variables are set
- Verify PostgreSQL and Redis are running
- Check logs: `docker-compose logs backend`

**Database migration errors:**
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Check database URL in `.env`
- Try: `docker-compose exec backend alembic downgrade base && alembic upgrade head`

**Frontend can't connect to backend:**
- Verify `VITE_API_BASE_URL` in frontend `.env`
- Check backend is running: `curl http://localhost:8000/api/health`
- Check CORS configuration

**For more troubleshooting, see [Docker Setup Guide](docs/guides/DOCKER_SETUP_GUIDE.md#-troubleshooting)**

---

## 📚 Documentation

- **[Documentation Index](docs/README.md)** - Complete documentation index
- **[Docker Setup Guide](docs/guides/DOCKER_SETUP_GUIDE.md)** - Backend setup with Docker
- **[Technical Documentation](docs/architecture/TECHNICAL_DOCUMENTATION.md)** - Technical choices and improvements
- **[API Contract](docs/api/DEVELOPER_CONTRACT.md)** - Backend API specification
- **[Team Workflow](docs/team/TEAM_WORKFLOW.md)** - Development workflow

---

## 🤝 Contributing

This is a private project. Please refer to:
- [Team Workflow](docs/team/TEAM_WORKFLOW.md) for development guidelines
- [Contracts Directory](contracts/) for API contracts
- [TASKS_PLANING.md](TASKS_PLANING.md) for project planning

---

## 📄 License

Private project - All rights reserved

---

**Last Updated:** 2026-01-22  
**Maintainers:** Backend Team
