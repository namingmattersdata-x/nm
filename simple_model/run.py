from simple_model.tools.gather import Gatherer
import pandas as pd
import numpy as np
import json
import os
import re
from sys import argv
import _pickle
from string import punctuation

def run_logistic(processed):	
	''' Calculates predicted probability of positive classification using a logistic regression model'''
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

	###
	for col in ["num_orgs","num_non_orgs","num_found","num_titlecase","num_industries"]:
		row[col+"_avg"]= (row[col] / row["num_articles"]) 

	row = row.fillna(0)
	###

	# normalize
	row.iloc[0,1:] = (row.iloc[0,1:] - means) / sds

	lincomb = row.values.dot(coefficients.T)
	sigmoid = np.exp(lincomb)
	p = (sigmoid/(1+sigmoid))[0]

	return(p)


def cache_top(model, processed=None):
	'''caches the "riskiest" webpages in ./cache'''
	if processed:
		df_dict = {"source":[],"preview":[],"date published":[],"risk score":[]}
		sort = sorted(processed.articles, key = lambda x:x["risk score"], reverse = True)
		for dic in sort:
			if dic["risk score"] >= 1:
				for key, value in dic.items():
					df_dict[key].append(value)
		df = pd.DataFrame(df_dict).iloc[:10,]
		df.to_csv("./cache/{}/{}.{}.csv".\
							format(model, "_".join("".join([l for l in processed.entity if l not in punctuation]).split()), 
								"-".join(["_".join("".join([l for l in i if l not in punctuation]).split()) for i in processed.industries])), 
							index = False)

def run_rf(processed):
	''' Calculates predicted probability of positive classification using a Random Forest model'''
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

	return rf.predict_proba(row)[0][1]

if __name__ == "__main__":
	
	model = "random_forest"

	company = argv[1]
	industries = argv[2]
	processed = Gatherer(company, industries).gather()
	cache_top(model, processed)
	model_funcs = {"logistic":run_logistic,"random_forest":run_rf}
	probability = model_funcs[model](processed)
	ascend = {.2:"Low Risk", .4:"Medium Risk", .6:"Significant Risk",
				.8:"High Risk", 1.0:"Very High Risk"}
	base = .2
	while probability > base:
		base = round(base + .2, 1)
	class_ = ascend[base]

	print("RISK SCORE: {}%\nCLASS: {}".format(round(probability*100,2), class_))









