# example microservice
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import asyncio
import os
from listener import listen_for_config_updates, ServerConfig
from contextlib import asynccontextmanager

# Assuming your SDK returns a ServerConfig which needs to be converted to this Config
class Settings(BaseModel):
    ball_color: str
    ball_size: int
    ball_speed: int
    number_of_balls: int

class Config(BaseModel):
    settings: Settings

# Global variable to store the latest config received
latest_config = None

def update_handler(server_config: ServerConfig):
    global latest_config
    settings = Settings(**server_config.settings)
    latest_config = Config(settings=settings)
    print("Updated config:", latest_config)


async def start_listening(max_retries: int = 5):
    sse_url = os.getenv('SSE_URL', 'http://localhost:8080/sse/dev')
    await listen_for_config_updates(sse_url, update_handler, max_retries=max_retries)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_listening())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def display_config():
    if not latest_config:
        print(f"Config not available yet {latest_config}")
        raise HTTPException(status_code=404, detail="Config not available yet")

    config_json = latest_config.json()
    return Response(content=config_json, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8082)
