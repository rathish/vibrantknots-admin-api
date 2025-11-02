#!/bin/bash

echo "Running tests with coverage..."
pytest --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=95

echo "Coverage report generated in htmlcov/index.html"
