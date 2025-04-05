# Face Recognition System Deployment Guide

## Prerequisites
- Docker 20.10+ and Docker Compose 1.29+
- NVIDIA Docker runtime (for GPU acceleration)
- Python 3.9+ (for development)
- Node.js 18+ (for frontend development)

## 1. Local Development Setup

### Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Frontend Setup
```bash
cd ui/web
npm install
npm start
```

## 2. Docker Deployment

### Build and Run
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Environment Configuration
1. Update `.env.production` with your actual credentials
2. Rebuild containers if changes are made:
   ```bash
   docker-compose up -d --build
   ```

## 3. Production Deployment (Cloud)

### AWS EC2 with GPU
```bash
# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Clone repository
git clone https://your-repository.git
cd face_recognition_system

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 4. System Management

### Common Commands
```bash
# Stop services
docker-compose down

# Update code
git pull origin main
docker-compose up -d --build

# Backup database
docker cp face_recognition_system:/app/data/criminal_db.sqlite ./backups/
```

## 5. Monitoring
Access services at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/status
- Video Feed: http://localhost:8000/video_feed

## Troubleshooting
1. **GPU Acceleration Issues**:
   - Verify NVIDIA drivers are installed
   - Run `nvidia-smi` to check GPU status
   - Add `runtime: nvidia` to docker-compose.yml services

2. **Performance Optimization**:
   - Adjust `DETECTION_INTERVAL` in .env.production
   - Reduce `MAX_FRAME_WIDTH/HEIGHT` for lower resolution processing

3. **Alert Delivery Problems**:
   - Check SMTP/Twilio credentials
   - Verify network connectivity
   - Inspect logs with `docker-compose logs alerts`