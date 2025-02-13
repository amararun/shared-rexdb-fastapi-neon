# Neon Database Management Service

This backend service facilitates the creation and management of PostgreSQL databases using the Neon API. It acts as an intermediary between frontend applications and Neon's infrastructure, handling database creation, user role management, and credential distribution.

## Quick Start

### Clone Repository
```bash
git clone [repository-url] .
```

### Build Command
To install the required dependencies, run:
```bash
pip install -r requirements.txt
```

## Environment Variables

The following environment variables are required for the application to function:

- `NEON_PROJECT_ID`: Your Neon project identifier
  - Available from Neon Console
  - Used to identify which Neon project to work with

- `NEON_HOST`: Neon database host address
  - Available from Neon Console
  - The hostname where your databases will be created

- `NEON_API_KEY`: Authentication key for Neon API
  - Available from Neon Console
  - Required for authenticating API requests to Neon

- `NEON_BRANCH_ID`: Branch identifier for database operations
  - Available from Neon Console > Branches > Main > Branch ID
  - Typically corresponds to your main branch

## API Endpoints

### 1. Create Neon Database
- **Endpoint**: `/api/create-neon-db`
- **Method**: POST
- **Description**: Creates a new PostgreSQL database with associated user role
- **Input**:
  ```json
  {
    "project": {
      "name": "database_nickname"
    }
  }
  ```
- **Output**:
  ```json
  {
    "hostname": "neon_host",
    "database_name": "safe_nickname",
    "database_owner": "owner_name",
    "database_owner_password": "generated_password",
    "port": 5432,
    "database_type": "postgresql",
    "database_nickname": "original_nickname"
  }
  ```

### 2. Health Check
- **Endpoint**: `/api/test`
- **Method**: GET
- **Description**: Simple health check endpoint to verify service status
- **Output**: `{"status": "ok"}`

## Running the Application

To start the server, execute:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

The service will be available at `http://localhost:$PORT` where `$PORT` is your specified port number.

## CORS Configuration

The service includes CORS middleware configured for the following domains:
- tigzig.com and its subdomains
- localhost development ports (8123, 5199)

For additional domains, update the CORS middleware configuration in `main.py`.

