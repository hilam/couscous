import os

import flet as ft
from dotenv import load_dotenv

from app.app import app_run

load_dotenv()

ft.run(
    app_run,
    host=os.getenv("APP_WEB_HOST", "127.0.0.1"),
    port=int(os.getenv("APP_SERVER_PORT", "8550")),
)
