import os

from dotenv import load_dotenv

load_dotenv()

API_PROTOCOL = os.getenv('COUSCOUS_API_PROTOCOL')
API_HOST = os.getenv('COUSCOUS_API_HOST')
API_PORT = os.getenv('COUSCOUS_API_PORT')

API_URI = (
    f"{API_PROTOCOL}://{API_HOST}:{API_PORT}"
    if API_PORT and int(API_PORT) > 1024
    else f"{API_PROTOCOL}://{API_HOST}"
)

API_VERSION = 'v1'
API_URL = f'{API_URI}/{API_VERSION}'

API_ROUTES = {
    'login': f'{API_URL}/login',
    'register': f'{API_URL}/register',
}
