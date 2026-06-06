import os

import flet as ft
from dotenv import load_dotenv

from app.app import app_run

load_dotenv()

ft.run(app_run, port=int(os.getenv("APP_SERVER_PORT", "8550")))
