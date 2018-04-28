from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np
import pandas as pd
import os
import json

def model():
	negative = pd.read_csv("../data/full_features_negative.csv", header=0, encoding='latin1')
	positive = pd.read_csv("../data/full_features_positive.csv", header=0, encoding='latin1')

	for df in [negative, positive]:
		df["ratio_results"] = [0 if df["newsapi_rawResults"][i] == 0 else \
								df["newsapi_totalResults"][i] / df["newsapi_rawResults"][i] \
									for i in range(df.shape[0])]

	# for practical purposes, get rid of observations that were meant to be "positive"
	# but that did not return ANY results at all (nothing found in api)
	positive = positive[positive["newsapi_rawResults"]!=0]

	negative["class"] = 0
	positive["class"] = 1

	full = negative.append(positive, ignore_index = True)

	for col in ["num_orgs","num_non_orgs","num_found","num_titlecase","num_industries"]:
		full[col+"_avg"]= (full[col] / full["num_articles"]) 

	cols = full.columns.tolist()
	cols.remove("class")
	full = full[cols + ["class",]]

	full = full.fillna(0)

	X = full.iloc[:,2:-1]
	y = full.iloc[:,-1]
	# normalize
	means = X.apply(np.mean, 0)
	sds = X.apply(np.std, 0)
	X = (X - means) / sds

	# X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=.2, random_state=131)

	logm = linear_model.LogisticRegression()
	logm.fit(X,y)
	# logm.fit(X_train,y_train)

	# print("Test Set Confusion Matrix:\n", metrics.confusion_matrix(y_test,logm.predict(X_test)))
	# full["predicted"] = [e[1] for e in logm.predict_proba(X)]
	# print(full[full["newsapi_rawResults"]==0])

	coefficients = list(logm.intercept_) + list(logm.coef_[0])
	data = {"means":list(means),"sds":list(sds),"coefficients":coefficients}
	return data

def dump(data):
	with open('logistic_coefficients.json', 'w') as out:
		json.dump(data, out)


if __name__ == '__main__':
	m = model()
	# dump(m)




