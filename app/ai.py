from tenacity import retry, stop_after_attempt, wait_random_exponential
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel, TextEmbeddingInput
import pickle
import numpy as np
from dotenv import load_dotenv
import vertexai
import os
import json
import requests
load_dotenv()
vertexai.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'),location=os.getenv('GOOGLE_CLOUD_LOCATION'))

class AI:
    def __init__(self) -> None:
        with open('puns.dict','rb') as f:
            self.puns_dict = pickle.load(f)

        self.provider = 'openai'

        self.generation_model = TextGenerationModel.from_pretrained("text-bison@001")
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko-multilingual@001")

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def text_generation_model_with_backoff(self,**kwargs):
        return self.generation_model.predict(**kwargs).text


    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def embedding_model_with_backoff(self,text:list):
        text_embedding_input = TextEmbeddingInput(
            task_type='SEMANTIC_SIMILARITY', title='', text=text)
        embeddings = self.embedding_model.get_embeddings(text_embedding_input)
        return embeddings

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def embedding_model_with_backoff_single(self,text:str):
        text_embedding_input = TextEmbeddingInput(
            task_type='SEMANTIC_SIMILARITY', title='', text=text)
        embeddings = self.embedding_model.get_embeddings([text_embedding_input])
        return embeddings
    
    def idea_generator(self):
        return self.text_generation_model_with_backoff(
            prompt='''Tell me a very short creative idea involves a nonfictional or fictional entity and a scenary. Do not explain''', temperature=0.99, top_p=0.99)
    

    def pun_generator(self, query:str):
        emb_query = (query, self.embedding_model_with_backoff_single(query)[0].values)
        # print(emb_query)
        srt_cp = []
        for k,v in self.puns_dict.items():
            srt_cp += [(k, sum(np.array(v['embeddings'])*np.array(emb_query[1])))]
        srt_cp = sorted(srt_cp, key=lambda x:x[1])
        # print(srt_cp)
        context = self.puns_dict[srt_cp[0][0]]['context']

        prompt = f""" From examples puns, write 3 new humorous creative pun.
  The new puns could only mention a part of the query, the essence is humor and the punchline.  \n\n
  Then from the 3 puns, choose the most humorous one.
              Context: \n {context} \n
              Query: \n {query} \n
              Pun 1:
              Pun 2:
              Pun 3:
              Answer: (just 1 of 3 puns)
            """

        # Call the PaLM API on the prompt.
        return self.text_generation_model_with_backoff(prompt=prompt, temperature=0.9, top_p=0.8)
    
    # @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def img_generator(self, query):
        img_kg = os.getenv('IMG_API')
        headers = {"Authorization": "Bearer " + img_kg}

        url = "https://api.edenai.run/v2/image/generation"
        payload = {
            "providers": self.provider,
            "text": query,
            "resolution": "1024x1024",
            "fallback_providers": "replicate"
        }

        response = requests.post(url, json=payload, headers=headers)
        return json.loads(response.text)


