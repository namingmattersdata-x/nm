# import nltk.tag.stanford as st
# from nltk.tokenize import word_tokenize, sent_tokenize
# import os

# os.environ["STANFORD_MODELS"] = "C:/Users/Andrew/Documents/School/S18/IEOR135/ts/School/S18/IEOR135/stanford-ner-2018-02-27"

# java_path = "C:/Program Files/Java/jdk1.8.0_131/bin/java.exe"
# os.environ['JAVAHOME'] = java_path

# tagger = st.StanfordNERTagger('C:/Users/Andrew/Documents/School/S18/IEOR135/stanford-ner-2018-02-27/classifiers/english.all.3class.distsim.crf.ser.gz',
# 							   'C:/Users/Andrew/Documents/School/S18/IEOR135/stanford-ner-2018-02-27/stanford-ner.jar',
# 					  		 encoding='utf-8')

# text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'

# tokenized_text = word_tokenize(text)
# classified_text = tagger.tag(tokenized_text)
# print(classified_text)

from sner import Ner
import json
tagger = Ner(host='localhost',port=9199)
with open('resolute_forestry_context.json', 'r') as infile:
	contexts = [e[0] for e in json.load(infile)]
print(len(contexts))
classified = []
for context in contexts:
	# tokenized_sents = [word_tokenize(sent) for sent in sent_tokenize(context)]
	# print(tokenized_sents)
	# tokenized_text = word_tokenize(context)
	# print(tagger.tag_sents(tokenized_sents))
	print(tagger.get_entities(context))
	# classified.extend(tagger.tag_sents(tokenized_sents))
# from pprint import PrettyPrinter
# with open("classified.txt", 'w') as out:
# 	PrettyPrinter(stream=out).pprint(classified)

