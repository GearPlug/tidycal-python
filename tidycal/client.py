from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session

import requests

from tidycal.exceptions import UnauthorizedError, WrongFormatInputError, BookingsLimitExceededError


class Client(object):
    URL = "https://tidycal.com/"
    AUTH_URL = "https://tidycal.com/oauth/authorize"
    TOKEN_URL = "https://tidycal.com/oauth/token"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        self.TOKEN = None

    def authorization_url(self):
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": "code",
        }

        return self.AUTH_URL + "?" + urlencode(params)

    def get_access_token(self, code):
        tidycal = OAuth2Session(self.CLIENT_ID, redirect_uri=self.REDIRECT_URI)
        self.TOKEN = tidycal.fetch_token(self.TOKEN_URL, code=code, client_secret=self.CLIENT_SECRET)
        self.set_token(self.TOKEN)
        return self.TOKEN

    def set_token(self, access_token):
        self.headers.update(Authorization=f"Bearer {access_token['access_token']}")

    def get_current_user(self):
        response = requests.get(self.URL + 'api/me', headers=self.headers)
        return self.parse(response)

    def list_bookings(self):
        response = requests.get(self.URL + 'api/bookings', headers=self.headers)
        return self.parse(response)

    def list_booking_types(self):
        response = requests.get(self.URL + 'api/booking-types', headers=self.headers)
        return self.parse(response)

    def list_contacts(self):
        response = requests.get(self.URL + 'api/contacts', headers=self.headers)
        return self.parse(response)

    def parse(self, response):
        status_code = response.status_code
        if "Content-Type" in response.headers and "application/json" in response.headers["Content-Type"]:
            try:
                r = response.json()
            except ValueError:
                r = response.text
        else:
            r = response.text
        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 406:
            raise BookingsLimitExceededError(r)
        if status_code == 500:
            raise Exception
        return r