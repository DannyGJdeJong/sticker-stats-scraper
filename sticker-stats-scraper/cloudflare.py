import requests
import logging

from .constants import CLOUDFLARE_ACCOUNT_IDENTIFIER, CLOUDFLARE_DATABASE_IDENTIFIER, CLOUDFLARE_API_TOKEN

# Set up logging
logger = logging.getLogger(__name__)

# Run a query on the Cloudflare database
def run_query(query, params = None):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_IDENTIFIER}/d1/database/{CLOUDFLARE_DATABASE_IDENTIFIER}/query"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "params": params,
        "sql": query,
    }

    res = requests.post(url, headers=headers, json=body)

    response_body = res.json()

    logger.debug(response_body)

    if not response_body["success"]:
        logger.error(response_body)
        return

    for result in response_body["result"]:
        if not result["success"]:
            logger.error(res.json())

# Insert total pack stats into database
def insert_total_pack_usage(pack_id: str, datetime: str, total_usage: int, total_installed: int, total_removed: int):
    query = """
    INSERT INTO total_pack_usage ("pack_id", "datetime", "total_usage", "total_installed", "total_removed")
    VALUES (?, ?, ?, ?, ?);
    """

    run_query(query, [pack_id, datetime, total_usage, total_installed, total_removed])
