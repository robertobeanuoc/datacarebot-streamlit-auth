"""A small, reusable Authentik OIDC login gate for Streamlit apps.

Wraps Streamlit's native `st.login()`/`st.user` support (Streamlit >= 1.42),
so every Streamlit app in the ecosystem gates access behind the same
Authentik login without reimplementing it - the Streamlit equivalent of the
`auth.py` blueprint duplicated across the Flask apps (food_recognition_model,
strava_to_db), just as a shared package instead, since apps here otherwise
copy small pieces of boilerplate rather than depend on each other directly.

This package holds no secrets and talks to no specific Authentik instance -
the consuming app configures its own OIDC client via Streamlit's standard
`.streamlit/secrets.toml` `[auth]` section (redirect_uri, cookie_secret,
client_id, client_secret, server_metadata_url), the same way Streamlit's
built-in auth support expects. Each app provisions its own Authentik OIDC
client (different redirect_uri/port per app), matching how every other app
in this ecosystem already has its own client - only the login-gate *code* is
shared, not credentials.

Usage:

    import streamlit as st
    from streamlit_authentik_login import require_login

    user = require_login(app_name="CGM Dashboard")
    st.write(f"Hello, {user['name']}")
"""

import streamlit as st

__all__ = ["require_login", "render_logout_button"]


def require_login(app_name: str = "This app") -> dict:
    """Gate the rest of the current page behind an authenticated Authentik
    session. Renders a login prompt and calls `st.stop()` if the visitor
    isn't logged in yet - nothing after this call runs until they are.

    Returns the logged-in user's identity as a plain dict with `sub`,
    `email`, `name` - the same shape `session['user']` uses in this
    ecosystem's Flask apps, so downstream code (e.g. scoping a database
    query by owner) looks the same regardless of which app it's in.
    """
    if not st.user.is_logged_in:
        st.title(app_name)
        st.write("Please log in to continue.")
        if st.button("Log in with Authentik"):
            st.login()
        st.stop()

    return {
        "sub": st.user.get("sub"),
        "email": st.user.get("email"),
        "name": st.user.get("name") or st.user.get("preferred_username"),
    }


def render_logout_button(label: str = "Log out") -> None:
    """Render a logout button in the sidebar. Call this once, after
    `require_login()`, from any page that should offer a way out."""
    if st.sidebar.button(label):
        st.logout()
