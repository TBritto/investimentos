from __future__ import annotations

import os

from dotenv import load_dotenv
from openbb import obb


def load_settings() -> None:
    load_dotenv()
    fmp_api_key = os.getenv("FMP_API_KEY")
    if fmp_api_key:
        obb.user.credentials.fmp_api_key = fmp_api_key
