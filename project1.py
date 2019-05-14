import json
import os
#print(os.getcwd())
import csv
import glob
import nltk
from nltk.corpus import stopwords
from collections import Counter
from math import log, sqrt

# Ranjan: I've had to do this because I am using an IDE and the working directory is something weird. You can remove this line if you want.
os.chdir("C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1" )

# This helper method just reads a json file and returns the object
def read_json(filename):

    with open(filename) as json_file:  
        claims = json.load(json_file)
        
    #    for key, value in claims.items():
    #        print('Id: ' + key)
    #        print('claim:  ' + value['claim'])
    #        print('label:  ' + value['label'])
        return claims

def stem_sentence(sentence):
    stemmer = nltk.stem.PorterStemmer()
    #return [stemmer.stem(word.lower()) for word in sentence if word.lower() in stopwords.words('english')]
    return [stemmer.stem(word.lower()) for word in sentence]

def add_sentence_to_vocab(sentence, vocab):
    for word in sentence:
        if word not in vocab:
            vocab[word] = len(vocab)
        
    return vocab

def read_wiki_data():
    wiki_raw_data = {}
    #wiki_processed_data = {}
    doc_term_freqs = {}
    vocab = {}
    csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)

    wiki_data_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-test\\*.txt'
    wiki_files = glob.glob(wiki_data_path)

    for name in wiki_files: 
        current_ID = ''
        with open(name, encoding='utf8') as wikifile:
            for row in csv.reader(wikifile, dialect='space'):
                
                
                #print(len(wiki_raw_data))
                if(current_ID != row[0]):
                    current_ID = row[0]
                #print(current_ID)
                stemmed_sentence = stem_sentence(row[2:])
                vocab = add_sentence_to_vocab(stemmed_sentence, vocab)
                if current_ID in doc_term_freqs:
                    #print("Update")
                    wiki_raw_data[current_ID].append(row[2:])
                    #wiki_processed_data[current_ID].append(stemmed_sentence)
                    #doc_term_freqs[len(doc_term_freqs)-1] = doc_term_freqs[len(doc_term_freqs)-1].update(Counter(stemmed_sentence))
                    doc_term_freqs[current_ID].update(Counter(stemmed_sentence))
                else:
                    #print("New")
                    wiki_raw_data[current_ID] = [row[2:]]
                    #wiki_processed_data[current_ID] = [stemmed_sentence]
                    doc_term_freqs[current_ID] = Counter(stemmed_sentence)
                
                #print(doc_term_freqs[current_ID])

    print(len(wiki_raw_data))
    print(len(doc_term_freqs))
    print(doc_term_freqs["1986_NBA_Finals"])
    print(len(vocab))

    return (vocab, doc_term_freqs, wiki_raw_data)

def decompress_list(input_bytes, gapped_encoded):
    res = []
    prev = 0
    idx = 0
    while idx < len(input_bytes):
        dec_num, consumed_bytes = vbyte_decode(input_bytes, idx)
        idx += consumed_bytes
        num = dec_num + prev
        res.append(num)
        if gapped_encoded:
            prev = num
    return res

def vbyte_encode(num):

    # out_bytes stores a list of output bytes encoding the number
    out_bytes = []
    
    ###
    # Your answer BEGINS HERE
    ###
    # Implement the compression algorithm from the lecture slides
    while num>=128:
        out_bytes.append(num%128)
        num = num // 128
    out_bytes.append(num + 128)
    ###
    # Your answer ENDS HERE
    ###
    
    return out_bytes


def vbyte_decode(input_bytes, idx):
    
    # x stores the decoded number
    x = 0
    # consumed stores the number of bytes consumed to decode the number
    consumed = 0

    ###
    # Your answer BEGINS HERE
    ###
    #Apply the decompression algorithm from the lecture slides
    s = 0
    while input_bytes[idx] < 128:
        x = x ^ (input_bytes[idx] << s)
        s = s + 7
        idx = idx + 1
        consumed = consumed + 1
    
    x = x ^ ((input_bytes[idx] - 128) << s)
    consumed = consumed + 1
    ###
    # Your answer ENDS HERE
    ###
    
    return x, consumed

class CompressedInvertedIndex:
    def __init__(self, vocab, doc_term_freqs):
        self.vocab = vocab
        self.doc_len = [0] * len(doc_term_freqs)
        self.doc_term_freqs = [[] for i in range(len(vocab))]
        self.doc_ids = [[] for i in range(len(vocab))]
        self.doc_freqs = [0] * len(vocab)
        self.total_num_docs = 0
        self.max_doc_len = 0
        for docid, term_freqs in enumerate(doc_term_freqs):
            doc_len = sum(term_freqs.values())
            self.max_doc_len = max(doc_len, self.max_doc_len)
            self.doc_len[docid] = doc_len
            self.total_num_docs += 1
            for term, freq in term_freqs.items():
                term_id = vocab[term]
                self.doc_ids[term_id].append(docid)
                self.doc_term_freqs[term_id].append(freq)
                self.doc_freqs[term_id] += 1

        # TODO NOW WE COMPRESS THE LISTS
        
        ###
        # Your answer BEGINS HERE
        ###
        
        # For doc_ids and doc_term_freqs, compress each list item while also using the gapped encoding method
        
        for doc_list in self.doc_ids:
            byte_array = []
            prev = 0
            for doc_id in doc_list:
                # subtract the previous value to get the gapped encoding
                byte_array.append(vbyte_encode(doc_id - prev))
                prev = doc_id
            doc_list = byte_array
            
        
        for doc_list in self.doc_term_freqs:
            byte_array = []
            prev = 0
            for doc_id in doc_list:
                # subtract the previous value to get the gapped encoding
                byte_array.append(vbyte_encode(doc_id - prev))
                prev = doc_id
            doc_list = byte_array
        ###
        # Your answer ENDS HERE
        ###
    
    def num_terms(self):
        return len(self.doc_ids)

    def num_docs(self):
        return self.total_num_docs

    def docids(self, term):
        term_id = self.vocab[term]
        # We decompress
        return decompress_list(self.doc_ids[term_id], True)

    def freqs(self, term):
        term_id = self.vocab[term]
        # We decompress
        return decompress_list(self.doc_term_freqs[term_id], False)

    def f_t(self, term):
        term_id = self.vocab[term]
        return self.doc_freqs[term_id]

    def space_in_bytes(self):
        # this function assumes the integers are now bytes
        space_usage = 0
        for doc_list in self.doc_ids:
            space_usage += len(doc_list)
        for freq_list in self.doc_term_freqs:
            space_usage += len(freq_list)
        return space_usage


data = read_wiki_data()

# We output the same statistics as before to ensure we still store the same data but now use much less space
#compressed_index = CompressedInvertedIndex(data[0], data[1])

def query_tfidf(query, index, k=10):
    
    # scores stores doc ids and their scores
    scores = Counter()
    
    ###
    # Your answer BEGINS HERE
    ###
    # iterate over the query terms
    for query_term in query:
        # check if the query term is in the vocabulary, ignore if not
        if query_term in index.vocab:
            term_id = index.vocab[query_term]
            #iterate over all the documents which contain the term
            for doc_id in index.doc_ids[term_id]:
                #Apply the formula for TF-IDF similarity scores
                scores.update({doc_id:(log(1 + index.doc_term_freqs[term_id][index.doc_ids[term_id].index(doc_id)])*log(index.total_num_docs/index.doc_freqs[term_id]))/sqrt(index.doc_len[doc_id])})
    ###
    # Your answer ENDS HERE
    ###
    
    return scores.most_common(k)

class InvertedIndex:
    def __init__(self, vocab, doc_term_freqs):
        self.vocab = vocab
        self.doc_len = {}
        self.doc_term_freqs = [[] for i in range(len(vocab))]
        self.doc_ids = [[] for i in range(len(vocab))]
        self.doc_freqs = [0] * len(vocab)
        self.total_num_docs = 0
        self.max_doc_len = 0
        for docid, term_freqs in doc_term_freqs.items():
            doc_len = sum(term_freqs.values())
            self.max_doc_len = max(doc_len, self.max_doc_len)
            self.doc_len[docid] = doc_len
            self.total_num_docs += 1
            for term, freq in term_freqs.items():
                term_id = vocab[term]
                self.doc_ids[term_id].append(docid)
                self.doc_term_freqs[term_id].append(freq)
                self.doc_freqs[term_id] += 1

    def num_terms(self):
        return len(self.doc_ids)

    def num_docs(self):
        return self.total_num_docs

    def docids(self, term):
        term_id = self.vocab[term]
        return self.doc_ids[term_id]

    def freqs(self, term):
        term_id = self.vocab[term]
        return self.doc_term_freqs[term_id]

    def f_t(self, term):
        term_id = self.vocab[term]
        return self.doc_freqs[term_id]

    def space_in_bytes(self):
        # this function assumes each integer is stored using 8 bytes
        space_usage = 0
        for doc_list in self.doc_ids:
            space_usage += len(doc_list) * 8
        for freq_list in self.doc_term_freqs:
            space_usage += len(freq_list) * 8
        return space_usage
    

invindex = InvertedIndex(data[0], data[1])

query = "nba boston champion"
stemmed_query = nltk.stem.PorterStemmer().stem(query).split()
results = query_tfidf(stemmed_query, invindex)
for rank, res in enumerate(results):
    # e.g RANK 1 DOCID 176 SCORE 0.426 CONTENT South Korea rose 1% in February from a year earlier, the
    print("RANK {:2d} DOCID {} SCORE {:.3f}".format(rank+1,res[0],res[1]))