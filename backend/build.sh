#!/bin/bash
set -o errexit

# Install dependencies
pip install -r /opt/render/project/src/backend/requirements.txt

# Collect static files
python /opt/render/project/src/backend/manage.py collectstatic --no-input

# Run migrations
python /opt/render/project/src/backend/manage.py migrate