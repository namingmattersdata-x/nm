import requests
def reach_nytimes(query=""):
# have to query multiple times because we need to offset each query in order to 'paginate'
# through results
	headers = {
			    "content-type" : "application/json",
			    "api-key" : "16d605322e6447bdac4dbf89c7625e96",
			    "User-agent" : "Mozilla/5.0"
			}
	def query_nytimes(query = "", offset=0):
		data = {
		    "query" : query,
		    "offset" : str(offset),
		    "fields": "article_list"
		}
		response = requests.get(
		    url="https://api.nytimes.com/svc/semantic/v2/concept/search.json",
		    headers=headers,
		    params=data
		).json()
		# print(response)
		return [{"name": each["concept_name"], "vernacular":each["vernacular"], \
					"date_created":each["concept_created"], "urls":[r["url"] for r in each["article_list"]["results"]]} \
					for each in response["results"] if each["concept_type"] in ["nytd_porg","nytd_org"]], \
				response["num_results"]
	try:
		companies, num = query_nytimes(query)
	except Exception as e:
		companies, num = None, 0
		print("Error at nytimes:\n{}".format(e))

	if num > 20:
		for i in range(num//20):
			# decide better limiter later
			if len(companies) >= 100:
				break
			else:
				try:
					companies.extend(query_nytimes(query,20*(i+1))[0])
				except Exception as e:
					print("Error at nytimes:\n{}".format(e))
	return companies

query_term = "resolute"
from pprint import PrettyPrinter
import bs4 as bs
companies = reach_nytimes(query_term)
headers = {"User-agent" : "Mozilla/5.0"}
for company in companies:
	company['context'] = []
	for url in company["urls"]:
		source = requests.get(url, headers)
		soup = bs.BeautifulSoup(source.content, "html.parser")
		context = [(each.text,(1 if company["vernacular"].lower() in each.text.lower() else 0)) \
						 for each in soup.find_all("p") if query_term in each.text.lower()]
		company['context'].extend(context)

PrettyPrinter().pprint(companies)