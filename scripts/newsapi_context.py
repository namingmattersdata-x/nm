from newsapi import NewsApiClient
import requests
import bs4 as bs

query_term =  "resolute forest products"
newsapi = NewsApiClient(api_key='25d399904da54cc3a0cec6eafbe8717b')
all_articles = newsapi.get_everything(q=query_term,
                                      #sources='bbc-news,the-verge',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      # from_parameter='2012-12-01',
                                      # to='2018-03-09',
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)

from pprint import PrettyPrinter
# for article in all_articles
# PrettyPrinter().pprint(all_articles)

def prune_context(content=""):
	if len(content) <= 500 + len(query_term):
		if len(content) <= 20 + len(query_term):
			return None
		return content
	else:
		return content[max(content.find(query_term) - 250, 0):content.find(query_term) + 250]
company = {"name":query_term, "context":[]}
#limiting to 10 for testing reasons... pretty slow :(
headers = {"User-agent" : "Mozilla/5.0"}
for article in all_articles["articles"][:10]:
	url = article["url"]
	source = requests.get(url, headers)
	soup = bs.BeautifulSoup(source.content, "html.parser")
	context = [(prune_context(each.text.lower()),(1 if company["name"].lower() in each.text.lower() else 0)) \
					 for each in soup.find_all("p") if query_term in each.text.lower()]
	company['context'].extend(context)
PrettyPrinter().pprint(company)
