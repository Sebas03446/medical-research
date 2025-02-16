# agent/setup.py
from setuptools import setup, find_namespace_packages

from pathlib import Path

# Get the absolute path to the backend directory
BACKEND_PATH = Path(__file__).parent.parent / 'backend'


setup(
    name="medical_agent",
    version="0.1.0",
    packages=find_namespace_packages(include=["agent", "agent.*"]),
    install_requires=[
        "anthropic",
        "python-dotenv",
        "pyyaml",
        f"medical_research_backend @ file://{BACKEND_PATH.resolve()}"
    ],
)
