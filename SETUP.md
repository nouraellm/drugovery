# Setup Instructions

## Initial Setup

### 1. Clone and Navigate
```bash
cd /Users/nouraellm/Downloads/nlp
```

### 2. Environment Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/drugdiscovery
REDIS_URL=redis://localhost:6379/0
MLFLOW_TRACKING_URI=http://localhost:5001
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Start Services with Docker Compose
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MLflow (port 5001)
- Backend API (port 8000)
- Frontend (port 3000)
- Celery worker

### 4. Initialize Database
```bash
# Wait for services to be ready (about 30 seconds)
sleep 30

# Initialize database tables
docker-compose exec backend python scripts/init_db.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py \
  --email admin@example.com \
  --password admin123
```

### 5. Verify Installation
```bash
# Check backend health
curl http://localhost:8000/health

# Check MLflow
curl http://localhost:5001

# Check frontend (should return HTML)
curl http://localhost:3000
```

## First Login

1. Open browser: http://localhost:3000
2. Login with:
   - Email: `admin@example.com`
   - Password: `admin123`

## Development Setup

### Backend Development

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (or use .env file):
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/drugdiscovery
export REDIS_URL=redis://localhost:6379/0
export MLFLOW_TRACKING_URI=http://localhost:5001
export SECRET_KEY=dev-secret-key
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

The frontend will be available at http://localhost:3000

### Running Tests

Backend tests:
```bash
cd backend
pytest tests/ -v
```

Frontend tests:
```bash
cd frontend
npm test
```

## Common Issues

### Port Already in Use
If a port is already in use, either:
1. Stop the conflicting service
2. Change the port in `docker-compose.yml`

### Database Connection Errors
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database credentials
- Wait for database to be fully initialized (may take 10-20 seconds)

### MLflow Not Starting
- Check PostgreSQL is running first
- Review MLflow logs: `docker-compose logs mlflow`
- Ensure MLflow database exists (created automatically)

### Frontend Can't Connect to Backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/app/core/config.py`
- Verify `REACT_APP_API_URL` environment variable

## Stopping Services

```bash
docker-compose down
```

To remove volumes (clears all data):
```bash
docker-compose down -v
```

## Resetting Database

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm nlp_postgres_data

# Start services again
docker-compose up -d

# Reinitialize
docker-compose exec backend python scripts/init_db.py
docker-compose exec backend python scripts/create_admin.py
```
