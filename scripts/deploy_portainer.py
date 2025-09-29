#!/usr/bin/env python
"""
Deploy to Portainer Script

This script deploys a stack to Portainer using the Portainer API.
It reads the compose file, patches image tags, and calls the Portainer API to deploy.
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urljoin

import requests
import yaml


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Deploy to Portainer')
    parser.add_argument('--portainer-url', default=os.getenv('PORTAINER_URL'),
                        help='Portainer URL')
    parser.add_argument('--api-key', default=os.getenv('PORTAINER_API_KEY'),
                        help='Portainer API key')
    parser.add_argument('--env-id', type=int, default=int(os.getenv('PORTAINER_ENV_ID', 1)),
                        help='Portainer environment ID')
    parser.add_argument('--stack-name', default=os.getenv('STACK_NAME'),
                        help='Stack name')
    parser.add_argument('--compose-file', default=os.getenv('COMPOSE_FILE'),
                        help='Compose file path')
    parser.add_argument('--image-tag', default=os.getenv('IMAGE_TAG'),
                        help='Image tag to use')
    parser.add_argument('--registry-url', default=os.getenv('DOCKER_REGISTRY_URL'),
                        help='Docker registry URL')
    parser.add_argument('--project-path', default=os.getenv('CI_PROJECT_PATH'),
                        help='Project path in registry')
    parser.add_argument('--prune', action='store_true',
                        help='Prune services on deploy')
    parser.add_argument('--pull', action='store_true',
                        help='Pull images on deploy')
    return parser.parse_args()


def validate_args(args):
    """Validate command line arguments."""
    missing = []
    if not args.portainer_url:
        missing.append('--portainer-url or PORTAINER_URL')
    if not args.api_key:
        missing.append('--api-key or PORTAINER_API_KEY')
    if not args.stack_name:
        missing.append('--stack-name or STACK_NAME')
    if not args.compose_file:
        missing.append('--compose-file or COMPOSE_FILE')
    
    if missing:
        print(f"Error: Missing required arguments: {', '.join(missing)}")
        sys.exit(1)
    
    if not os.path.exists(args.compose_file):
        print(f"Error: Compose file not found: {args.compose_file}")
        sys.exit(1)


def read_compose_file(file_path):
    """Read and parse the compose file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading compose file: {e}")
        sys.exit(1)


def update_image_tags(compose_data, registry_url, project_path, image_tag):
    """Update image tags in the compose file."""
    if not registry_url or not project_path or not image_tag:
        print("Warning: Missing registry URL, project path, or image tag. Skipping image tag update.")
        return compose_data
    
    for service_name, service_config in compose_data.get('services', {}).items():
        if 'image' in service_config:
            # Only update images that match our project path
            if project_path.lower() in service_config['image'].lower():
                # Replace the image tag
                image_parts = service_config['image'].split(':')
                base_image = image_parts[0]
                service_config['image'] = f"{base_image}:{image_tag}"
                print(f"Updated image for service {service_name}: {service_config['image']}")
    
    return compose_data


def get_stack_id(portainer_url, api_key, env_id, stack_name):
    """Get the stack ID for an existing stack."""
    url = urljoin(portainer_url, f"/api/stacks")
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        stacks = response.json()
        for stack in stacks:
            if stack.get('Name') == stack_name and stack.get('EndpointId') == env_id:
                return stack.get('Id')
        
        return None
    except Exception as e:
        print(f"Error getting stack ID: {e}")
        return None


def create_stack(portainer_url, api_key, env_id, stack_name, compose_content, prune, pull):
    """Create a new stack in Portainer."""
    url = urljoin(portainer_url, f"/api/stacks")
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'name': stack_name,
        'stackFileContent': compose_content,
        'endpointId': env_id,
        'swarmId': '',  # Leave empty for standalone Docker or set for Swarm
        'env': [],  # Environment variables
        'prune': prune,
        'pullImage': pull
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Stack {stack_name} created successfully!")
        return response.json().get('Id')
    except Exception as e:
        print(f"Error creating stack: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def update_stack(portainer_url, api_key, stack_id, env_id, compose_content, prune, pull):
    """Update an existing stack in Portainer."""
    url = urljoin(portainer_url, f"/api/stacks/{stack_id}")
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'stackFileContent': compose_content,
        'env': [],  # Environment variables
        'prune': prune,
        'pullImage': pull
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Stack updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating stack: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def main():
    """Main function to deploy to Portainer."""
    args = parse_arguments()
    validate_args(args)
    
    # Read and update compose file
    compose_data = read_compose_file(args.compose_file)
    if args.image_tag and args.registry_url and args.project_path:
        compose_data = update_image_tags(
            compose_data, args.registry_url, args.project_path, args.image_tag
        )
    
    # Convert to YAML string
    compose_content = yaml.dump(compose_data)
    
    # Check if stack exists
    stack_id = get_stack_id(args.portainer_url, args.api_key, args.env_id, args.stack_name)
    
    # Deploy stack
    if stack_id:
        print(f"Updating existing stack {args.stack_name} (ID: {stack_id})...")
        update_stack(
            args.portainer_url, args.api_key, stack_id, args.env_id, 
            compose_content, args.prune, args.pull
        )
    else:
        print(f"Creating new stack {args.stack_name}...")
        create_stack(
            args.portainer_url, args.api_key, args.env_id, args.stack_name, 
            compose_content, args.prune, args.pull
        )
    
    print("Deployment completed successfully!")


if __name__ == "__main__":
    main()