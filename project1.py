import json
import os
#print(os.getcwd())
import csv
import glob
import nltk
from nltk.corpus import stopwords

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

def read_wiki_data():
    wiki_raw_data = {}
    csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)

    wiki_data_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-test\\*.txt'
    wiki_files = glob.glob(wiki_data_path)

    for name in wiki_files: 
        current_ID = ''
        with open(name, encoding='utf8') as wikifile:
            for row in csv.reader(wikifile, dialect='space'):
                
                #print(current_ID)
                #print(len(wiki_raw_data))
                if(current_ID != row[0]):
                    current_ID = row[0]
                if current_ID in wiki_raw_data:
                    wiki_raw_data[current_ID].append(stem_sentence(row[2:]))
                else:
                    wiki_raw_data[current_ID] = [stem_sentence(row[2:])]

    print(len(wiki_raw_data))

read_wiki_data()