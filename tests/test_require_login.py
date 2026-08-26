from unittest.mock import MagicMock, patch

import pytest

from streamlit_authentik_login import render_logout_button, require_login


class _StopCalled(Exception):
    """Stand-in for streamlit.stop()'s real (internal) exception, just to
    prove require_login() didn't fall through past the login gate."""


def _fake_user(is_logged_in: bool, **claims):
    user = MagicMock()
    user.is_logged_in = is_logged_in
    user.get.side_effect = lambda key, default=None: claims.get(key, default)
    return user


@patch("streamlit_authentik_login.st")
def test_require_login_returns_the_users_identity_when_logged_in(mock_st):
    mock_st.user = _fake_user(True, sub="user-123", email="a@example.com", name="Ada")

    identity = require_login()

    assert identity == {"sub": "user-123", "email": "a@example.com", "name": "Ada"}
    mock_st.stop.assert_not_called()


@patch("streamlit_authentik_login.st")
def test_require_login_falls_back_to_preferred_username_when_name_is_missing(mock_st):
    mock_st.user = _fake_user(True, sub="user-123", email="a@example.com", preferred_username="ada")

    identity = require_login()

    assert identity["name"] == "ada"


@patch("streamlit_authentik_login.st")
def test_require_login_starts_the_oidc_flow_immediately_when_not_logged_in(mock_st):
    """No interstitial button: an unauthenticated visitor is bounced straight into the OIDC
    flow, so a visitor with an existing Authentik session elsewhere round-trips silently."""
    mock_st.user = _fake_user(False)
    mock_st.stop.side_effect = _StopCalled

    with pytest.raises(_StopCalled):
        require_login()

    mock_st.login.assert_called_once()
    mock_st.stop.assert_called_once()


@patch("streamlit_authentik_login.st")
def test_render_logout_button_logs_out_when_clicked(mock_st):
    mock_st.sidebar.button.return_value = True

    render_logout_button()

    mock_st.logout.assert_called_once()


@patch("streamlit_authentik_login.st")
def test_render_logout_button_does_nothing_when_not_clicked(mock_st):
    mock_st.sidebar.button.return_value = False

    render_logout_button()

    mock_st.logout.assert_not_called()
