# helper functions and class for the search engine

from string import punctuation
import re
from stemming.porter2 import stem
from math import sqrt
from collections import Counter


def remove_punc(string):
    '''remove punctuation characters from a string'''
    return ''.join(c for c in string if c not in punctuation)
assert remove_punc('Just, test!ng th?s fun.cti()n') == 'Just testng ths functin'


def process_xml_doc(xml_doc):
    '''
    takes as input  a document in the form of a string starting with 
    '<DOC id' and ending with '</DOC>'
    returns doc id and content as a list of lowercased, stemmed words
    '''
    id_mo = re.search('id=.+?"', xml_doc, re.DOTALL) # get doc id
    doc_id = id_mo.group(0)[3:]

    content_mo = re.search('<TEXT>.+?</TEXT>', xml_doc, re.DOTALL) # get content
    content = content_mo.group(0)[6:-8].lower().split()    

    hline_mo = re.search('<HEADLINE>.+?</HEADLINE>', xml_doc, re.DOTALL) # get headline
    if hline_mo:
        hline = hline_mo.group(0)[10:-12].lower().split()

        content.extend(hline) # combine content and headline

    content = [remove_punc(token) for token in content if token != '<p>' and token != '</p>'] 
    # remove punctuation from all tokens

    content = [stem(token) for token in content] # stem all tokens

    return doc_id, content


def cosine(d, q):
    '''
    takes as input two non-0 vectors in the form of dictionaries
    returns cosine similarity
    '''
    if all(dim not in d for dim in q):
        return 0 # dot product = 0 -> cosine = 0
        
    else:
        dot_prod = sum(d[dim]*q[dim] for dim in q)

        sumsq_q = sum(q[dim]**2 for dim in q)

        sumsq_d = 0
        for dim in d:
            sumsq_d += d[dim]**2

        norm_prod = sqrt(sumsq_q*sumsq_d)

        return dot_prod/norm_prod


class Document:

    def __init__(self, doc_id, content):
        '''content: list of all tokens in document'''

        self.doc_id = doc_id

        self.word_counts =  Counter(content)
        del self.word_counts[''] # remove empty strings

        self.max_occ = self.word_counts.most_common(1)[0][1] # max occurrence in document

    def compute_tf(self, term):
        '''compute tf in the document of a given term'''
        return self.word_counts[term]/self.max_occ