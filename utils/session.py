"""Session management for user authentication state."""

_session = {
    "username": None,
    "logged_in": False,
    "demo_mode": False
}

def get_user():
    """Returns the current session dictionary."""
    return _session.copy()

def set_user(username, demo_mode=False):
    """Sets the current logged-in user."""
    _session["username"] = username
    _session["logged_in"] = True
    _session["demo_mode"] = demo_mode

def clear_user():
    """Clears the current session."""
    _session["username"] = None
    _session["logged_in"] = False
    _session["demo_mode"] = False

def is_logged_in():
    """Returns True if a user is logged in."""
    return _session["logged_in"]

def get_username():
    """Returns the current username or None."""
    return _session["username"]

def is_demo_mode():
    """Returns True if in demo mode."""
    return _session["demo_mode"]
