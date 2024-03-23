import httpx
import asyncio
import json
from models import ServerConfig
from logger import get_logger

logger = get_logger()

async def listen_for_config_updates(sse_url: str, update_handler, max_retries: int = 5):
    """
    Starts listening for configuration updates from an SSE endpoint, with configurable retry behavior.

    Args:
        sse_url (str): The URL of the SSE endpoint to connect to.
        update_handler (callable): Function to call with the parsed ServerConfig whenever an update is received.
        max_retries (int, optional): Maximum number of connection retry attempts. Defaults to 5.
        backoff_factor (float, optional): Factor to determine the delay between retries. Defaults to 1.5.
    """
    async with SSEClient(sse_url, max_retries=max_retries) as client:
        await client.listen(update_handler)


class SSEClient:
    """
    A client for connecting to and listening for messages from an SSE (Server-Sent Events) endpoint.
    """

    def __init__(self, url: str, max_retries: int = 5):
        """
        Initializes the SSEClient with a URL and retry parameters.

        Args:
            url (str): The URL of the SSE endpoint.
            max_retries (int): The maximum number of retry attempts. Defaults to 5.
            backoff_factor (float): The factor by which the wait time increases after each retry. Defaults to 1.5.
        """
        self.url = url
        self.max_retries = max_retries
        self.backoff_factor = 1.5
        self.client = httpx.AsyncClient(timeout=None)

    async def __aenter__(self):
        """
        Asynchronous context manager entry point.
        """
        return self

    async def __aexit__(self):
        """
        Asynchronous context manager exit point. Closes the HTTP client.
        """
        await self.client.aclose()

    async def listen(self, update_handler):
        """
        Listens for updates from the SSE endpoint and handles them using the provided update handler.

        Args:
            update_handler (callable): A function to call with the parsed ServerConfig object
                                       whenever a new configuration is received.

        This method attempts to connect to the SSE endpoint and listens for incoming messages.
        If a message is received, it is parsed into a ServerConfig object and passed to the
        `update_handler`. The method will retry connecting to the endpoint up to `max_retries` times
        with an exponential backoff strategy.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                logger.info(f"Attempting to connect to the config server at {self.url}")
                async with self.client.stream("GET", self.url, headers={"Accept": "text/event-stream"}) as response:
                    logger.info(f"Connected to the config server at {self.url}")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            json_part = line.replace("data: ", "", 1).strip()
                            try:
                                config = ServerConfig.parse_raw(json_part)
                                update_handler(config)
                            except json.JSONDecodeError as e:
                                logger.error(f"Error decoding JSON: {e}")
            except httpx.HTTPError as e:
                retries += 1
                wait = self.backoff_factor ** retries
                logger.error(f"SSE connection error: {e}. Retrying in {wait:.2f} seconds.")
                await asyncio.sleep(wait)
            else:
                retries = 0
        logger.error("Maximum retries reached. Stopping listener.")
