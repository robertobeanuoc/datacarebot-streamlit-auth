# streamlit-authentik-login

A small, reusable Authentik OIDC login gate for Streamlit apps in this
ecosystem. Wraps Streamlit's native `st.login()`/`st.user` support
(Streamlit >= 1.42) so every Streamlit app gates access behind the same
Authentik login without reimplementing it.

This package holds no secrets and is not tied to any specific Authentik
instance. Each consuming app provisions its own Authentik OIDC client
(its own `client_id`/`client_secret`/`redirect_uri`) - only the login-gate
*code* is shared here, the same way the ecosystem's Flask apps each keep
their own `auth.py` rather than depend on a shared library for it.

## Install

From a `requirements.txt`, pin a commit or tag:

```
git+https://github.com/robertobeanuoc/datacarebot-streamlit-auth.git@main
```

## Setup

1. Provision an Authentik OAuth2/OIDC provider + application for your app
   (same as any other app in this ecosystem - see
   `datacarebot-identity/authentik/scripts/create_oauth2_client.py`).
2. Configure Streamlit's built-in auth via `.streamlit/secrets.toml` (or the
   equivalent env vars) in your app:

   ```toml
   [auth]
   redirect_uri = "https://your-host:port/oauth2callback"
   cookie_secret = "a-random-secret-string"
   client_id = "..."
   client_secret = "..."
   server_metadata_url = "https://authentik-host/application/o/your-app-slug/.well-known/openid-configuration"
   ```

## Usage

```python
import streamlit as st
from streamlit_authentik_login import require_login, render_logout_button

user = require_login(app_name="My Dashboard")
render_logout_button()

st.write(f"Hello, {user['name']} ({user['email']})")
# user['sub'] is the same Authentik user UUID used across this ecosystem's
# other apps (sub_mode=USER_UUID) - use it to scope data by owner.
```
