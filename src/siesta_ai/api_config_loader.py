import os
import requests

def load_config_from_api(config_type: str) -> dict:
    """Fetches configuration from CONFIG_API_BASE/{config_type} endpoint."""
    base_url = os.getenv("CONFIG_API_BASE")
    if not base_url:
        raise ValueError("CONFIG_API_BASE environment variable is not set.")

    try:
        response = requests.get(f"{base_url}/{config_type}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch config from /{config_type}: {e}")