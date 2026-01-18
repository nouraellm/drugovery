# Drug Discovery Informatics Platform

A comprehensive MVP platform for managing compound libraries, running ML predictions, tracking experiments, and generating reports for drug discovery applications.


<img width="1437" height="787" alt="Screenshot 2026-01-18 at 05 49 30" src="https://github.com/user-attachments/assets/73442577-af1c-45da-b028-db18a0e81ab2" />


## Features

- **Compound Library Management**: Upload, search, and manage chemical compounds with SMILES notation
- **ML Predictions**: QSAR models for molecular properties (solubility, toxicity) and drug-target interactions
- **Experiment Tracking**: MLflow integration for tracking ML runs and comparing models
- **Report Generation**: PDF/CSV exports with visualizations
- **User Authentication**: JWT-based auth with role-based access control
- **Data Versioning**: Track changes to compound data over time

## Tech Stack

### Backend
- FastAPI (Python 3.9+)
- PostgreSQL
- Redis
- MLflow
- Celery
- RDKit
- SQLAlchemy

### Frontend
- React.js 18+
- Material-UI (MUI)
- Axios
- React Router
- Chart.js

### Infrastructure
- Docker & Docker Compose
- Nginx
- Kubernetes-ready

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the project directory.

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MLflow UI: http://localhost:5001

5. Create initial admin user:
```bash
docker-compose exec backend python scripts/create_admin.py
```

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run migrations
python scripts/init_db.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### Start Supporting Services
```bash
# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:14

# Redis
docker run -d -p 6379:6379 redis:7

# MLflow
mlflow server --backend-store-uri postgresql://postgres:postgres@localhost/mlflow --default-artifact-root ./mlruns --host 0.0.0.0 --port 5001
```

## Project Structure

```
nlp/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── compounds.py
│   │   │   │   ├── predictions.py
│   │   │   │   ├── experiments.py
│   │   │   │   └── reports.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── compound.py
│   │   │   ├── experiment.py
│   │   │   └── prediction.py
│   │   ├── schemas/
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ml_service.py
│   │   │   ├── chembl_service.py
│   │   │   └── versioning_service.py
│   │   ├── tasks/
│   │   │   └── prediction_tasks.py
│   │   └── main.py
│   ├── ml_models/
│   │   ├── qsar_models/
│   │   └── dti_models/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

```bash
kubectl apply -f k8s/
```

## Usage Examples

### Creating a Compound
```python
import requests

token = "your-jwt-token"
headers = {"Authorization": f"Bearer {token}"}

compound_data = {
    "name": "Aspirin",
    "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "molecular_formula": "C9H8O4"
}

response = requests.post(
    "http://localhost:8000/api/v1/compounds",
    json=compound_data,
    headers=headers
)
```

### Running a Prediction
```python
prediction_data = {
    "compound_id": 1,
    "model_type": "solubility",
    "model_name": "solubility_model"
}

response = requests.post(
    "http://localhost:8000/api/v1/predictions",
    json=prediction_data,
    headers=headers
)
```

### Batch Predictions
```python
batch_data = {
    "compound_ids": [1, 2, 3, 4, 5],
    "model_type": "toxicity",
    "model_name": "toxicity_model"
}

response = requests.post(
    "http://localhost:8000/api/v1/predictions/batch",
    json=batch_data,
    headers=headers
)
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check database credentials in `.env`
- Verify network connectivity between services

### MLflow Connection Issues
- Check MLflow service is running: `docker-compose logs mlflow`
- Verify MLFLOW_TRACKING_URI in environment variables
- Check PostgreSQL connection for MLflow backend

### Frontend Not Loading
- Check backend API is accessible: `curl http://localhost:8000/health`
- Verify CORS settings in backend config
- Check browser console for errors

## Performance Tips

1. **Database Indexing**: Add indexes on frequently queried fields
2. **Caching**: Use Redis for caching compound lookups
3. **Batch Operations**: Use batch endpoints for multiple operations
4. **Pagination**: Always use pagination for large datasets
5. **Async Tasks**: Use Celery for long-running predictions

## Security Best Practices

1. Change default SECRET_KEY in production
2. Use strong database passwords
3. Enable HTTPS in production
4. Implement rate limiting
5. Regularly update dependencies
6. Use environment variables for secrets
7. Implement input validation
8. Enable audit logging

## License

MIT

## Contributing

Contributions are welcome! Please see the implementation guide for details on extending the platform.

## Support

For issues and questions, please open an issue on the repository.
