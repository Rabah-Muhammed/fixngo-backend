set -o errexit

pip install -r backend/requirements.txt


python manage.py collectstatic --no-input

python manage.py migrate