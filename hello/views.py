import os
import logging
import requests

from django.shortcuts import render

from .models import Greeting

logger = logging.getLogger('testlogger')


def index(request):
    return render(request, "index.html")

def authorize(request):
    # Set ENV variables
    CLIENT_ID = os.environ.get('RIPPLING_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('RIPPLING_CLIENT_SECRET', '')
    TOKEN_URL = os.environ.get('RIPPLING_TOKEN_URL', '')
    # 'https://warm-taiga-61775-50933b0ebe0c.herokuapp.com/authorize'
    redirect_uri = os.environ.get('DEMO_WEBSITE_REDIRECT_URL', '')

    # Get Basic Auth header
    def get_basic_auth_header(client_id, client_secret):
        import base64

        """Encodes client_id and client_secret into a Basic Auth header."""
        auth_str = f"{client_id}:{client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        return {'Authorization': f'Basic {b64_auth_str}'}

    headers = get_basic_auth_header(CLIENT_ID, CLIENT_SECRET)
    code = request.GET.get('code')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code != 200:
        logger.error(f'Failed to retrieve access token: {response.status_code}')
        return render(request, "authorize.html")

    tokens = response.json()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    def get_company_info(access_token):
        """Retrieve information about the current company using the access token."""
        api_url = 'https://api.rippling.com/platform/api/companies/current'
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            return None

        return response.json()


    company_info = get_company_info(access_token)
    logger.info(f'Company info: {company_info}')

    return render(request, "authorize.html")


def db(request):
    # If you encounter errors visiting the `/db/` page on the example app, check that:
    #
    # When running the app on Heroku:
    #   1. You have added the Postgres database to your app.
    #   2. You have uncommented the `psycopg` dependency in `requirements.txt`, and the `release`
    #      process entry in `Procfile`, git committed your changes and re-deployed the app.
    #
    # When running the app locally:
    #   1. You have run `./manage.py migrate` to create the `hello_greeting` database table.

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
