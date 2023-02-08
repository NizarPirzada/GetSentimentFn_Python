import logging

import azure.functions as func
import json
import flair
from flair.models import TextClassifier
from flair.data import Sentence
from flair.models import SequenceTagger
flair_sentiment = TextClassifier.load('en-sentiment')
tagger = SequenceTagger.load('ner-ontonotes-large')

def GetSentimentFromText(text):
    sentiment = {}
    try:
        sentence=flair.data.Sentence(text)
        flair_sentiment.predict(sentence)
        total_sentiment = sentence.labels
        label = total_sentiment[0].value
        score = total_sentiment[0].score
        score1 = 1 - total_sentiment[0].score
        label1 = "POSITIVE"
        if label == "POSITIVE":
            label1 = "NEGATIVE"
        sentiment[label] = score
        sentiment[label1] = score1
    except:
        pass
    return sentiment
    
def GetNERFromText(text):
    
    NERs = []
    try:
        # make a sentence
        sentence = Sentence(text)

        # run NER over sentence
        tagger.predict(sentence)

        # iterate over entities and print
        for entity in sentence.get_spans('ner'):
            NER = {}
            ner_dict = entity.to_dict()
            NER["token"] = ner_dict["text"]
            NER["tag"] = ner_dict["labels"][0].value
            NERs.append(NER)
    except:
        pass
    return NERs



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    articles = req.params.get('articles')
    if not articles:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            articles = req_body.get('articles')

    if articles:
        results = []
        for article in articles:
            result = {}
            sentiment = GetSentimentFromText(article)
            NERs = GetNERFromText(article)
            result["sentiment"] = sentiment
            result["NER"] = NERs
            results.append(result)
        data = {"Sentiments": results}
        return func.HttpResponse(json.dumps(data, indent=4, sort_keys=True, default=str),status_code=200)     
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
