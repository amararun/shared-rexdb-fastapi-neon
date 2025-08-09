# Neon Database Management Service

## Live App
A full version of app using this backed is deployed and available at [app.tigzig.com](https://app.tigzig.com)  
DATS-4 : Database AI Suite - Version 4

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

The following environment variables are required for the application to function. You can create a `.env` file in the root of the project and add the following variables. A `.env.example` file is provided as a template.

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

## Running the Application

To start the server, execute:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

The service will be available at `http://localhost:$PORT`. If the `PORT` environment variable is not set, the application will default to port `8000`.

## API Endpoints

### 1. Create Neon Database
- **Endpoint**: `/api/create-neon-db`
- **Method**: POST
- **Description**: Creates a new PostgreSQL database with an associated user role. The endpoint includes a retry mechanism with exponential backoff to handle cases where the Neon project is locked.
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
- **Description**: Simple health check endpoint to verify service status.
- **Output**: 
  ```json
  {"status": "ok"}
  ```

## CORS Configuration

The service includes CORS middleware configured for a list of domains. To add a new domain, you need to update the `allow_origins` list in the `main.py` file.

For example, to add `https://newdomain.com`, you would modify the `add_middleware` call as follows:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://your-frontend-app.com",
    "https://your-ai-tool.com",
    "http://localhost:1234", # Example for local development
    "http://localhost:5678"  # Example for another local service
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For testing or temporary purposes, you can allow all domains by setting `allow_origins` to `["*"]`.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note:** This is not recommended for production environments. It is always advisable to have a whitelist of trusted domains to prevent security vulnerabilities.


-------
Built by Amar Harolikar // More tools at [app.tigzig.com](https://app.tigzig.com)  // [LinkedIn Profile](https://www.linkedin.com/in/amarharolikar)
