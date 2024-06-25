from flask import redirect, request, url_for, render_template, session
from requests_oauthlib import OAuth2Session
from oauth_config import client_id, authorization_base_url, redirect_callback
from flask.views import MethodView
import dbmodel
from google.cloud import storage
import os
from dotenv import load_dotenv
import base64


class View(MethodView):
    def __init__(self) -> None:
        super().__init__()
        load_dotenv()


    def gcp_load_img(self, url):
        # client = storage.Client.from_service_account_json(os.path.abspath('credentials.json'))
        client = storage.Client()
        bucket = client.get_bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.get_blob(url.split('/')[-1])

        return base64.b64encode(blob.download_as_bytes()).decode()


    def get(self):
        # If client has an OAuth2 token, use it to get their information and render
        #   the signing page with it
        if 'oauth_token' in session:
            google = OAuth2Session(client_id, token=session['oauth_token'])
            userinfo = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        
            model = dbmodel.get_model()

            if 'dbcursor' not in session:
                session['dbcursor'] = None

            nxt_cursor, entries = model.select_with_cursor(email=userinfo['email'], cursor=session['dbcursor'])
            session['dbcursor'] = nxt_cursor
            for idx,entry in enumerate(entries):
                entries[idx]['image'] = self.gcp_load_img(entry['image'])
            return render_template('view.html', entries=entries, name=userinfo['name'], email=userinfo['email'], picture=userinfo['picture'])
    
        else:
        # Redirect to the identity provider and ask the identity provider to return the client
        #   back to /callback route with the code
            google = OAuth2Session(client_id,
                    redirect_uri = redirect_callback,
                    scope = 'https://www.googleapis.com/auth/userinfo.email ' +                   
                            'https://www.googleapis.com/auth/userinfo.profile'
            )
            authorization_url, state = google.authorization_url(authorization_base_url, prompt='login')

            # Identity provider returns URL and random "state" that must be echoed later
            #   to prevent CSRF.
            session['oauth_state'] = state
            session['redirect_after_auth'] = url_for('view')
            return redirect(authorization_url)
        

    def post(self):
        # If client has an OAuth2 token, use it to get their information and render
        #   the signing page with it
        if 'oauth_token' in session:
            return url_for(url_for('view'))
        else:
        # Redirect to the identity provider and ask the identity provider to return the client
        #   back to /callback route with the code
            google = OAuth2Session(client_id,
                    redirect_uri = redirect_callback,
                    scope = 'https://www.googleapis.com/auth/userinfo.email ' +                   
                            'https://www.googleapis.com/auth/userinfo.profile'
            )
            authorization_url, state = google.authorization_url(authorization_base_url, prompt='login')

            # Identity provider returns URL and random "state" that must be echoed later
            #   to prevent CSRF.
            session['oauth_state'] = state
            session['redirect_after_auth'] = url_for('view')
            return redirect(authorization_url)
