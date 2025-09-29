## Testing Playbook


- Unit tests: `pytest tests/unit`
- Integration tests: `docker-compose -f docker-compose.integration.yml up -d && pytest tests/integration`
- E2E tests: `pytest tests/e2e -k 'smoke or critical' --headless`
- BDD: `behave`
- Reports (Allure): `allure generate reports/allure-results --clean -o reports/allure-report`

