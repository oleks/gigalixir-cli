import requests
from . import auth
from . import netrc
import logging
import click
import stripe
import json

def create(host, email, card_number, card_exp_month, card_exp_year, card_cvc, password, accept_terms_of_service_and_privacy_policy):
    if not accept_terms_of_service_and_privacy_policy:
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Terms of Service: https://www.gigalixir.com/terms")
        logging.getLogger("gigalixir-cli").info("GIGALIXIR Privacy Policy: https://www.gigalixir.com/privacy")
        if not click.confirm('Do you accept the Terms of Service and Privacy Policy?'):
            raise Exception("Sorry, you must accept the Terms of Service and Privacy Policy to continue.")

    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": card_exp_month,
            "exp_year": card_exp_year,
            "cvc": card_cvc,
        },
    )
    r = requests.post('%s/api/users' % host, headers = {
        'Content-Type': 'application/json',
    }, json = {
        'email': email,
        'password': password,
        'stripe_token': token["id"],
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def change_password(host, email, current_password, new_password):
    r = requests.patch('%s/api/users' % host, auth = (email, current_password), json = {
        "new_password": new_password
    })
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def logout():
    netrc.clear_netrc()

def login(host, email, password, yes):
    r = requests.get('%s/api/login' % host, auth = (email, password))
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        key = json.loads(r.text)["data"]["key"]
        if yes or click.confirm('Would you like to save your api key to your ~/.netrc file?', default=True):
            netrc.update_netrc(email, key)
        else:
            logging.getLogger("gigalixir-cli").info('Your api key is %s' % key)
            logging.getLogger("gigalixir-cli").warn('Many GIGALIXIR CLI commands may not work unless you your ~/.netrc file contains your GIGALIXIR credentials.')

def get_reset_password_token(host, email):
    r = requests.put('%s/api/users/reset_password' % host, json = {"email": email})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        logging.getLogger("gigalixir-cli").info("Reset password token has been sent to your email.")

def reset_password(host, token, password):
    r = requests.post('%s/api/users/reset_password' % host, json = {"token": token, "password": password})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)

def get_confirmation_token(host, email):
    r = requests.put('%s/api/users/reconfirm_email' % host, json = {"email": email})
    if r.status_code != 200:
        if r.status_code == 401:
            raise auth.AuthException()
        raise Exception(r.text)
    else:
        logging.getLogger("gigalixir-cli").info("Confirmation token has been sent to your email.")