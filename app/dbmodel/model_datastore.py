# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .Model import Model
from datetime import datetime
from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter
import os
from dotenv import load_dotenv


def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()
    # return [entity['name'],entity['email'],entity['profile'],entity['date'],entity['query'],entity['pun'],entity['image']]
    return dict(name=entity['name'],
            email=entity['email'],
            profile=entity['profile'],
            date=entity['date'],
            query=entity['query'],
            pun=entity['pun'],
            image=entity['image'])

class model(Model):
    def __init__(self):
        load_dotenv()
        self.client = datastore.Client(os.getenv('GOOGLE_CLOUD_PROJECT'))
        self.dbkind = 'wistive'

    def select(self, email):
        query = self.client.query(kind = self.dbkind)

        query.add_filter(filter=PropertyFilter("email", "=", email))
    
        entities = list(map(from_datastore,query.fetch(limit=5)))
        return entities
    
    def select_with_cursor(self, email, cursor=None):
        query = self.client.query(kind=self.dbkind)
        query.add_filter(filter=PropertyFilter("email", "=", email))
        query_iter = query.fetch(start_cursor=cursor, limit=5)
        page = next(query_iter.pages)

        entities = list(map(from_datastore, page))
        next_cursor = query_iter.next_page_token

        return next_cursor, entities

    def select_with_date(self, email, date=datetime.today().strftime('%Y-%m-%d')):
        query = self.client.query(kind = self.dbkind)

        query.add_filter(filter=PropertyFilter("email", "=", email))
        query.add_filter(filter=PropertyFilter("date", "=", date))
    
        entities = list(map(from_datastore,query.fetch()))
        return entities

    def insert(self,name,email,profile,query,pun,image):
        key = self.client.key(self.dbkind)
        rev = datastore.Entity(key)
        rev.update( {
            'name': name,
            'email' : email,
            'date' : datetime.today().strftime('%Y-%m-%d'),
            'profile' : profile,
            'query':query,
            'pun':pun,
            'image':image
            })
        self.client.put(rev)
        return True
