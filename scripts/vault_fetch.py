"""
Fetch secrets from HashiCorp Vault and export as environment variables.
Expected env vars: VAULT_ADDR, VAULT_ROLE (optional), VAULT_TOKEN (if not using approle/oidc), SECRET_PATHS (comma-separated path=ENV_PREFIX pairs)
Example: SECRET_PATHS="secret/data/ci/docker=DOCKER,secret/data/ci/portainer=PORTAINER"
"""

import os
import sys
import hvac


def main():
    vault_addr = os.getenv("VAULT_ADDR")
    if not vault_addr:
        print("VAULT_ADDR not set; skipping Vault fetch")
        return

    client = hvac.Client(url=vault_addr)

    # Basic token auth for simplicity; extend to approle/oidc as needed
    token = os.getenv("VAULT_TOKEN")
    if token:
        client.token = token
    if not client.is_authenticated():
        print("Vault authentication failed", file=sys.stderr)
        sys.exit(1)

    secret_specs = os.getenv("SECRET_PATHS", "").split(",")
    for spec in filter(None, secret_specs):
        path, _, prefix = spec.partition("=")
        prefix = prefix or "SECRET"
        read = client.secrets.kv.v2.read_secret_version(path=path)
        data = read.get("data", {}).get("data", {})
        for key, value in data.items():
            env_key = f"{prefix}_{key}".upper()
            print(f"export {env_key}='{value}'")


if __name__ == "__main__":
    main()

