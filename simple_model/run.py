from simple_model.tools.gather import Gatherer
import pandas as pd
import numpy as np
import json
import os

model = 'logistic'

with open('simple_model/models/{}_coefficients.json'.format(model), 'r') as infile:
	data = json.load(infile)

coefficients = np.array(data["coefficients"])
means = np.array(data["means"])
sds = np.array(data["sds"])

company = input("input desired company name... ")
industries = input("input desired industries separated by a comma (,)... ")

process = Gatherer(company, industries).gather()

keys = ['ratio_orgs', 'newsapi_totalResults', 'root_mean_distance', 'num_orgs', 'num_non_orgs', 
		'num_titlecase', 'num_articles', 'org_at_least_once', 'num_found', 'num_industries', 
		'ratio_case', 'newsapi_rawResults','avg_article_length']

observation = [1, ]
for key in keys:
	observation.append(process.features[key])

row = pd.DataFrame([observation,], columns = ['intercept'] + keys)
row["ratio_results"] = 0 if row["newsapi_rawResults"][0] == 0 else \
							row["newsapi_totalResults"][0] / row["newsapi_rawResults"][0]

# normalize
row.iloc[0,1:] = (row.iloc[0,1:] - means) / sds

lincomb = row.values.dot(coefficients.T)
sigmoid = np.exp(lincomb)
p = (sigmoid/(1+sigmoid))[0]
print(p)

