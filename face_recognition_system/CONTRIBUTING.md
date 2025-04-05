# Contribution Guidelines

## Development Workflow

1. **Fork** the repository
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/face-recognition-system.git
   ```
3. **Branch** naming convention:
   - `feature/` for new features
   - `fix/` for bug fixes
   - `docs/` for documentation
   - `test/` for test cases

## Environment Setup

### Backend
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
```

### Frontend
```bash
cd ui/web
npm install
```

## Testing

### Unit Tests
```bash
# Backend tests
pytest tests/unit -v

# Frontend tests
cd ui/web
npm test
```

### Integration Tests
```bash
# Run with test database
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## Code Standards

1. **Python**:
   - PEP 8 compliance
   - Type hints for all functions
   - Google-style docstrings

2. **JavaScript/React**:
   - ESLint with Airbnb config
   - PropTypes for all components
   - Functional components with hooks

3. **Commit Messages**:
   - Conventional Commits standard
   - Format: `<type>(<scope>): <description>`
   - Example: `feat(api): add criminal search endpoint`

## Pull Requests

1. Ensure all tests pass
2. Update documentation if needed
3. Include screenshots for UI changes
4. Describe changes in detail
5. Reference related issues

## Issue Reporting

1. Use the provided template
2. Include:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots if applicable

## Model Training (Advanced)

1. Dataset preparation:
   ```bash
   python scripts/prepare_dataset.py --input ./data/raw --output ./data/processed
   ```

2. Training new face recognition model:
   ```bash
   python scripts/train.py --config configs/arcface_r100.yaml
   ```

3. Model conversion for production:
   ```bash
   python scripts/convert_model.py --input ./models/trained --output ./models/prod
   ```

## Code Review Process

1. Two maintainers must approve
2. All CI checks must pass
3. 72-hour waiting period for significant changes
4. Backward compatibility required for API changes