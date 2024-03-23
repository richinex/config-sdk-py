
# Python SDK for Config-Server-SSE Integration

This Python-based SDK simplifies the process of integrating with config-server-sse endpoints, enabling Python applications to receive real-time configuration updates efficiently and robustly. It incorporates exponential backoff retry strategies and comprehensive error handling to deal with connectivity issues effectively.

## Features

- **Real-Time Configuration Updates**: Utilize Server-Sent Events (SSE) to receive configuration changes as they happen.
- **Exponential Backoff**: Employ an exponential backoff strategy for reconnection attempts to enhance connection stability.
- **Robust Error Handling**: Comprehensive error handling mechanisms for dealing with connectivity and data parsing issues.
- **Asyncio Support**: Designed with `asyncio` and `httpx` for asynchronous operation, fitting well into modern async Python applications.

## Getting Started

### Prerequisites

- Python 3.7 or newer.
- `httpx` and `pydantic` libraries. Installation instructions are provided below.

### Installation

Install the required packages using pip:

```bash
pip install httpx pydantic
```

### Usage Example

Below is a minimal FastAPI application example that utilizes the SDK to listen for configuration updates and serve the latest configuration via a simple HTTP endpoint:

```python
from fastapi import FastAPI, HTTPException, Response
import asyncio
import os
from listener import listen_for_config_updates, ServerConfig
from pydantic import BaseModel

class Config(BaseModel):
    settings: dict

# Global variable to store the latest config received
latest_config = None

def update_handler(server_config: ServerConfig):
    global latest_config
    latest_config = Config(settings=server_config.settings)
    print("Updated config:", latest_config)

async def start_listening(max_retries: int = 5):
    sse_url = os.getenv('SSE_URL', 'http://localhost:8080/sse/dev')
    await listen_for_config_updates(sse_url, update_handler, max_retries=max_retries)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_listening())

@app.get("/")
async def display_config():
    if not latest_config:
        raise HTTPException(status_code=404, detail="Config not available yet")
    return latest_config
```

## Contributing

Your contributions are welcome! Feel free to submit pull requests, report bugs, or suggest new features.

## License

This SDK is available under the MIT License. For more information, see the LICENSE file in this repository.
