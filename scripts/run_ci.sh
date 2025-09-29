#!/bin/bash
set -euo pipefail

echo "Checking VPN requirement"
bash scripts/vpn_check.sh || (echo "VPN check failed" && exit 1)

echo "Installing dependencies"
pip install -r requirements.txt
pip install -r requirements-dev.txt || true

echo "Static checks"
black --check . || true
flake8 . || true
pylint src tests || true

echo "Unit tests"
mkdir -p reports/junit reports/allure-results
pytest tests/unit --junitxml=reports/junit/unit.xml --alluredir=reports/allure-results --maxfail=1 -q

echo "Integration tests"
docker-compose -f docker-compose.integration.yml up -d
pytest tests/integration --junitxml=reports/junit/integration.xml --alluredir=reports/allure-results --fixtures-per-test || (docker-compose -f docker-compose.integration.yml down && exit 1)
docker-compose -f docker-compose.integration.yml down

echo "Done"

