from flask import redirect, request, url_for, render_template, session
from requests_oauthlib import OAuth2Session
from flask.views import MethodView
import dbmodel
from oauth_config import client_id, authorization_base_url, redirect_callback
from google.cloud import storage
import base64
import os
from dotenv import load_dotenv
import tempfile
from ai import AI
from datetime import datetime


class Poof(MethodView):
    def __init__(self) -> None:
        load_dotenv()
        super().__init__()
        self.ai = AI()
        self.dbmodel = dbmodel.get_model()
        self.submit_quota = 10

    def get(self):
        # If client has an OAuth2 token, use it to get their information and render
        #   the signing page with it
        if 'oauth_token' in session:
            google = OAuth2Session(client_id, token=session['oauth_token'])
            userinfo = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

            entries = self.dbmodel.select_with_date(email=userinfo['email'],date=datetime.today().strftime('%Y-%m-%d'))
            quota = f"Daily limit {len(entries)}/{self.submit_quota}"

            return render_template('poof.html', name=userinfo['name'], email=userinfo['email'], picture=userinfo['picture'], daily_quota=quota)
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
            session['redirect_after_auth'] = url_for('poof')
            return redirect(authorization_url)
    
    def gcs_upload_image(self, data):
        png = base64.b64decode(data)  

        temp_dir = tempfile.TemporaryDirectory()

        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir.name, delete=False)
        temp_file.write(png)
        temp_file.close()

        # client = storage.Client.from_service_account_json(os.path.abspath('credentials.json'))
        client = storage.Client()
        bucket = client.get_bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(os.path.basename(temp_file.name))        
        with open(temp_file.name, 'rb') as my_file:
            blob.upload_from_file(my_file)
        
        temp_dir.cleanup()       
        return f"https://storage.googleapis.com/{os.getenv('BUCKET_NAME')}/{os.path.basename(temp_file.name)}"

    def post(self):
        """
        Accepts POST requests, and processes the form;
        Redirect to index when completed.
        """
        if 'oauth_token' in session:
            google = OAuth2Session(client_id, token=session['oauth_token'])
            userinfo = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

            entries = self.dbmodel.select_with_date(email=userinfo['email'],date=datetime.today().strftime('%Y-%m-%d'))
            quota = f"Daily limit {len(entries)}/{self.submit_quota}"
            if len(entries) >= self.submit_quota:
                return redirect(url_for('poof'))
            
            if request.form['submit'] == 'ai':
                idea = self.ai.idea_generator()
                return render_template('poof.html',generated=idea, name=userinfo['name'],
                                        email=userinfo['email'], picture=userinfo['picture'],enable_button=True, daily_quota=quota)
            
            else:
                # Insert based on form fields only if an OAuth2 token is present to ensure
                #   values in all fields exist
                query = request.form.get('query')[:1000]
                pun = self.ai.pun_generator(query)

                b64 = self.ai.img_generator(query)[self.ai.provider]['items'][0]['image']

                entries=[{'query':query,
                        'pun': pun,
                        'image':b64}]
                
                image_url = self.gcs_upload_image(b64)
                
                self.dbmodel.insert(name=userinfo['name'],email=userinfo['email'],profile=userinfo['picture'],query=query,pun=pun,image=image_url)
            
                return render_template('creation.html', entries=entries)
        else:
            # Redirect to the identity provider and ask the identity provider to return the client
            # back to /callback route with the code
            google = OAuth2Session(client_id,
                    redirect_uri = redirect_callback,
                    scope = 'https://www.googleapis.com/auth/userinfo.email ' +                   
                            'https://www.googleapis.com/auth/userinfo.profile'
            )
            authorization_url, state = google.authorization_url(authorization_base_url, prompt='login')

            # Identity provider returns URL and random "state" that must be echoed later
            #   to prevent CSRF.
            session['oauth_state'] = state
            session['redire_after_auth'] = url_for('poof')
            return redirect(authorization_url)
