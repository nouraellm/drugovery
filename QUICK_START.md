# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start All Services
```bash
docker-compose up -d
```

### Step 2: Initialize Database
```bash
# Wait 30 seconds for services to start
sleep 30

# Create database tables
docker-compose exec backend python scripts/init_db.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### Step 3: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5001

### Step 4: Login
- Email: `admin@example.com`
- Password: `admin123`

## 📋 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

### Restart a Service
```bash
docker-compose restart backend
```

### Access Backend Shell
```bash
docker-compose exec backend bash
```

### Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

## 🧪 Test the API

### Get Auth Token
```bash
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123" \
  | jq -r '.access_token')
```

### Create a Compound
```bash
curl -X POST "http://localhost:8000/api/v1/compounds" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "molecular_formula": "C9H8O4"
  }'
```

### Run a Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "compound_id": 1,
    "model_type": "solubility"
  }'
```

## 📚 Next Steps

1. **Explore the Frontend**: Navigate through the UI to understand all features
2. **Read the Docs**: Check out `IMPLEMENTATION.md` for architecture details
3. **Run Tests**: See `TESTING.md` for testing instructions
4. **Deploy**: Follow `DEPLOYMENT.md` for production deployment

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check what's running
docker-compose ps

# Check logs
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### Can't Connect to Database
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres
```

### Frontend Shows Errors
- Check browser console (F12)
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend config

## 📖 Documentation

- **README.md**: Overview and features
- **SETUP.md**: Detailed setup instructions
- **ARCHITECTURE.md**: System architecture
- **IMPLEMENTATION.md**: Implementation details
- **TESTING.md**: Testing guide
- **DEPLOYMENT.md**: Deployment guide

## 🎯 Key Features to Try

1. **Create Compounds**: Add chemical compounds with SMILES notation
2. **Run Predictions**: Predict solubility, toxicity, or drug-target interactions
3. **Batch Predictions**: Process multiple compounds at once
4. **Track Experiments**: Use MLflow to track ML runs
5. **Generate Reports**: Export data as PDF or CSV
6. **Version History**: View and rollback compound changes

Enjoy exploring the Drug Discovery Informatics Platform! 🧬
