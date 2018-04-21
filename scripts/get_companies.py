import pandas as pd 
import random
import json

csv = 'negative_companies.csv'
df = pd.read_csv(csv)
zipped = list(zip([str(e).lower() for e in df["Organization Name"]],
	[",".join([f.strip() for f in str(e).lower().split(',')][:random.randint(1,len(str(e).split(',')))])\
	 for e in df["Categories"]]))

with open('negative_companies_processed.json','w') as out:
	json.dump(zipped,out)
