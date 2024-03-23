# models.py
from pydantic import BaseModel
from typing import Dict, Any

class ServerConfig(BaseModel):
    """
    A Pydantic model representing the server configuration.

    Attributes:
        settings (Dict[str, Any]): A dictionary mapping configuration keys to their values.
            The values can be of any type, reflecting the flexible nature of the configuration.

    Example:
        >>> config = ServerConfig(settings={"debug_mode": True, "max_users": 100})
        >>> print(config.settings["debug_mode"])
        True
    """
    settings: Dict[str, Any]
