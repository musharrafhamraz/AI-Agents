# Utility Scripts

This directory contains utility scripts for managing the Validata platform.

## Available Scripts

### setup_db.py
Initializes the database schema by creating all required tables.

**Usage:**
```bash
python scripts/setup_db.py
```

**Prerequisites:**
- PostgreSQL must be running
- `.env` file must be configured with `DATABASE_URL`

### seed_data.py
Seeds the database with sample data for development and testing.

**Usage:**
```bash
python scripts/seed_data.py
```

## Development Workflow

1. Start Docker services:
   ```bash
   docker-compose up -d
   ```

2. Set up the database:
   ```bash
   python scripts/setup_db.py
   ```

3. (Optional) Seed sample data:
   ```bash
   python scripts/seed_data.py
   ```

4. Run the application:
   ```bash
   cd backend
   uvicorn api.main:app --reload
   ```
