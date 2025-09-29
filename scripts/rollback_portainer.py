#!/usr/bin/env python
"""
Rollback Portainer Deployment Script

This script rolls back a Portainer stack to a previous version.
It retrieves the previous successful image tag and updates the stack.
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
    parser = argparse.ArgumentParser(description='Rollback Portainer deployment')
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
    parser.add_argument('--registry-url', default=os.getenv('DOCKER_REGISTRY_URL'),
                        help='Docker registry URL')
    parser.add_argument('--project-path', default=os.getenv('CI_PROJECT_PATH'),
                        help='Project path in registry')
    parser.add_argument('--previous-tag', default=os.getenv('PREVIOUS_TAG'),
                        help='Previous image tag to rollback to')
    parser.add_argument('--artifact-path', default=os.getenv('ARTIFACT_PATH', 'artifacts/last_successful_tag.json'),
                        help='Path to artifact file containing last successful tag')
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


def get_previous_tag(args):
    """Get the previous successful tag to rollback to."""
    # If a specific tag is provided, use it
    if args.previous_tag:
        print(f"Using provided previous tag: {args.previous_tag}")
        return args.previous_tag
    
    # Otherwise, try to read from artifact file
    try:
        if os.path.exists(args.artifact_path):
            with open(args.artifact_path, 'r') as f:
                data = json.load(f)
                tag = data.get('last_successful_tag')
                if tag:
                    print(f"Using last successful tag from artifact: {tag}")
                    return tag
    except Exception as e:
        print(f"Warning: Could not read previous tag from artifact: {e}")
    
    # If no tag is found, query the registry or Portainer API
    tag = query_previous_tag_from_registry(args)
    if tag:
        return tag
    
    print("Error: Could not determine previous tag for rollback")
    sys.exit(1)


def query_previous_tag_from_registry(args):
    """Query the Docker registry for previous tags."""
    # This is a simplified example. In a real implementation, you would:
    # 1. Query the Docker registry API for image tags
    # 2. Filter by branch/environment
    # 3. Sort by date
    # 4. Return the most recent tag before the current one
    
    print("Querying registry for previous tags...")
    
    # For demonstration purposes, we'll just use a fallback tag
    branch = os.getenv('CI_COMMIT_REF_NAME', 'main')
    fallback_tag = f"{branch}-latest"
    print(f"Using fallback tag: {fallback_tag}")
    return fallback_tag


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


def update_stack(portainer_url, api_key, stack_id, env_id, compose_content, prune=False, pull=True):
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
    """Main function to rollback Portainer deployment."""
    args = parse_arguments()
    validate_args(args)
    
    # Get the previous tag to rollback to
    previous_tag = get_previous_tag(args)
    
    # Read and update compose file
    compose_data = read_compose_file(args.compose_file)
    compose_data = update_image_tags(
        compose_data, args.registry_url, args.project_path, previous_tag
    )
    
    # Convert to YAML string
    compose_content = yaml.dump(compose_data)
    
    # Get stack ID
    stack_id = get_stack_id(args.portainer_url, args.api_key, args.env_id, args.stack_name)
    if not stack_id:
        print(f"Error: Stack {args.stack_name} not found")
        sys.exit(1)
    
    # Update stack with previous version
    print(f"Rolling back stack {args.stack_name} to tag {previous_tag}...")
    update_stack(args.portainer_url, args.api_key, stack_id, args.env_id, compose_content, pull=True)
    
    print("Rollback completed successfully!")
    
    # Record the rollback in a log file
    try:
        rollback_log = os.path.join(os.path.dirname(args.artifact_path), 'rollback_history.json')
        history = []
        if os.path.exists(rollback_log):
            with open(rollback_log, 'r') as f:
                history = json.load(f)
        
        history.append({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stack': args.stack_name,
            'environment': os.getenv('CI_COMMIT_REF_NAME', 'unknown'),
            'rolled_back_to': previous_tag
        })
        
        os.makedirs(os.path.dirname(rollback_log), exist_ok=True)
        with open(rollback_log, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not record rollback history: {e}")


if __name__ == "__main__":
    main()