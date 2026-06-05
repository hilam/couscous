import secrets
from typing import Any
from urllib.parse import urlencode

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc7636 import create_s256_code_challenge

from database.service.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    OAUTH_REDIRECT_URI,
)


def _provider_config(provider: str) -> dict[str, Any] | None:
    if provider == "google":
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            return None
        return {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "scope": "openid email profile",
            "userinfo_name_key": "name",
            "userinfo_id_key": "sub",
        }
    if provider == "github":
        if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
            return None
        return {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "read:user",
            "userinfo_name_key": "login",
            "userinfo_id_key": "id",
        }
    return None


_oauth_states: dict[str, dict[str, str]] = {}


def is_provider_available(provider: str) -> bool:
    return _provider_config(provider) is not None


def get_authorization_url(provider: str) -> tuple[str, str]:
    config = _provider_config(provider)
    if not config:
        msg = f"OAuth provider '{provider}' is not configured"
        raise ValueError(msg)

    code_verifier = secrets.token_urlsafe(32)
    code_challenge = create_s256_code_challenge(code_verifier)
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": OAUTH_REDIRECT_URI,
        "scope": config["scope"],
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    uri = f"{config['authorization_url']}?{urlencode(params)}"
    _oauth_states[state] = {"code_verifier": code_verifier, "provider": provider}
    return uri, state


async def handle_callback(code: str, state: str) -> dict[str, Any]:
    stored = _oauth_states.pop(state, None)
    if not stored:
        msg = "Sessão OAuth inválida ou expirada"
        raise ValueError(msg)

    provider = stored["provider"]
    code_verifier = stored["code_verifier"]
    config = _provider_config(provider)
    if not config:
        msg = f"Provider '{provider}' not configured"
        raise ValueError(msg)

    client = AsyncOAuth2Client(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=OAUTH_REDIRECT_URI,
    )
    token = await client.fetch_token(
        config["token_url"],
        code=code,
        code_verifier=code_verifier,
    )

    async with httpx.AsyncClient() as hc:
        resp = await hc.get(
            config["userinfo_url"],
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        resp.raise_for_status()
        userinfo = resp.json()

    oauth_id = str(userinfo[config["userinfo_id_key"]])
    name = userinfo[config["userinfo_name_key"]]

    return {
        "provider": provider,
        "oauth_id": oauth_id,
        "name": name,
    }
