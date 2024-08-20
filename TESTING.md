# Testing Guide

## Backend Testing

### Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Frontend Testing

### Setup
```bash
cd frontend
npm install
```

### Run Tests
```bash
npm test
```

## Integration Testing

### Manual API Testing

1. Start all services:
```bash
docker-compose up -d
```

2. Create admin user:
```bash
docker-compose exec backend python scripts/create_admin.py
```

3. Test authentication:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

4. Test compound creation (replace TOKEN):
```bash
curl -X POST "http://localhost:8000/api/v1/compounds" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ethanol",
    "smiles": "CCO",
    "molecular_formula": "C2H6O"
  }'
```

5. Test prediction:
```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "compound_id": 1,
    "model_type": "solubility",
    "model_name": "solubility_model"
  }'
```

## Performance Testing

### Load Testing with Apache Bench
```bash
# Test compound listing endpoint
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/compounds
```

## End-to-End Testing

1. Start the application:
```bash
docker-compose up -d
```

2. Access frontend: http://localhost:3000

3. Login with admin credentials

4. Test workflows:
   - Create a compound
   - Run a prediction
   - Create an experiment
   - Generate a report
