import bs4 as bs
import requests
# import json

# FULL CONTACT (BY DOMAIN) (to get more information using domain)
def full_contact(query=""):
	headers = {
	    "content-type" : "application/json",
	    "Authorization" : "Bearer 0rSBQRfFsRFdkUxHmw5ThBcvy8VtH2YN"
	}
	data = {
	    "domain": query,
	}

	response = requests.post(
	    url="https://api.fullcontact.com/v3/company.enrich",
	    headers=headers,
	    json=data
	)
	return response.json()

# NYTIMES (to find company names)

# only returns objects that CONTAIN the search query.
# ie "Frank's bike" returns "Frank's Bike Shop Manhattan", but "Frank's bikes" does NOT 

def nytimes(query = ""):
	def query_nytimes(query = "", offset=0):
		headers = {
		    "content-type" : "application/json",
		    "api-key" : "16d605322e6447bdac4dbf89c7625e96",
		    "User-agent" : "Mozilla/5.0"
		}
		data = {
		    "query" : query,
		    "offset" : str(offset)
		}
		response = requests.get(
		    url="https://api.nytimes.com/svc/semantic/v2/concept/search.json",
		    headers=headers,
		    params=data
		).json()
		return [each for each in response["results"] if each["concept_type"] in ["nytd_porg","nytd_org"]], response["num_results"]
	companies, num = query_nytimes(query)
	if num > 20:
		for i in range(num//20):
			# decide better limiter later
			if len(companies) >= 100:
				break
			else:
				companies.extend(query_nytimes(query,20*(i+1))[0])
	return companies


# from pprint import PrettyPrinter
# PrettyPrinter().pprint(nytimes('apple'))

# Thomasnet (to find company names) (other similar sites?)

def thomas_net(query=""):
	headers = {
	    "User-agent" : "Mozilla/5.0"
	}

	objs, inds = [],[]
	i = 1
	while True:
		
		url = "https://www.thomasnet.com/compsearch.html?what={}&cov=NA&which=comp&pg={}".format(query,i)
		headers = {
		    "User-agent" : "Mozilla/5.0"
		}
		source = requests.get(url, headers = headers)
		soup = bs.BeautifulSoup(source.content, "html.parser")
		tmp = soup.find_all(class_ = "profile-card__title")
		if not tmp or i > 10:
			# can change limiter later
			break
		else:
			objs.extend(tmp)
			inds.extend(soup.find_all(class_ = "profile-card__subheader"))
			i += 1

	return zip([each.text.split('-')[0].strip() for each in objs], 
				[each.text.split('-')[1].strip() for each in objs], 
				[each.text[:-1] for each in inds])


# print(list(thomas_net("resolute")))


## PeopleDataLabs (to find company names)
# Google News API (to get more information and possibly risk factor/maybe find company names)