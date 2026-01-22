# Docker Setup Guide for Backend Developers

This guide will help you set up and run the BalanceCloud backend using Docker and Docker Compose.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or later)
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Verify installation: `docker --version`
  
- **Docker Compose** (version 2.0 or later)
  - Usually included with Docker Desktop
  - Verify installation: `docker-compose --version` or `docker compose version`

- **Git** (to clone the repository)
  - Verify installation: `git --version`

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd balancecloud/mvp_v1
```

### Step 2: Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### Step 3: Configure Environment Variables

Open `.env` in your editor and set the following **REQUIRED** variables:

#### Database Configuration
```bash
POSTGRES_USER=balancecloud
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=balancecloud_mvp
```

#### Security Keys (Generate secure random strings)
```bash
# Generate with: openssl rand -hex 32
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
```

#### Storage Configuration
```bash
# Default storage quota per user in bytes
# 10 GB = 10737418240 bytes
# 5 GB = 5368709120 bytes
DEFAULT_STORAGE_QUOTA_BYTES=10737418240
```

#### Optional: OAuth Configuration (for cloud uploads)
```bash
# Google Drive OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Microsoft OneDrive OAuth (optional)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/cloud-accounts/callback/onedrive
MICROSOFT_TENANT_ID=common
```

#### Other Configuration (Optional - defaults provided)
```bash
# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:5173

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Important Notes:**
- All variables marked as **REQUIRED** must be set, or the backend will fail to start
- Use strong, unique values for security keys in production
- Never commit your `.env` file to version control

### Step 4: Start Services with Docker Compose

Start all services (PostgreSQL, Redis, and Backend):

```bash
docker-compose up -d
```

This command will:
- Build the backend Docker image (first time only)
- Start PostgreSQL database
- Start Redis cache
- Start the backend API server
- Wait for services to be healthy before starting dependent services

### Step 5: Run Database Migrations

After services are running, apply database migrations:

```bash
docker-compose exec backend alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade <revision> -> <revision>, <description>
```

### Step 6: Verify Setup

Check that all services are running:

```bash
docker-compose ps
```

You should see all three services (postgres, redis, backend) with status "Up" and "healthy".

Test the API health endpoint:

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"healthy","service":"balancecloud-backend"}
```

## 📝 Common Operations

### View Logs

View logs from all services:
```bash
docker-compose logs -f
```

View logs from a specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Stop Services

Stop all services:
```bash
docker-compose stop
```

Stop and remove containers (keeps volumes):
```bash
docker-compose down
```

Stop and remove containers and volumes (⚠️ **deletes database data**):
```bash
docker-compose down -v
```

### Restart Services

Restart all services:
```bash
docker-compose restart
```

Restart a specific service:
```bash
docker-compose restart backend
```

### Rebuild Backend Image

If you've made changes to the backend code or Dockerfile:

```bash
docker-compose build backend
docker-compose up -d backend
```

Or rebuild and restart in one command:
```bash
docker-compose up -d --build backend
```

### Access Database

Connect to PostgreSQL:
```bash
docker-compose exec postgres psql -U balancecloud -d balancecloud_mvp
```

Or using the POSTGRES_USER from your .env:
```bash
docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

### Access Redis

Connect to Redis CLI:
```bash
docker-compose exec redis redis-cli
```

### Run Commands in Backend Container

Execute commands inside the backend container:
```bash
docker-compose exec backend <command>
```

Examples:
```bash
# Run Python script
docker-compose exec backend python tests/test_db_connection.py

# Run Alembic commands
docker-compose exec backend alembic current
docker-compose exec backend alembic history

# Access Python shell
docker-compose exec backend python
```

## 🔧 Troubleshooting

### Backend Fails to Start

**Error: `DEFAULT_STORAGE_QUOTA_BYTES environment variable is required`**

**Solution:** Make sure `DEFAULT_STORAGE_QUOTA_BYTES` is set in your `.env` file.

**Error: `ValueError: SECRET_KEY environment variable is required`**

**Solution:** Make sure all required security keys are set in your `.env` file:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`

**Error: `Connection refused` or `Could not connect to database`**

**Solution:** 
1. Check if PostgreSQL is running: `docker-compose ps`
2. Wait for PostgreSQL to be healthy: `docker-compose logs postgres`
3. Verify database credentials in `.env` match `docker-compose.yml`

### Port Already in Use

**Error: `Bind for 0.0.0.0:8000 failed: port is already allocated`**

**Solution:**
1. Find what's using the port:
   ```bash
   # Linux/Mac
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```
2. Stop the service using the port, or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8001:8000"  # Use 8001 instead of 8000
   ```

### Database Migration Errors

**Error: `alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'`**

**Solution:**
1. Check current migration state:
   ```bash
   docker-compose exec backend alembic current
   ```
2. If migrations are out of sync, you may need to reset:
   ```bash
   # ⚠️ WARNING: This will delete all data
   docker-compose down -v
   docker-compose up -d postgres redis
   docker-compose exec backend alembic upgrade head
   ```

**Error: `relation "alembic_version" does not exist`**

**Solution:** The database is empty. Run migrations:
```bash
docker-compose exec backend alembic upgrade head
```

### Container Keeps Restarting

**Check logs:**
```bash
docker-compose logs backend
```

Common causes:
- Missing required environment variables
- Database connection issues
- Port conflicts

### Cannot Connect to Database from Host Machine

If you need to connect from outside Docker (e.g., using a database GUI):

1. The database is exposed on `localhost:5432` by default
2. Use these credentials from your `.env`:
   - Host: `localhost`
   - Port: `5432`
   - Database: `POSTGRES_DB` value
   - Username: `POSTGRES_USER` value
   - Password: `POSTGRES_PASSWORD` value

## 🧪 Testing the Setup

### Test Database Connection

```bash
docker-compose exec backend python tests/test_db_connection.py
```

Expected output:
```
✅ PostgreSQL connection successful!
```

### Test Redis Connection

```bash
docker-compose exec backend python tests/test_redis_connection.py
```

Expected output:
```
✅ Redis connection successful!
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Create a test user (requires valid request body)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

## 📚 Next Steps

Once your backend is running:

1. **Read the API Documentation:**
   - [Quick API Reference](QUICK_API_REFERENCE.md)
   - [Developer Contract](../api/DEVELOPER_CONTRACT.md)

2. **Explore the Codebase:**
   - Backend code: `backend/app/`
   - API routes: `backend/app/api/routes/`
   - Services: `backend/app/services/`
   - Models: `backend/app/models/`

3. **Run Tests:**
   ```bash
   docker-compose exec backend pytest tests/
   ```

4. **Development Workflow:**
   - Make code changes locally
   - Rebuild backend: `docker-compose up -d --build backend`
   - Test changes
   - View logs: `docker-compose logs -f backend`

## 🔐 Security Notes

- **Never commit `.env` files** to version control
- Use strong, unique passwords and keys in production
- Rotate security keys regularly
- Keep Docker and dependencies updated
- Review security headers in production (see `INFRASTRUCTURE_SETUP.md`)

## 📞 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f backend`
2. Verify your `.env` file has all required variables
3. Check the [Troubleshooting](#-troubleshooting) section above
4. Review other documentation in `docs/` directory
5. Check GitHub Issues for similar problems

## 🎯 Summary Checklist

- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] `.env` file created from `.env.example`
- [ ] All required environment variables set
- [ ] Services started: `docker-compose up -d`
- [ ] Migrations run: `docker-compose exec backend alembic upgrade head`
- [ ] Health check passes: `curl http://localhost:8000/api/health`
- [ ] Database connection test passes
- [ ] Redis connection test passes

Once all items are checked, you're ready to develop! 🚀
