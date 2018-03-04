import requests
import bs4 as bs

class Collector():
	def __init__ (self):
		self.sources = []
		self.func_map = {"nytimes":self.reach_nytimes,
						"thomas":self.reach_thomas,
						"opencorp":self.reach_opencorp}

	def collect(self, sources = "all", term = ""):
		if sources == "all":
			self.sources = ['nytimes','thomas','opencorp']
		else:
			self.sources = [source for source in sources if source in ['nytimes','thomas','opencorp']]
		self.raw = {source:self.func_map[source](term) for source in self.sources}
		return(self.raw)

	def reach_nytimes(self, query=""):
		pass
	def reach_opencorp(self, query=""):
		pass
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
					processed = ([{"name":each.text.split('-')[0].strip(),	
								"location":each.text.split('-')[1].strip()} for each in tmp])
					# if there is a mismatch between # names and # types, ignore the type (for now)
					for i, pro in enumerate(processed):
						pro["type"] = inds[i].text[:-1] if len(tmp) == len(inds) else None
					profiles.extend(processed)
			except Exception as e:
				print("Error at thomas.net:\n{}".format(e))
			i += 1
		return profiles

print(Collector().collect("all", "resolute"))