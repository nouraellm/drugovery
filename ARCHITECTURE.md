# Drug Discovery Informatics Platform - Architecture

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                           │
│                    (React + Material-UI)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         Nginx (Reverse Proxy)                   │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
    ┌────────▼────────┐            ┌────────▼────────┐
    │   Frontend      │            │    Backend      │
    │   (React)       │            │   (FastAPI)     │
    │   Port: 3000    │            │   Port: 8000    │
    └─────────────────┘            └────────┬───────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    │                        │                    │
         ┌──────────▼──────────┐  ┌──────────▼──────────┐  ┌─────▼──────┐
         │   PostgreSQL       │  │   Redis (Cache)     │  │   MLflow   │
         │   (Primary DB)     │  │   (Celery Broker)   │  │  (Tracking) │
         └────────────────────┘  └─────────────────────┘  └─────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Celery Worker  │
                                    │  (ML Tasks)     │
                                    └─────────────────┘
```

## Component Architecture

### Backend Services (FastAPI)

1. **Authentication Service**
   - JWT token generation/validation
   - User management (CRUD)
   - Role-based access control (Admin/User)

2. **Compound Management Service**
   - CRUD operations for compounds
   - Search and filtering
   - Integration with ChEMBL/PubChem APIs
   - Data versioning

3. **ML Prediction Service**
   - QSAR model predictions (solubility, toxicity)
   - Drug-target interaction predictions
   - Batch and real-time predictions
   - Model serving via MLflow

4. **Experiment Tracking Service**
   - MLflow integration
   - Experiment logging
   - Model comparison
   - Artifact storage

5. **Reporting Service**
   - PDF generation
   - CSV export
   - Data visualization

### Frontend Components (React)

1. **Authentication Module**
   - Login/Register pages
   - Protected routes
   - User profile management

2. **Compound Library Module**
   - Compound list/table
   - Search and filters
   - Upload/import functionality
   - Molecular structure viewer

3. **Prediction Module**
   - Prediction interface
   - Batch prediction upload
   - Results visualization
   - Model selection

4. **Experiment Dashboard**
   - Experiment list
   - Run comparison
   - Metrics visualization

5. **Reporting Module**
   - Report generation UI
   - Export options

## Data Flow

### Prediction Flow
```
User Request → FastAPI → Validate Input → 
  → Queue Task (Celery) → ML Model (MLflow) → 
  → Store Results → Update DB → Return Response
```

### Experiment Tracking Flow
```
ML Run → MLflow Client → Log Parameters/Metrics → 
  → Store Artifacts → Update Experiment DB → 
  → Frontend Dashboard
```

## Database Schema

### Core Tables
- `users` - User accounts and authentication
- `compounds` - Chemical compound data
- `compound_versions` - Version history for compounds
- `experiments` - ML experiment metadata
- `predictions` - Prediction results
- `reports` - Generated reports metadata

## Security Considerations

- JWT tokens with expiration
- Password hashing (bcrypt)
- Input validation and sanitization
- Rate limiting
- HTTPS enforcement
- Role-based access control
- Data encryption at rest (sensitive compounds)

## Scalability Considerations

- Horizontal scaling via Kubernetes
- Redis caching for frequent queries
- Celery for async task processing
- Database connection pooling
- CDN for static assets
- Load balancing via Nginx
