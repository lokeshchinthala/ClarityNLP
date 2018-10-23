from tasks.task_utilities import BaseTask
from pymongo import MongoClient
import requests
import util


class SentimentAPITask(BaseTask):
    task_name = "AzureSentiment"

    # NLPQL

    # define sampleTask:
    # Clarity.AzureSentiment({
    #   documentset: [ProviderNotes],
    #   "api_key": "{your_api_key}"
    # });

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        for doc in self.docs:

            sentence_list = self.get_document_sentences(doc)

            for sentence in sentence_list:
                headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': self.pipeline_config.custom_arguments['api_key']}
                self.write_log_data("INFO", self.pipeline_config.custom_arguments['api_key'])

                payload = {"documents": [{"language": "en", "id": "1", "text": sentence}]}
                response = requests.post('https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', headers=headers, json=payload)
                if response.status_code == 200:
                    json_response = response.json()
                    val = json_response['documents'][0]
                    obj = {
                        'sentiment_score': val['score'],
                        'sentence': sentence
                    }

                    # writing results
                    self.write_result_data(temp_file, mongo_client, doc, obj)

                else:
                    # writing to log (optional)
                    self.write_log_data("OOPS", "No sentiment this time!")
