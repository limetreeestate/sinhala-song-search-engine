# Sinhala song search engine

### Requirements
This system is based on ElasticSearch, a correct URL of the host location of the running ElasticSearch service should be provided in the `conf.json` file. The corpus provided in https://github.com/binodmx/sinhala-songs-corpus is used as a reference in making this system, and therefore a record in the ElasticSearch database should follow the structure of this corpus.

### Usage
This system conducts search on an already existing ElasticSearch server running locally or remotely. Data can be loaded from the JSON file in the repository (Taken from https://github.com/binodmx/sinhala-songs-corpus) or uploaded by the user. 

`SubmitData.py` handles the task of adding data to the ElasticSearch database. `PrepareJson.py` can be used to encode multiline strings into an acceptable JSON format.
`Search.py` handles the actual searching.