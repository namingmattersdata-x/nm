# Using the Simple Model

Please see `./datax_nm_final_presentation.pptx` for a general overview. The "app" that is referenced in these docs refers to Method 2 of the powerpoint, which we found to be much more useful/usable than Method 1 (which was more of a theoretical experiment).

### Dependencies

The necessary dependencies should be contained within `requirements.txt`. However, this is simply a `pip freeze` of my local environment while testing the app. It contains many extra unecessary packages that are simply the result of Anaconda default installs.

The only non-base packages that I believe are required are: 
- newsapi-python
- sner
- beautiful soup, requests
- pandas, numpy

Additionally, Stanford's named-entity-recognition package must be downloaded. It can be found at https://nlp.stanford.edu/software/CRF-NER.shtml#Download under `Download Stanford Named Entity Recognizer version x.x.x`.

In order for the app to function fully, the sner classifier must be running on local port while running the app. To start the "server", run the following command from the root of the SNER folder that was downloaded.
```bash
java -Djava.ext.dirs=./lib -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -port 9199 -loadClassifier ./classifiers/english.all.3class.distsim.crf.ser.gz  -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer -tokenizerOptions tokenizeNLs=false
```

### Test the App

From the root of the repo, run
```bash
python -m simple_model.run "name of company" "industries separated by comma"
```
This will print an overall risk score to standard out and store a csv in the `./cache/random_forest/` directory. The CSV contains links to articles that were determined to most contribute to the potential risk involved. These are ordered in descending by "risk score" - one of which each webpage is assigned. Note that this webpage-specific risk score was added in haste mostly for purposes of presenting a feature, the normalization and calculation of these risk scores could use much work. (IMPORTANT: these webpage-specific risk scores completely irrelevant from the overall risk score which is given in standard output.

### Structure of the Repo
There is a lot of stuff in the repo which is irrelevant. Perhaps there is some value to be derived in them,   but likely not. All that is usable and that comprises the "app" presented above is found in `./simple_model/`.

Within `./simple_model/` are four directories: `data/`, `models/`, `scripts/`, and `tools/`. `scripts/` contains one-off stuff and likely contains nothing useful. `data/` contains training data for the models themselves. `models/` contains code to build the models and retrieve relevant model parameters. `tools/` contains the class `Gatherer`, which pulls webpage information from the newsapi.

The file `run.py` in `./simple_model` is the cockpit for the app and is quite easy to interpret.

### How it Works

It will be necessary to read through the code to properly understand the moving parts, but here is a basic overview beyond the powerpoint.

#### Predict
Essentially, the app takes the user specified company name and industry/industries and queries the newsapi (https://newsapi.org/) for web results. It then visits a subset of the resulting articles/webpages (was too slow to visit a ton of results, since many http requests are involved). It processes those pages and derives a number of numerical features such as how often the queried terms appear in the page in titlecase, how often they are classified by sner as organizations, root mean squared character distance between the name and the industries, etc. It then uses these features and our model(s) to predict a probability of positive classification. A positive classification in the context of our model is "This is in fact a company that does business in at least one of these industries".

#### Model(s)
The model that we found to perform better and be more interpretable was the random forest model, although results are often not that polar between the logistic model and the rf model.  To find the parameters of the model based on our training data, `models/rf.py` can be run (it is very self-explanatory).

#### Data
Training data was and is a challenge of this implementation. On one hand, finding positive training data is very easy (most of our positive training data was taken from crunchbase). Finding negative training data is quite hard, however. We took a couple of approaches to building/gathering negative training data:
- Associate real company names with pseudorandom erroneous industries (that they ostensibly do not operate in).
- Manually create entirely fake company names and confirm to some real extent that they are not real companies (industry here can be random).
- Some total BS inputs.

All of these options *should* present negative classifications for our model as desired, but the truth behind the method is questionable. Better solutions for generating/finding negative training data could serve to improve the model results extensively.

### Improvements
- Better negative training data and more training data in general.
- More sources for internet/doc search. The current implementation only uses newsapi but this could be easily expanded to incorporate as many search engines as desired, including offline unstructured bodies of text.
- Industry canonization/classification tools for more robust industry association.
- Fuzzy search to expand model capabilities to recognize risk in a broader umbrella of names that are phonetically/syntactically similar to the desired name.

