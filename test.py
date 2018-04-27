from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key='25d399904da54cc3a0cec6eafbe8717b')
all_articles = newsapi.get_everything(q="this is a test",
                                      language='en', # necessary to only maintain english? probably for now
                                      sort_by='relevancy',
                                      page=1)
from pprint import PrettyPrinter
PrettyPrinter().pprint(all_articles)