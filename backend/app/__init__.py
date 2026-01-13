"""
AI-Powered Virtual Classroom backend package.

This module exposes the FastAPI application factory so that tests and
external tooling can import the app without triggering side-effects.
"""

from .main import create_app

__all__ = ["create_app"]

