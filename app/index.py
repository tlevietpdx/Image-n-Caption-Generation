from flask import render_template
from flask.views import MethodView
from flask import redirect, request, url_for, render_template, session
from requests_oauthlib import OAuth2Session
from flask.views import MethodView
from oauth_config import client_id, authorization_base_url, redirect_callback
        
import dbmodel


class Index(MethodView):
    def get(self):
        # model = dbmodel.get_model()
        # entries = [dict(name=row[0], email=row[1], signed_on=row[2], message=row[3], picture=row[4]) for row in model.select()]
        # return render_template('index.html',entries=entries)
        return render_template('index.html')