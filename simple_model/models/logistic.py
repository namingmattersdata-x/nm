from sklearn import linear_model
from sklearn import metrics
import numpy as np
import pandas as pd
import os
import json

negative = pd.read_csv("../data/full_features_negative.csv", header=0, encoding='latin1')
positive = pd.read_csv("../data/full_features_positive.csv", header=0, encoding='latin1')

for df in [negative, positive]:
	df["ratio_results"] = [0 if df["newsapi_rawResults"][i] == 0 else \
							df["newsapi_totalResults"][i] / df["newsapi_rawResults"][i] \
								for i in range(df.shape[0])]

negative["class"] = 0
positive["class"] = 1

full = negative.append(positive, ignore_index = True)

X = full.iloc[:,2:-1]
y = full.iloc[:,-1]
# normalize
means = X.apply(np.mean, 0)
sds = X.apply(np.std, 0)
X = (X - means) / sds

logm = linear_model.LogisticRegression()
logm.fit(X,y)

# print("Training Set Confusion Matrix:\n", metrics.confusion_matrix(logm.predict(X),y))

# full["predicted"] = [e[1] for e in logm.predict_proba(X)]
# print(full[full["newsapi_rawResults"]==0])

# V = X.values.dot(logm.coef_.transpose())
# print(X.values[105])
# U = V + logm.intercept_
# A = np.exp(U)
# P = A/(1+A)

coefficients = list(logm.intercept_) + list(logm.coef_[0])
with open('logistic_coefficients.json', 'w') as out:
	json.dump({"means":list(means),"sds":list(sds),"coefficients":coefficients}, out)



