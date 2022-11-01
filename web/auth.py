import functools
import json
import urllib.request
from urllib.error import URLError, HTTPError

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from web.config import API_ROUTES
from web.service.connection import call_api

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if not error:
            data = {'name': username, 'password': generate_password_hash(password)}
            response = call_api(route='register', post_data=data, next='auth.login')

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        error = None
        password = request.form['password']
        try:
            data = {
                'name': request.form['username'],
                'password': generate_password_hash(password)
            }
            json_dict = call_api(route='login', post_data=data)
            user = json_dict['user']
            if not user:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'
        except HTTPError as exc:
            error = f"HTTP Error {exc} happens."
        except URLError as exc:
            error = f"Exception {exc} happens."
        else:
            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        data = {}
        g.user = urllib.request.urlopen(g.API_ROUTES['login'], data=bytes(data))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
