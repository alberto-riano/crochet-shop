#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/crochet-shop}"

cd "$PROJECT_DIR"
source venv/bin/activate

git pull --ff-only
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
sudo systemctl status gunicorn --no-pager --lines=5

echo "Deploy completado"