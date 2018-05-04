from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np
import pandas as pd
import os
import json
import _pickle

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

	# methods in section below not found to increase performance 
	"""
	# for col in ["num_orgs","num_non_orgs","num_found","num_titlecase","num_industries"]:
	# 	full[col]= (full[col] / full["num_articles"]) 

	# full = full.fillna(0)

	# cols = full.columns.tolist()
	# cols.remove("class")
	# full = full[cols + ["class",]]
	"""

	X = full.iloc[:,2:-1]
	y = full.iloc[:,-1]

	X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=.2, random_state=131)

	random_forest = RandomForestClassifier(n_estimators=1000)
	random_forest.fit(X,y)
	# random_forest.fit(X_train, y_train)

	# below for tuning analysis etc
	# """
	# p = np.array([e[1] for e in random_forest.predict_proba(X_test)])
	# classes = np.greater_equal(p,.45).astype(int)
	# print(metrics.confusion_matrix(y_test, classes))
	# """
	return random_forest

def dump(rf):
	with open('rf.pkl', 'wb') as outfile:
		_pickle.dump(rf, outfile)

if __name__ == '__main__':
	m = model()
	# dump(m)



