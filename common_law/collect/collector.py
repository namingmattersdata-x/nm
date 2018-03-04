from common_law.cleaners.company_name import CompanyName
import requests
import bs4 as bs

class Collector():
	def __init__ (self):
		self.sources = []
		self.func_map = {"nytimes":self.reach_nytimes,
						"thomas":self.reach_thomas,
						"opencorp":self.reach_opencorp}
		self.raw = {}
		self.processed = {}
		self.blocking_key = {"location": (lambda x: x),
								"name": (lambda x: [e['name'] for e in x]),
								"date_created": (lambda x: x),
								"type": (lambda x: x)}

	def as_dict(self):
		return self.processed

	def collect(self, sources = "all", term = ""):
		if sources == "all":
			self.sources = ['nytimes','thomas','opencorp']
		else:
			self.sources = [source for source in sources if source in ['nytimes','thomas','opencorp']]
		self.raw = {source:self.func_map[source](term) for source in self.sources}
		return self

	def reach_nytimes(self, query=""):
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
			    "offset" : str(offset)
			}
			response = requests.get(
			    url="https://api.nytimes.com/svc/semantic/v2/concept/search.json",
			    headers=headers,
			    params=data
			).json()
			return [{"name":CompanyName(each["concept_name"]).pre_process().as_dict(), \
						"date_created":each["concept_created"]} \
						for each in response["results"] if each["concept_type"] in ["nytd_porg","nytd_org"]], \
					response["num_results"]
		try:
			companies, num = query_nytimes(query)
		except Exception as e:
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

	def reach_opencorp(self, query=""):
		# this source kinda sucks
		headers = {
		    "content-type" : "application/json",
		}
		data = {
		    "q": query,
		}
		response = requests.get(
		    url="https://api.opencorporates.com/companies/search",
		    headers=headers,
		    params=data
		)
		def lower_if_string(x):
			return(x.lower()) if x else x
		try:
			companies = [{"name":CompanyName(company['company']['name']).pre_process().as_dict(), \
							"location":lower_if_string(company['company']['registered_address_in_full']),\
							"date_created":lower_if_string(company['company']['retrieved_at'])}\
							for company in response.json()['results']['companies']]
			return companies
		except Exception as e:
			print("Error at opencorp:\n{}".format(e))
			return None

		return

	def reach_thomas(self, query=""):
		# this source provides name, location, and "type" (ie distributor, manufacturer, etc).
		# could potentially be second-level scraped for more info, but would take a lot more time.
		headers = {
		    "User-agent" : "Mozilla/5.0"
		}
		profiles = []
		i = 1
		while True:		
			try : 	
				url = "https://www.thomasnet.com/compsearch.html?what={}&cov=NA&which=comp&pg={}".format(query,i)
				source = requests.get(url, headers = headers)
				soup = bs.BeautifulSoup(source.content, "html.parser")
				tmp = soup.find_all(class_ = "profile-card__title")
				if not tmp or i > 10:
					break
				else:
					inds = soup.find_all(class_ = "profile-card__subheader")
					processed = ([{"name":CompanyName(each.text.split('-')[0].strip()).pre_process().as_dict(),	
									"location":each.text.split('-')[1].strip().lower()} for each in tmp])
					# if there is a mismatch between # names and # types, ignore the type (for now)
					for i, pro in enumerate(processed):
						pro["type"] = inds[i].text[:-1].lower() if len(tmp) == len(inds) else None
					profiles.extend(processed)
			except Exception as e:
				print("Error at thomas.net:\n{}".format(e))
			i += 1
		return profiles

	def consolidate(self):
		def merge(processed,new):
			for key, value in new.items():
				if value:
					if key + 's' in processed and self.blocking_key[key]([value])[0] not in self.blocking_key[key](processed[key + 's']):
						processed[key + 's'].append(value)
					else:
						processed[key + 's'] = [value]
			return processed

		for source, profiles in self.raw.items():
			for profile in profiles:
				if profile['name']['clean'] in self.processed:
					self.processed[profile['name']['clean']] = merge(self.processed[profile['name']['clean']], profile)
					self.processed[profile['name']['clean']]['sources'].add(source)
				else:
					self.processed[profile['name']['clean']] = {key + 's':list(filter(None,[value])) for key,value in profile.items()}
					self.processed[profile['name']['clean']]['sources'] = set([source])
		return self


# from pprint import PrettyPrinter
# PrettyPrinter().pprint(Collector().collect("all", "resolute"))