#!/usr/bin/env python
"""
Seed QA Data Script

This script generates synthetic test data using Faker and saves it to JSON files.
It can be used to populate test environments with realistic but non-sensitive data.
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta

from faker import Faker

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Seed QA data for testing')
    parser.add_argument('--env', default='qa', choices=['dev', 'qa', 'staging', 'prod'],
                        help='Environment to seed data for')
    parser.add_argument('--count', type=int, default=100,
                        help='Number of records to generate')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducible data generation')
    parser.add_argument('--out', default='data/test_users.json',
                        help='Output file path')
    parser.add_argument('--type', default='users', 
                        choices=['users', 'transactions', 'products', 'all'],
                        help='Type of data to generate')
    return parser.parse_args()

def ensure_directory_exists(file_path):
    """Ensure the directory for the file exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def generate_users(fake, count):
    """Generate synthetic user data."""
    users = []
    for _ in range(count):
        user = {
            'id': fake.uuid4(),
            'email': fake.email(),
            'username': fake.user_name(),
            'name': fake.name(),
            'phone': fake.phone_number(),
            'address': {
                'street': fake.street_address(),
                'city': fake.city(),
                'state': fake.state(),
                'zipcode': fake.zipcode(),
                'country': fake.country()
            },
            'created_at': fake.date_time_this_year().isoformat(),
            'is_active': random.choice([True, False]),
            'role': random.choice(['user', 'admin', 'tester', 'manager'])
        }
        users.append(user)
    return users

def generate_transactions(fake, count, user_ids=None):
    """Generate synthetic transaction data."""
    if not user_ids:
        user_ids = [fake.uuid4() for _ in range(count // 5)]
    
    transactions = []
    for _ in range(count):
        transaction = {
            'id': fake.uuid4(),
            'user_id': random.choice(user_ids),
            'amount': round(random.uniform(10.0, 1000.0), 2),
            'currency': random.choice(['USD', 'EUR', 'GBP', 'NGN']),
            'status': random.choice(['completed', 'pending', 'failed', 'refunded']),
            'type': random.choice(['payment', 'refund', 'deposit', 'withdrawal']),
            'created_at': fake.date_time_this_year().isoformat(),
            'updated_at': fake.date_time_this_year().isoformat(),
            'reference': fake.bothify(text='TRX-????-########'),
            'description': fake.sentence()
        }
        transactions.append(transaction)
    return transactions

def generate_products(fake, count):
    """Generate synthetic product data."""
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Beauty', 'Sports', 'Food']
    products = []
    for _ in range(count):
        product = {
            'id': fake.uuid4(),
            'name': fake.catch_phrase(),
            'description': fake.paragraph(),
            'price': round(random.uniform(5.0, 500.0), 2),
            'category': random.choice(categories),
            'sku': fake.bothify(text='SKU-????-########'),
            'in_stock': random.choice([True, False]),
            'stock_quantity': random.randint(0, 100),
            'created_at': fake.date_time_this_year().isoformat(),
            'updated_at': fake.date_time_this_year().isoformat()
        }
        products.append(product)
    return products

def main():
    """Main function to generate and save test data."""
    args = parse_arguments()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        fake = Faker()
        Faker.seed(args.seed)
    else:
        fake = Faker()
    
    print(f"Generating {args.count} records of {args.type} data for {args.env} environment...")
    
    # Generate data based on type
    if args.type == 'users' or args.type == 'all':
        users = generate_users(fake, args.count)
        user_file = args.out if args.type == 'users' else 'data/test_users.json'
        ensure_directory_exists(user_file)
        with open(user_file, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"Generated {len(users)} users and saved to {user_file}")
        
        # Extract user IDs for transactions if generating all
        user_ids = [user['id'] for user in users]
    else:
        user_ids = None
    
    if args.type == 'transactions' or args.type == 'all':
        transactions = generate_transactions(fake, args.count, user_ids)
        transaction_file = args.out if args.type == 'transactions' else 'data/test_transactions.json'
        ensure_directory_exists(transaction_file)
        with open(transaction_file, 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"Generated {len(transactions)} transactions and saved to {transaction_file}")
    
    if args.type == 'products' or args.type == 'all':
        products = generate_products(fake, args.count)
        product_file = args.out if args.type == 'products' else 'data/test_products.json'
        ensure_directory_exists(product_file)
        with open(product_file, 'w') as f:
            json.dump(products, f, indent=2)
        print(f"Generated {len(products)} products and saved to {product_file}")
    
    print("Data Seeding Completed Successfully!")

if __name__ == "__main__":
    main()