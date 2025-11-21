# PulseML

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**PulseML** is a modern, GPU-friendly machine learning platform featuring automated hyperparameter optimization and comprehensive training pipeline management. This repository contains both the FastAPI backend and React/TypeScript frontend for Phase 2 of the project.

---

## 🚀 Features (Phase 2)

### Backend (FastAPI)
- **User Authentication**: JWT-based auth with access and refresh tokens
- **Dataset Management**: Upload, analyze, and preview CSV datasets with automatic type inference
  - **No Row Limits**: Analyze datasets with 70k+ rows without artificial restrictions
  - **Rename Datasets**: Update dataset names and descriptions
  - **Delete Datasets**: Remove datasets with confirmation dialogs
- **Schema Management**: Define feature roles (feature/target/timestamp/ignore) for ML workflows
- **Model Templates**: Pre-configured model templates with comprehensive hyperparameter schemas
- **Training Run Orchestration**: Track training runs with status management (pending/queued/running/completed/failed/stopped)
- **PostgreSQL + Alembic**: Full database migrations and JSONB support for flexible metadata
- **Redis Integration**: Job queue infrastructure (Phase 3 will use for distributed training)

### Frontend (React + Vite + TypeScript)
- **Modern UI**: Dark theme with responsive layout and professional color palette
  - **Responsive Design**: Content scales properly on all screen widths with centered layout
  - **Mobile-Friendly**: Tables scroll horizontally while content adapts to screen size
- **Dataset Upload & Preview**: Drag-and-drop CSV upload with column-level schema management
- **Dynamic Hyperparameter Forms**: Auto-generated forms based on model template schemas
  - **Informative Tooltips**: Comprehensive, well-formatted parameter explanations
  - **Educational Content**: Each hyperparameter includes best practices and typical ranges
- **Training Run Dashboard**: Real-time status tracking and metrics visualization (ready for Phase 3)
- **React Query**: Optimistic updates and intelligent caching
- **Protected Routes**: Auth-guarded pages with automatic token refresh

### Infrastructure
- **Fully Dockerized**: One-command stack deployment with Docker Compose
- **Hot Reload**: Development mode with live reload for both frontend and backend
- **Configurable Ports**: All ports and URLs controlled via `.env` file
- **CORS-Ready**: Pre-configured for seamless frontend-backend communication

---

## 📋 Prerequisites

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- **Python 3.11+** (if running backend locally without Docker)
- **Node.js 20+** (if running frontend locally without Docker)

---

## 🔧 Quick Start

### 1. Clone and Configure Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd PulseML

# Copy the example environment file
cp .env.example .env
```

### 2. Generate Secret Key

Your `.env` file requires a strong `SECRET_KEY` for JWT signing. Generate one:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output and paste it into your `.env` file as the `SECRET_KEY` value.

### 3. Configure Ports (Optional)

By default, PulseML uses these ports:
- **Frontend**: `3100`
- **Backend API**: `8100`
- **PostgreSQL**: `5433`
- **Redis**: `6380`

You can customize these in `.env` if they conflict with existing services.

### 4. Start the Database and Run Migrations

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Wait ~5 seconds for PostgreSQL to finish initializing, then run migrations
docker-compose run --rm backend alembic upgrade head
```

### 5. Launch the Full Stack

```bash
docker-compose up --build
```

This will start:
- PostgreSQL (persistent data storage)
- Redis (job queue, ready for Phase 3)
- Backend (FastAPI on port 8100)
- Frontend (React/Vite on port 3100)

### 6. Access the Application

Open your browser and navigate to:

🌐 **Frontend**: [http://localhost:3100](http://localhost:3100)  
🔌 **Backend API Docs**: [http://localhost:8100/docs](http://localhost:8100/docs)  
❤️ **Health Check**: [http://localhost:8100/health](http://localhost:8100/health)

---

## 🎯 Usage Workflow

### First-Time Setup
1. **Register a User**: Navigate to the Register page and create your account
2. **Login**: Authenticate with your credentials (JWT tokens stored automatically)

### Working with Datasets
3. **Upload a Dataset**: 
   - Go to **Datasets** → **Upload Dataset**
   - Drop a CSV file or click to browse (supports large datasets with 70k+ rows)
   - Provide a name and optional description
   - Backend automatically analyzes columns, infers types, and generates statistics

4. **Manage Datasets**:
   - Click on a dataset to view details
   - **Rename**: Update dataset name and description using the "Rename" button
   - **Delete**: Remove datasets with confirmation dialog using the "Delete" button
   - **Configure Schema**: Assign roles to each column:
     - **Feature**: Input variable for the model
     - **Target**: Prediction target (label)
     - **Timestamp**: Time-series index
     - **Ignore**: Exclude from training
   - View missing value percentages and data types
   - Save schema changes

### Training Runs
5. **Create a Training Run**:
   - Go to **Training Runs** → **New Training Run**
   - Select a dataset and model template
   - Configure hyperparameters using the dynamic form (tooltips explain each parameter)
   - Click **Start Training** (Phase 2 queues the run; Phase 3 will execute training)

6. **Monitor Progress**:
   - View all runs in the **Training Runs** page
   - Check status badges (Pending/Running/Completed/Failed)
   - Click a run to see hyperparameters and metrics (Phase 3 will populate real metrics)

### AI Assistant (Coming in Phase 3)
7. **Auto-Tuning**: The "Auto-tune with AI 🤖" button will enable automated hyperparameter search using historical run data to iteratively improve model performance.

---

## 🏗️ Architecture

### Stack Overview

```
┌─────────────────────────────────────────────┐
│          Browser (localhost:3100)           │
│     React + TypeScript + Vite + Query       │
└─────────────────┬───────────────────────────┘
                  │ HTTP (CORS-enabled)
                  ▼
┌─────────────────────────────────────────────┐
│       FastAPI Backend (localhost:8100)      │
│   JWT Auth • Dataset Analysis • Training    │
└─────────┬──────────────────┬────────────────┘
          │                  │
          ▼                  ▼
┌──────────────────┐  ┌─────────────────┐
│   PostgreSQL     │  │     Redis       │
│   (port 5433)    │  │   (port 6380)   │
│  Persistent DB   │  │   Job Queue     │
└──────────────────┘  └─────────────────┘
```

### Technology Stack

**Backend**:
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM with asyncio support)
- Alembic (database migrations)
- Pydantic v2 (validation and settings)
- psycopg2 (PostgreSQL driver)
- Redis (job queue, ready for Celery in Phase 3)
- pandas + numpy (dataset analysis)
- python-jose (JWT signing)
- passlib + bcrypt (password hashing)

**Frontend**:
- React 18 (UI framework)
- TypeScript (type safety)
- Vite (build tool and dev server)
- React Router v6 (routing)
- TanStack React Query (server state management)
- Axios (HTTP client)
- Recharts (data visualization, ready for Phase 3 metrics)

**Infrastructure**:
- Docker + Docker Compose (containerization)
- PostgreSQL 15 (relational database)
- Redis 7 (cache and job queue)

---

## 📁 Project Structure

```
PulseML/
├── backend/
│   ├── app/
│   │   ├── api/               # API endpoints (auth, datasets, training, models)
│   │   ├── db/                # Database session, models, base
│   │   ├── models_registry/   # Model template definitions
│   │   ├── dataset_utils/     # CSV analysis and schema validation
│   │   ├── config.py          # Settings (Pydantic)
│   │   └── main.py            # FastAPI app factory
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios client and API wrappers
│   │   ├── components/        # UI components (layout, domain, reusable)
│   │   ├── pages/             # Page components (Dashboard, Datasets, etc.)
│   │   ├── router/            # React Router config
│   │   ├── hooks/             # Custom hooks (useAuth, etc.)
│   │   ├── styles/            # Global CSS and theme
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── package.json
│
├── docker-compose.yml         # Multi-service orchestration
├── .env.example               # Template environment variables
├── .env                       # Your local config (not committed)
└── README.md
```

---

## 🛠️ Development

### Running Locally (Without Docker)

#### Backend
```bash
cd backend
pip install -e .
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/pulseml"
export SECRET_KEY="your-secret-key"
alembic upgrade head
uvicorn app.main:create_application --factory --reload --port 8100
```

#### Frontend
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8100/api" > .env.local
npm run dev
```

### Docker Commands

```bash
# Rebuild a specific service
docker-compose build backend

# View logs for a service
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# Run a one-off command in a service
docker-compose run --rm backend alembic revision --autogenerate -m "Add new table"
```

### Database Migrations

```bash
# Create a new migration after modifying models
docker-compose run --rm backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose run --rm backend alembic upgrade head

# Rollback one migration
docker-compose run --rm backend alembic downgrade -1
```

---

## 🔒 Security Notes

- **Never commit `.env`** to version control (already in `.gitignore`)
- Generate a new `SECRET_KEY` for production (64+ character random string)
- Update `BACKEND_CORS_ORIGINS` in production to match your frontend domain
- Use strong PostgreSQL passwords in production
- Consider enabling HTTPS/TLS for production deployments

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Symptom**: CORS errors or "Network Error" in browser console

**Solution**: 
1. Ensure `VITE_API_BASE_URL` in `.env` is set to `http://localhost:8100/api` (not `http://backend:8000`)
2. Verify `BACKEND_CORS_ORIGINS` includes `http://localhost:3100`
3. Rebuild: `docker-compose up --build`

### Backend fails with "database system is starting up"

**Symptom**: Backend container exits immediately with Postgres connection error

**Solution**: 
1. Start DB first: `docker-compose up -d db redis`
2. Wait 5-10 seconds for Postgres to initialize
3. Then start backend: `docker-compose up backend frontend`

### Port conflicts

**Symptom**: `address already in use` error

**Solution**: Change conflicting ports in `.env`:
```ini
FRONTEND_PORT=3200
BACKEND_PORT=8200
POSTGRES_PORT=5434
REDIS_PORT=6381
```

### Alembic migration fails with "type already exists"

**Symptom**: `DuplicateObject: type "trainingstatus" already exists`

**Solution**: Reset the database:
```bash
docker-compose down -v
docker-compose up -d db redis
# Wait 10 seconds
docker-compose run --rm backend alembic upgrade head
```

---

## 🗺️ Roadmap

### ✅ Phase 1 (Complete)
- Backend API with auth, datasets, and training run bookkeeping
- Database schema with Alembic migrations

### ✅ Phase 2 (Current)
- Dockerized full-stack deployment
- React frontend with dataset management UI
- Dynamic hyperparameter forms
- Training run dashboard (UI ready, execution in Phase 3)

### 🚧 Phase 3 (Planned)
- **Training Engine**: Celery workers for distributed training
- **Real Metrics**: Loss curves, accuracy, and custom metrics visualization
- **Model Artifacts**: Download trained models and logs
- **AI Hyperparameter Assistant**: Automated tuning with historical analysis
- **Multi-GPU Support**: Distributed training across GPUs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📧 Contact

For questions, suggestions, or issues, please open an issue on GitHub.

---

**Built with ❤️ for the machine learning community**
