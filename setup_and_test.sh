#!/bin/bash

# Backend Setup and Test Script
# This script helps developers quickly set up and test the backend

set -e  # Exit on error

echo "🚀 BalanceCloud Backend Setup & Test Script"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from env.example...${NC}"
    if [ -f "backend/env.example" ]; then
        cp backend/env.example backend/.env
        echo -e "${YELLOW}⚠️  Please edit backend/.env and set the required values:${NC}"
        echo "   - POSTGRES_USER"
        echo "   - POSTGRES_PASSWORD"
        echo "   - POSTGRES_DB"
        echo "   - SECRET_KEY (generate with: openssl rand -hex 32)"
        echo "   - JWT_SECRET_KEY (generate with: openssl rand -hex 32)"
        echo "   - ENCRYPTION_KEY (generate with: openssl rand -hex 32)"
        echo ""
        read -p "Press Enter after you've edited backend/.env file..."
    else
        echo -e "${RED}❌ env.example file not found!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Start services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy (30 seconds)..."
sleep 30

# Check service status
echo ""
echo "📊 Checking service status..."
docker-compose ps

# Test health endpoint
echo ""
echo "🏥 Testing health endpoint..."
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ Backend health check failed after 10 attempts${NC}"
            echo "   Check logs with: docker-compose logs backend"
            exit 1
        fi
        echo "   Attempt $i/10: Waiting for backend..."
        sleep 3
    fi
done

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
docker-compose exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Migration failed. This might be normal if migrations already ran.${NC}"
}

# Test database connection
echo ""
echo "🔍 Testing database connection..."
docker-compose exec -T backend python tests/test_db_connection.py || {
    echo -e "${YELLOW}⚠️  Database test had issues, but continuing...${NC}"
}

# Test Redis connection
echo ""
echo "🔴 Testing Redis connection..."
docker-compose exec -T backend python tests/test_redis_connection.py || {
    echo -e "${YELLOW}⚠️  Redis test had issues, but continuing...${NC}"
}

# Test API endpoints
echo ""
echo "🧪 Testing API endpoints..."
echo ""
docker-compose exec -T backend python tests/test_api_endpoints.py || {
    echo -e "${YELLOW}⚠️  Some API tests failed. Check the output above.${NC}"
}

# Summary
echo ""
echo "============================================"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📚 Next steps:"
echo "   1. View API docs: http://localhost:8000/api/docs"
echo "   2. Read TESTING_GUIDE.md for detailed testing instructions"
echo "   3. Read DEVELOPER_CONTRACT.md for API contract"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f backend"
echo "   - Stop services: docker-compose stop"
echo "   - Restart services: docker-compose restart"
echo "   - Stop and remove: docker-compose down"
echo ""
