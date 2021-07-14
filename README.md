# search-engine
Simple search engine using tf-idf

This is a simple search engine based on tf-idf.

The text corpora that contain the documents to be searched
are in XML-like format (nyt199501.xml and nytsmall.xml)

Run the program with the command:
    $ python search-engine.py [corpus_name]
    
Do not include ".xml" in corpus_name. 
If no corpus file is specified or if the corpus file does not exist,
the program will use the nyt199501 corpus.

The first time the search engine is initiated, it will create index files
for all the tf and idf, which might take a few minutes. Once these index files
already exist, subsequent runs of the search engine will just read in these files.

To build the search engine and create new index files from scratch, make sure the index
files (corpus_name.tf and corpus_name.idf) do not already exist in the
directory. Otherwise, the program will simply read in these files.
