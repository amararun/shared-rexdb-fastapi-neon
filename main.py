from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enhanced logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
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

# Load environment variables
NEON_PROJECT_ID = os.getenv('NEON_PROJECT_ID')
NEON_HOST = os.getenv('NEON_HOST')
NEON_API_KEY = os.getenv('NEON_API_KEY')
NEON_BRANCH_ID = os.getenv('NEON_BRANCH_ID')

# Validate environment variables
if not all([NEON_PROJECT_ID, NEON_HOST, NEON_API_KEY, NEON_BRANCH_ID]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

class ProjectCreate(BaseModel):
    project: dict

async def create_database_with_retry(client, url: str, headers: dict, payload: dict, max_retries: int = 3) -> Optional[dict]:
    """Attempt to create database with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.debug(f"Database creation attempt {attempt + 1}/{max_retries}")
            response = await client.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            logger.debug(f"Database creation response: {response_data}")
            
            if response.status_code == 423:  # Locked
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    logger.info(f"Project locked, waiting {wait_time} seconds before retry")
                    await asyncio.sleep(wait_time)
                    continue
            
            response.raise_for_status()
            return response_data
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise
    return None

@app.post("/api/create-neon-db")
async def create_neon_db(request: ProjectCreate):
    logger.debug("Received create database request")
    
    try:
        nickname = request.project.get('name')
        if not nickname or not nickname.strip():
            raise HTTPException(status_code=422, detail="Database nickname cannot be empty")
            
        safe_nickname = "".join(
            c.lower() for c in nickname 
            if c.isalnum() or c in '-_'
        )
        
        owner_name = f"user_{safe_nickname}"
        
        headers = {
            "Authorization": f"Bearer {NEON_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Create role
            create_role_url = f"https://console.neon.tech/api/v2/projects/{NEON_PROJECT_ID}/branches/{NEON_BRANCH_ID}/roles"
            create_role_payload = {
                "role": {
                    "name": owner_name
                }
            }
            
            logger.debug(f"Creating role: {owner_name}")
            role_response = await client.post(create_role_url, headers=headers, json=create_role_payload)
            logger.debug(f"Role creation response: {role_response.text}")
            
            if role_response.status_code >= 400:
                logger.error(f"Role creation failed: {role_response.status_code} - {role_response.text}")
                raise HTTPException(
                    status_code=role_response.status_code,
                    detail=f"Role creation failed: {role_response.text}"
                )
            
            # Create database with retry
            create_db_url = f"https://console.neon.tech/api/v2/projects/{NEON_PROJECT_ID}/branches/{NEON_BRANCH_ID}/databases"
            create_db_payload = {
                "database": {
                    "name": safe_nickname,
                    "owner_name": owner_name
                }
            }
            
            logger.debug("Attempting database creation")
            db_response = await create_database_with_retry(
                client, 
                create_db_url, 
                headers, 
                create_db_payload
            )
            
            if not db_response:
                raise HTTPException(status_code=500, detail="Failed to create database after retries")
            
            # Get password
            logger.debug(f"Retrieving password for role: {owner_name}")
            password_url = f"https://console.neon.tech/api/v2/projects/{NEON_PROJECT_ID}/branches/{NEON_BRANCH_ID}/roles/{owner_name}/reveal_password"
            
            password_response = await client.get(password_url, headers=headers)
            logger.debug(f"Password retrieval response status: {password_response.status_code}")
            
            if password_response.status_code >= 400:
                logger.error(f"Password retrieval failed: {password_response.status_code} - {password_response.text}")
                raise HTTPException(
                    status_code=password_response.status_code,
                    detail=f"Failed to retrieve password: {password_response.text}"
                )
            
            password_data = password_response.json()
            password = password_data.get("password")
            
            if not password:
                logger.error("No password in response")
                raise HTTPException(status_code=500, detail="Password not found in response")
            
            response_data = {
                "hostname": NEON_HOST,
                "database_name": safe_nickname,
                "database_owner": owner_name,
                "database_owner_password": password,
                "port": 5432,
                "database_type": "postgresql",
                "database_nickname": nickname
            }
            
            logger.debug("Successfully created database and retrieved credentials")
            return response_data
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test():
    return {"status": "ok"}