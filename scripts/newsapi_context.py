from newsapi import NewsApiClient
import requests
import bs4 as bs
from bs4.element import Comment
import json
import re

name =  "resolute"
subject = "software,information technology"
# query_term ='"' + name + '"'
query_term = '"' + name + '" AND (' + " OR ".join(['"' + s.strip() + '"' for s in subject.split(',')]) + ")"

newsapi = NewsApiClient(api_key='25d399904da54cc3a0cec6eafbe8717b')
all_articles = newsapi.get_everything(q=query_term,
                                      #sources='bbc-news,the-verge',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      # from_parameter='2012-12-01',
                                      # to='2018-03-09',
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)

print([a['url'] for a in all_articles['articles']])

# def tag_visible(element):
#     if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
#         return False
#     if isinstance(element, Comment):
#         return False
#     return True


# def text_from_html(body):
#     soup = bs.BeautifulSoup(body, 'html.parser')
#     texts = soup.findAll(text=True)
#     visible_texts = filter(tag_visible, texts)  
#     return u" ".join(t.strip() for t in visible_texts)


# from pprint import PrettyPrinter
# # PrettyPrinter().pprint(all_articles)

# def prune_context(content=""):
# 	if len(content) <= 500 + len(query_term):
# 		if len(content) <= 20 + len(query_term):
# 			return None
# 		return content
# 	else:
# 		return content[max(content.find(query_term) - 250, 0):content.find(query_term) + 250]
# company = {"name":name, "query":query_term, "context":[]}
#limiting to 10 for testing reasons... pretty slow :(
# headers = {"User-agent" : "Mozilla/5.0"}
# for article in all_articles["articles"][:1]:
# 	url = article["url"]
# 	source = requests.get(url, headers)
# 	# soup = bs.BeautifulSoup(source.content, "html.parser")
# 	# context = [(prune_context(each.text),(1 if company["name"].lower() in each.text.lower() else 0)) \
# 	# 				 for each in soup.find_all("p") if name in each.text.lower()]
# 	# company['context'].extend(filter(lambda x:x[0] is not None, context))
# 	text = text_from_html(source.content).encode('utf-8',"ignore")

# # PrettyPrinter().pprint(company)
# # with open('resolute_forestry_context.json', 'w') as outfile:
# # 	json.dump(company['context'],outfile)

# # pattern = ["[" + e[0] + e[0].upper "]" name.split()]

# indices = [m.start() for m in re.finditer(name, str(text).lower())]
# for index in indices:
# 	print(text[max(index - 250, 0):index + 250])
