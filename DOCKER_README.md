# Docker Setup for Banking AI Assistant

This project now includes Docker & Docker Compose for easy development and deployment.

## 🐳 Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### 1. Start All Services
```bash
# Start all services (frontend, backend, redis)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 2. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **RedisInsight**: http://localhost:8001 (optional)

### 3. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🏗️ Architecture

The Docker setup includes:

### Services
- **frontend**: Next.js app (port 3000)
- **backend**: FastAPI app (port 8000) 
- **redis**: Redis Stack for semantic routing (port 6380)

### Features
- **Hot Reload**: Code changes are reflected immediately
- **Health Checks**: Services wait for dependencies to be healthy
- **Volume Mounts**: Source code is mounted for development
- **Environment Variables**: Loaded from `.env` file

## 🔧 Development Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild Services
```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Execute Commands in Containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## 📁 File Structure

```
bank_langcache/
├── docker-compose.yml          # Main compose file
├── Dockerfile.dev              # Backend Dockerfile
├── .dockerignore               # Backend ignore file
├── nextjs-app/
│   ├── Dockerfile.dev          # Frontend Dockerfile
│   └── .dockerignore           # Frontend ignore file
└── DOCKER_README.md            # This file
```

## 🚀 Production Deployment

For production, you'll want to:
1. Create production Dockerfiles (without dev dependencies)
2. Use multi-stage builds
3. Set up proper secrets management
4. Configure reverse proxy (nginx)
5. Use Docker Swarm or Kubernetes for orchestration

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Clean Up
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker system prune -a
```

## 🔄 Migration from Manual Setup

If you were running the app manually before:

1. **Stop manual processes**:
   ```bash
   # Stop any running uvicorn/npm processes
   pkill -f uvicorn
   pkill -f "npm run dev"
   ```

2. **Start with Docker**:
   ```bash
   docker-compose up --build
   ```

3. **Verify everything works**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000/health

The Docker setup provides the same functionality with better isolation and easier deployment!
