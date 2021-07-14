
'''
Trang Hoang - UdS
Simple search engine using tf-idf
'''

import sys
import re
from collections import defaultdict
from math import log
import csv
from os.path import isfile
from helpers import *



class SearchEngine:

    def __init__(self, collectionName, create):
        '''
        Initialize the search engine, i.e. create or read in index. If
        create=True, the search index is created and written to
        files. If create=False, the search index will read from
        the files. The collectionName points to the filename of the
        document collection (without the .xml at the end).

        The idf index is written/read to/from file <collectionName>.idf, 
        and the tf index to/from file <collectionName>.tf in this directory.
        '''

        tf_file_name = collectionName+'.tf'
        idf_file_name = collectionName+'.idf'

        ############### Creating index files #######################

        if create == True: 

            with open(collectionName+'.xml') as f:
                collection = f.read()
               
            docs_xml = re.findall('<DOC id=".+?</DOC>', collection, re.DOTALL) 
            #list of all strings that are between DOC tags

            all_docs = list() # list of  all docs (instances of class Document) in collection

            for doc in docs_xml:
                doc_id, content = process_xml_doc(doc)
                document = Document(doc_id, content) # create an object Document 
                all_docs.append(document)

            all_docs.sort(key=lambda x: x.doc_id) # sort docs by id 
            
            tf_by_doc = defaultdict(lambda: defaultdict(float))
            # nested dictionary storing tf of words in all documents

            all_df = defaultdict(int)
            # dict of df of all words in vocab, values to be added as program iterates 
            # over all docs to compute tf, see next block      

            with open(tf_file_name, 'w') as f:  # write tf in tf file
                for document in all_docs:        
                    for word in sorted(set(document.word_counts)):
                        all_df[word] += 1 # updating df of the word
                        tf = document.compute_tf(word)
                        tf_by_doc[document.doc_id][word] = tf
                        f.write(document.doc_id + '\t' + word + '\t' + str(tf) + '\n')


            N = len(all_docs) # total number of docs in collection

            all_idf = dict() # dict storing idf of all words in vocab

            with open(idf_file_name, 'w') as f:  # write idf in idf file
                for word in sorted(all_df.keys()):
                    idf = log(N/all_df[word])
                    all_idf[word] = idf
                    f.write(word + '\t' + str(idf) + '\n')


        ############ Read index files into dictionaries ##################

        if create == False:

            tf_by_doc = defaultdict(lambda: defaultdict(float))
            all_idf = dict()

            with open(idf_file_name) as f:
                idf_table = csv.reader(f, delimiter = '\t')
                for row in idf_table: # iterate over all rows, add idf of all words to idf dict
                    all_idf[row[0]] = float(row[1])

            with open(tf_file_name) as f:
                tf_table = csv.reader(f, delimiter = '\t')        
                for row in tf_table: # iterate over all rows, add tf of all words/all docs to idf dict
                    tf_by_doc[row[0]][row[1]] = float(row[2])  


        ############ Define class attributes ###########################

        self.tf_index = tf_by_doc
        self.idf_index = all_idf


    def weight_term(self, doc_id, term):
        '''
        takes as input the id of a document and a term
        looks up tf and idf of the term 
        returns tf.idf of the term in the doc
        '''
        return self.tf_index[doc_id][term]*self.idf_index[term]
        # if term's not in doc, will give 0 as tf (defaultdict default value)
        
     
    def executeQuery(self, queryTerms):
        '''
        Input: List of query terms
        Returns up to 10 highest ranked documents together with their
        tf.idf-sum scores, sorted by score
        '''
        queryTerms = [stem(term.lower()) for term in queryTerms]
        

        if all(term not in self.idf_index for term in queryTerms):
            return 0 # all query terms are OOV

        else:
            
            result = list()

            query_doc = Document(None, queryTerms)

            q_vector = {term: query_doc.word_counts[term]*self.idf_index[term] \
                        for term in query_doc.word_counts}

            q_vector = defaultdict(float, q_vector)

            for doc_id in self.tf_index:
                d_vector = {term: self.weight_term(doc_id, term) \
                            for term in self.tf_index[doc_id]}
                d_vector = defaultdict(float, d_vector)

                score = cosine(d_vector, q_vector)
 
                if score != 0: # if score = 0, ignore doc

                    if len(result) < 10: # if result list has less than 10 docs, 
                                            # add current doc regardless of score
                        result.append((doc_id, score))
                        result.sort(key=lambda x: x[1], reverse=True)

                    else: # if result list already has 10 docs, 
                            # compare score with lowest score from result list
                        if score <= result[-1][1]:
                            result[-1] = (doc_id, score)
                        result.sort(key=lambda x: x[1], reverse=True)

            return result

        
    def executeQueryConsole(self):
        '''
        starts interactive console, asks for queries and displays the search results,
        until the user simply hits enter
        '''
        while True:
            query = input('\nPlease enter query terms separated by whitespace: ')

            if query == '':
                break
            
            else:               
                query_terms = query.split()
                search_result = self.executeQuery(query_terms)
                
                if search_result == 0:
                    print("Sorry, I didn't find any documents for this query.")
                elif len(search_result) == 0:
                    print("Query terms too common. Please use more specific terms.") 
                else:
                    print('I found the following documents:')
                    print(*search_result, sep='\n') 


#----------------------------------------------------------------------------        

 
    
if __name__ == '__main__':
    '''
    * load index / start search engine
    * start the loop asking for query terms
    * program should quit if users enters no term and simply hits enter
    '''
    default_collection = 'nyt199501'

    try:
        collection = sys.argv[1]       
    except:
        collection = default_collection
    # if no collection name is specified in command line, use the default collection

    if not isfile(collection+'.xml'):
        collection = default_collection
        print('\nCollection cannot be found. Search engine will be generated using '
             + default_collection + ' collection.\n')
    # if the specified collection is not found, use default collection


    indices_exist = isfile(collection+'.tf') and isfile(collection+'.idf')
    # check if index files already exist

    print('Reading index from file...')

    searchEngine = SearchEngine(collection, create = not indices_exist)
    # create index files if they don't exist yet, otherwise read in existing index files
    
    print('Done.')

    searchEngine.executeQueryConsole()