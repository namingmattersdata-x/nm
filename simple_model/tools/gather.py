from sner import Ner
import json
from newsapi import NewsApiClient
import requests
import bs4 as bs
from bs4.element import Comment
import re
from collections import defaultdict

# have to have the ner server running locally...
tagger = Ner(host='localhost',port=9199)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = bs.BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    # encode to get rid of encoding errors (hopefully)
    return " ".join(t.strip() for t in visible_texts).encode('utf-8','ignore')

class Gatherer():
	def __init__(self, entity, industries):
		self.entity = entity.lower()
		self.industries = [i.strip().lower() for i in industries.split(',')]
		self.query = ""
		self.features = defaultdict(float)
		self.contexts = []
		self.articles = []

	def gather(self, sources=["newsapi"]):
		if "newsapi" in sources:
			self.reach_news_api()
		return self

	def reach_news_api(self):
		self.query = '"' + self.entity + '" AND (' + " OR ".join(['"' + e + '"' for e in self.industries]) + ")"
		newsapi = NewsApiClient(api_key='25d399904da54cc3a0cec6eafbe8717b')
		all_articles = newsapi.get_everything(q=self.query,
		                                      language='en', # necessary to only maintain english? probably for now
		                                      sort_by='relevancy',
		                                      page=1)
		# if 'totalResults' not in all_articles:
		# 	return self
		self.features["newsapi_totalResults"] = all_articles["totalResults"]
		self.features["newsapi_rawResults"] = newsapi.get_everything(q='"' + self.entity + '"',
                                      language='en', 
                                      sort_by='relevancy',
                                      page=1)["totalResults"]
		headers = {"User-agent" : "Mozilla/5.0"}
		self.contexts = []
		for article in all_articles["articles"]:
			url = article["url"]
			try: 
				# TODO: pass if response is bad (403 etc)
				source = requests.get(url, headers)
				if source.status_code != 200:
					continue
				# decode to bring back to string (lol)
				text = text_from_html(source.content).decode('utf-8')
				# pattern = " ".join(["[" + e[0] + e[0].upper() + "]" + e[1:] for e in self.entity.split()])
				# indices = [m.start() for m in re.finditer(pattern, str(text))]
				indices = [m.start() for m in re.finditer(self.entity, text.lower())] # this way was faster with limited testing
				# this is just to keep some contexts for NN training
				if not indices: # ignore if entity never found in article (means something probly wrong)
					continue
				orgs = 0
				nonorgs = 0
				count = 0
				for index in indices:
					current = text[max(index - 250, 0):index + 250]
					if count < 20: #limit to 20 contexts per article for now
						self.contexts.append(current)
					ner = tagger.get_entities(current)
					entity_split = self.entity.split()
					for i in range(len(ner)):
						if ner[i][0].lower() == entity_split[0]:
							if " ".join([e[0].lower() for e in ner[i:i+len(entity_split)]]) == self.entity:
								if [e for e in ner[i:i+len(entity_split)] if e[1] == "ORGANIZATION"]: # if any of the terms in the name are rec as org
									orgs += 1
								else:
									nonorgs += 1
								i += len(entity_split)
							else:
								i += 1
						else:
							i += 1

						if i >= len(ner):
							break	
					count += 1
				industry_indices = [m.start() for m in re.finditer("(" + "|".join(self.industries) + ")", text.lower())]
				if not industry_indices:
					industry_indices = [0,]
				square_sum = 0
				for industry_index in industry_indices:
					for name_index in indices:
						square_sum += (name_index-industry_index)**2
				root_mean = (square_sum / (len(industry_indices)*len(indices))) ** .5
				self.features["root_mean_distance"] += root_mean
				self.features["num_industries"] += len(industry_indices)
				self.features["org_at_least_once"] += 1 if orgs >= 1 else 0
				self.features["num_orgs"] += orgs
				self.features["num_non_orgs"] += nonorgs
				self.features["ratio_orgs"] += float(orgs) / nonorgs if nonorgs != 0 else 0
				num_found = len(indices)
				num_titlecase = len(list(re.finditer(self.entity.title(), text)))
				self.features["num_found"] += num_found
				self.features["num_titlecase"] += num_titlecase
				self.features["ratio_case"] += float(num_titlecase) / num_found if num_found != 0 else 0
				self.features["avg_article_length"] +=  len(text)
				self.features["num_articles"] += 1
				score = 2*((orgs/(orgs+nonorgs)) if orgs+nonorgs != 0 else 0) \
								+ (float(num_titlecase) / num_found if num_found != 0 else 0)
				self.articles.append({"source":article["source"]["name"],"preview":url,
										"date published":article["publishedAt"],"risk score":score})

			except Exception as e:
				# print("Error at url (newsapi):\n{}\n{}".format(url,e))
				pass
		if not self.features["num_articles"]: 
			return self
		self.features["avg_article_length"] /= self.features["num_articles"]
		self.features["root_mean_distance"] /= self.features["num_articles"]
		self.features["ratio_case"] /= self.features["num_articles"]
		self.features["ratio_orgs"] /= self.features["num_articles"]
		return self

