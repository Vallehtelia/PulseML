<div align="center">
  <img src="frontend/public/PulseML-Logo.png" alt="PulseML Logo" width="300" />
  
  **PulseML** is a modern, GPU-friendly machine learning platform featuring automated hyperparameter optimization and comprehensive training pipeline management.
  
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
</div>

---

## 🚀 Overview

PulseML is a full-stack machine learning platform that enables users to:
- Upload and analyze datasets with automatic column role detection
- Configure and train deep learning models (TCN, LSTM, CNN, Transformer)
- Monitor training progress in real-time with live metrics visualization
- Manage training runs with GPU/CPU support
- Track experiment history and compare results

## ✨ Features

### 📊 Dataset Management
- **CSV Upload & Analysis**: Automatic dataset analysis with column statistics
- **Column Role Assignment**: Set feature, target, and timestamp columns
- **Target Column Creation**: Easily create target columns from existing data
- **Data Preview**: Preview datasets before training

### 🎯 Model Training
- **Multiple Architectures**: TCN, LSTM, CNN, and Transformer support
- **Hyperparameter Configuration**: Dynamic forms with validation and defaults
- **Real-time Monitoring**: Live epoch progress and metrics visualization
- **GPU/CPU Support**: Automatic device detection (CUDA if available)
- **Training Metrics**: Track train/validation loss with graphical charts

### 📈 Training Management
- **Run Status Tracking**: Pending → Running → Completed/Failed
- **Progress Indicators**: Real-time epoch progress with percentage
- **Metrics Visualization**: Interactive charts showing training curves
- **Artifact Storage**: Model checkpoints and training logs

## 🖼️ Screenshots

### Dashboard
![Dashboard](images/dashboard.png)

### Training Configuration
![Training Parameters](images/parameters.png)

### Training Progress
![Training Metrics](images/training.png)

## 🏗️ Architecture

```
PulseML/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── auth/        # Authentication (JWT)
│   │   ├── datasets/    # Dataset management
│   │   ├── training/    # Training run management
│   │   ├── ml_engine/   # PyTorch training engine
│   │   │   ├── tcn_trainer.py    # TCN model trainer
│   │   │   └── worker.py         # Training worker process
│   │   └── db/          # Database models
│   └── alembic/         # Database migrations
│
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable UI components
│   │   └── api/        # API client
│   └── public/         # Static assets
│
└── images/              # Documentation images
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM)
- Alembic (database migrations)
- PyTorch (deep learning)
- PostgreSQL (database)
- Redis (job queue)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- React Router v6
- TanStack React Query
- Recharts (data visualization)

**Infrastructure:**
- Docker + Docker Compose
- PostgreSQL 15
- Redis 7

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PulseML
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose run --rm backend alembic upgrade head
   ```

5. **Start the training worker** (optional, for training execution)
   ```bash
   docker-compose up -d worker
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🎓 Usage Guide

### 1. Create an Account
Register a new account or login to access the platform.

### 2. Upload a Dataset
- Navigate to **Datasets** → **Upload Dataset**
- Upload a CSV file
- Review the automatic analysis
- Set column roles (feature/target/timestamp)
- Use "Set Target Column" to create a target column if needed

### 3. Create a Training Run
- Go to **Training Runs** → **New Training Run**
- Select your dataset
- Choose a model template (TCN, LSTM, CNN, Transformer)
- Configure hyperparameters
- Start training

### 4. Monitor Training
- View real-time progress on the training run detail page
- See epoch progress: "Epoch X / Y (Z%)"
- Watch live metrics: train_loss and val_loss curves
- Check device usage (CPU/GPU)

### 5. Review Results
- View final metrics (RMSE, MSE, MAE, MAPE)
- Download model checkpoints
- Analyze training logs

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -e .
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5433/pulseml"
export SECRET_KEY="your-secret-key"
alembic upgrade head
uvicorn app.main:create_application --factory --reload --port 8100
```

### Frontend Development
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8100/api" > .env.local
npm run dev
```

### Database Migrations
```bash
# Create a new migration
docker-compose run --rm backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose run --rm backend alembic upgrade head

# Rollback
docker-compose run --rm backend alembic downgrade -1
```

## 📊 Training Engine

The training engine supports:
- **TCN (Temporal Convolutional Network)**: For time series forecasting
- Automatic data preprocessing and normalization
- Train/validation/test splits
- Model checkpointing
- CSV log file generation
- Real-time progress updates

### Worker Process

The training worker runs as a separate process:
- Polls database for pending training runs
- Executes training with PyTorch
- Updates progress in real-time
- Handles errors gracefully

Start the worker:
```bash
docker-compose up -d worker
```

Or run manually:
```bash
docker-compose run --rm backend python -m app.ml_engine.worker
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Environment-based configuration
- Never commit `.env` files

## 📝 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🗺️ Roadmap

### ✅ Phase 1 (Complete)
- Backend API with auth, datasets, and training run bookkeeping
- Database schema with Alembic migrations

### ✅ Phase 2 (Complete)
- Dockerized full-stack deployment
- React frontend with dataset management UI
- Dynamic hyperparameter forms
- Training run dashboard

### ✅ Phase 3 (Complete)
- Real PyTorch-based TCN training engine
- Worker process for training execution
- Real-time metrics visualization
- GPU/CPU support
- Progress tracking

### 🚧 Future Enhancements
- Additional model architectures (LSTM, CNN, Transformer implementations)
- Hyperparameter optimization with AI assistant
- Model versioning and comparison
- Experiment tracking and MLflow integration
- Distributed training support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI, React, and PyTorch
- Inspired by modern ML platforms like Weights & Biases and MLflow

---

<div align="center">
  Made with ❤️ for the ML community
</div>

