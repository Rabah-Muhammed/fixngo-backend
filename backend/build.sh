set -o errexit

pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput 

if [[ $CREATE_SUPERUSER == "True" ]]; then
    python manage.py createsuperuser --no-input
fi