# QA Test Automation Python Master Blueprint

Enterprise-grade QA/test automation scaffold built around Python (pytest, behave, Playwright/Selenium), GitLab CI, Portainer deployments, VPN enforcement, artifact management, reporting, monitoring, and rollback.

## Overview

This repository contains a comprehensive test automation framework designed for enterprise use. It includes:

- **Python Testing Stack**: pytest, behave, Playwright/Selenium
- **CI/CD Integration**: GitLab CI with VPN enforcement
- **Deployment**: Portainer integration with rollback capabilities
- **Reporting**: Allure, JUnit XML, HTML reports
- **Observability**: Prometheus metrics, structured logging
- **Security**: Vault integration for secrets management

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- GitLab Runner (for local CI execution)
- VPN access to corporate network
- Access to artifact registry and Portainer

## Getting Started

### Local Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development tools
   ```
4. Ensure VPN connection:
   ```bash
   ./scripts/vpn_check.sh
   ```

### Running Tests Locally

```bash
# Run unit tests
pytest tests/unit

# Run integration tests with ephemeral database
docker-compose -f docker-compose.dev.yml up -d
pytest tests/integration

# Run E2E tests with Playwright
pytest tests/e2e --headless

# Run BDD tests with Behave
behave
```

## CI/CD Pipeline

The CI/CD pipeline is configured in `.gitlab-ci.yml` and includes the following stages:

1. **Precheck**: Ensures VPN connectivity and prerequisites
2. **Build**: Installs dependencies and builds Docker images
3. **Test**: Runs unit, integration, and E2E tests
4. **Push**: Pushes Docker images to registry
5. **Deploy**: Deploys to appropriate environment via Portainer
6. **Post-deploy**: Runs health checks and smoke tests

## Directory Structure

```
├── README.md
├── pyproject.toml / requirements.txt
├── requirements-dev.txt
├── .gitlab-ci.yml
├── docker-compose.*.yml
├── Dockerfile
├── scripts/
│   ├── run_local.sh
│   ├── run_ci.sh
│   ├── seed_qa_data.py
│   ├── vpn_check.sh
│   └── deploy_portainer.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── perf/
│   ├── security/
│   └── a11y/
├── pages/
│   ├── ui_page_objects/
│   └── api_clients/
├── src/
├── reports/
├── configs/
│   ├── base.yaml
│   ├── dev.yaml
│   ├── qa.yaml
│   ├── staging.yaml
│   ├── prod.yaml
│   └── secrets.template.env
├── infra/
│   ├── k8s/
│   ├── terraform/
│   └── portainer_templates/
└── docs/
    ├── testing_playbook.md
    ├── onboarding.md
    ├── owner_matrix.md
    └── runbooks/
```

## Reporting

Test results are collected and reported using Allure:

```bash
# Generate Allure report
allure generate reports/allure-results --clean -o reports/allure-report
```

## Security Notes

- No plaintext secrets are stored in this repository
- All secrets are managed through Vault
- CI jobs inject secrets at runtime
- VPN enforcement ensures secure access to protected resources

## Documentation

For more detailed information, please refer to the documentation in the `docs/` directory:

- [Testing Playbook](docs/testing_playbook.md)
- [Onboarding Guide](docs/onboarding.md)
- [Test Ownership Matrix](docs/owner_matrix.md)
- [Runbooks](docs/runbooks/)

## License

