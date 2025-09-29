"""
Upload a directory of artifacts to S3-compatible storage.
Requires env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, and optional AWS_ENDPOINT_URL (for MinIO or custom).
"""

import argparse
import os
import sys
import boto3


def upload_directory(s3, bucket: str, prefix: str, local_path: str) -> None:
    for root, _, files in os.walk(local_path):
        for name in files:
            full = os.path.join(root, name)
            key = os.path.join(prefix, os.path.relpath(full, start=local_path)).replace("\\", "/")
            print(f"Uploading {full} -> s3://{bucket}/{key}")
            s3.upload_file(full, bucket, key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()

    session = boto3.session.Session()
    endpoint = os.getenv("AWS_ENDPOINT_URL")
    s3 = session.client("s3", endpoint_url=endpoint) if endpoint else session.client("s3")

    if not os.path.isdir(args.path):
        print(f"Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    upload_directory(s3, args.bucket, args.prefix, args.path)


if __name__ == "__main__":
    main()

