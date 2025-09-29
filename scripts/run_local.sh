#!/bin/bash
set -euo pipefail

echo "Running unit tests"
pytest tests/unit -q

echo "Starting integration services"
docker-compose -f docker-compose.integration.yml up -d
trap 'docker-compose -f docker-compose.integration.yml down' EXIT

echo "Running integration tests"
pytest tests/integration -q

echo "Running BDD tests"
behave

echo "Done"

