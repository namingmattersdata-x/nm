from simple_model.tools.gather import Gatherer
# companies = [("andrew's pets care services","pets, pet services"),
# 				("whois","mobile apps, mobile, applications"),
# 				('whosit','games, consumer products')]

indices = (120,180)
with open('team_negative_processed.json','r') as infile:
	companies = json.load(infile)

keys = ['ratio_orgs', 'newsapi_totalResults', 'root_mean_distance', 'num_orgs', 'num_non_orgs', 'num_titlecase', 'num_articles',
 'org_at_least_once', 'num_found', 'num_industries', 'ratio_case', 'newsapi_rawResults','avg_article_length']

for i in range((indices[0] // 20) , (indices[1]//20)):
	print("{}, {}".format(20*i,20*(i+1)))
	print ("beginning batch {}...".format(i))
	with open("extra_negative_contexts/record_contexts" + str(i) + ".csv", 'w') as out_context:
		with open("extra_negative_features/record_features" + str(i) + ".csv", 'w') as out_features:
			out_features.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(*(["name","industries"] + keys)))
			for company in companies[20*i:20*(i+1)]:
				current = Gatherer(company[0],company[1]).gather_contexts()
				out_context.write(current.entity.replace(',',';') + "," + ";".join(current.industries) + "," + \
							"4899".join([c.replace(',',';').replace('\n',' ').replace('\r',' ') for c in current.contexts]) + "\n")
				out_features.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n"\
					.format(*([current.entity.replace(',',';'),";".join(current.industries)] + \
								[current.features[key] for key in keys])))
	print ("completing batch {}...".format(i))