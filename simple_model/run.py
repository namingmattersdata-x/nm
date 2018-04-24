from simple_model.tools.gather import Gatherer
import pandas as pd
import numpy as np
import json
import os
from sys import argv
import _pickle

def run_logistic(processed):	
	with open('simple_model/models/logistic_coefficients.json', 'r') as infile:
		data = json.load(infile)

	coefficients = np.array(data["coefficients"])
	means = np.array(data["means"])
	sds = np.array(data["sds"])

	keys = ['ratio_orgs', 'newsapi_totalResults', 'root_mean_distance', 'num_orgs', 'num_non_orgs', 
			'num_titlecase', 'num_articles', 'org_at_least_once', 'num_found', 'num_industries', 
			'ratio_case', 'newsapi_rawResults','avg_article_length']

	observation = [1, ]
	for key in keys:
		observation.append(processed.features[key])

	row = pd.DataFrame([observation,], columns = ['intercept'] + keys)
	row["ratio_results"] = 0 if row["newsapi_rawResults"][0] == 0 else \
								row["newsapi_totalResults"][0] / row["newsapi_rawResults"][0]

	# empty = False
	# if row["newsapi_totalResults"][0] == 0:
	# 	empty = True

	# normalize
	row.iloc[0,1:] = (row.iloc[0,1:] - means) / sds

	lincomb = row.values.dot(coefficients.T)
	sigmoid = np.exp(lincomb)
	p = (sigmoid/(1+sigmoid))[0]

	# if empty:
	# 	p = 0

	return(p)


def cache_top(model, processed=None):
	if processed:
		df = pd.DataFrame({"source":["nytimes"],"preview":["this is your COMPANY in context"],"date published":["April 20, 1997"],"risk score":["87%"]})
		df.to_csv("./cache/{}/{}.{}.csv".format(model, "_".join(processed.entity.split()), "-".join(["_".join(i.split()) for i in processed.industries])), index = False)

def run_rf(processed):
	with open('simple_model/models/rf.pkl', 'rb') as infile:
		rf = _pickle.load(infile)

	keys = ['ratio_orgs', 'newsapi_totalResults', 'root_mean_distance', 'num_orgs', 'num_non_orgs', 
			'num_titlecase', 'num_articles', 'org_at_least_once', 'num_found', 'num_industries', 
			'ratio_case', 'newsapi_rawResults','avg_article_length']

	observation = [ ]
	for key in keys:
		observation.append(processed.features[key])

	row = pd.DataFrame([observation,], columns = keys)
	row["ratio_results"] = 0 if row["newsapi_rawResults"][0] == 0 else \
								row["newsapi_totalResults"][0] / row["newsapi_rawResults"][0]

	if row["newsapi_rawResults"][0] == 0:
		return 0

	return rf.predict_proba(row)[0][1]

if __name__ == "__main__":
	
	model = "random_forest"

	company = argv[1]
	industries = argv[2]
	processed = Gatherer(company, industries).gather()
	cache_top(model, processed)
	model_funcs = {"logistic":run_logistic,"random_forest":run_rf}
	probability = model_funcs[model](processed)
	ascend = {.2:"Low Risk", .4:"Medium-Low Risk", .6:"Medium Risk",
				.8:"Medium-High Risk", 1.0:"High Risk"}
	base = .2
	while probability > base:
		base += .2
	class_ = ascend[base]

	print("PROBABILITY: {}\nCLASS: {}".format(probability,class_))









