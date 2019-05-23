import json
import whoosh
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh import scoring
import os
#print(os.getcwd())
import csv
import glob


os.chdir("D:\Web Search" )

def read_json(filename):

    with open(filename) as json_file:  
        claims = json.load(json_file)
        
    #    for key, value in claims.items():
    #        print('Id: ' + key)
    #        print('claim:  ' + value['claim'])
    #        print('label:  ' + value['label'])
        return claims


def create_index():


    schema = whoosh.fields.Schema(title = whoosh.fields.ID(stored=True, unique=True), document=whoosh.fields.TEXT(stored=True), sentence_mapping=whoosh.fields.STORED)

    if not os.path.exists("index"):
        os.mkdir("index")
    ix = whoosh.index.create_in("index", schema)

    return ix

def create_temp_index():

    schema = whoosh.fields.Schema(sentence_number = whoosh.fields.ID(stored=True, unique=True), document=whoosh.fields.TEXT(stored=True))

    if not os.path.exists("temp_index"):
        os.mkdir("temp_index")
    ix = whoosh.index.create_in("temp_index", schema)

    return ix

def get_sentences_from_mapping(document, sentence_mapping):
    sentences = {}
    cursor = 0
    document_as_list = document.split()
    for sentence in sentence_mapping:
        sentence_text = get_sentence_text(sentence[1], cursor, document_as_list)
        sentences[sentence[0]] = " ".join(sentence_text)
        cursor += sentence[1]
    return sentences

def get_sentence_text(sentence_length, offset, document_as_list):
    return document_as_list[offset:sentence_length+offset-1]

def get_top5_sentences_for_document(document, sentence_mapping, hypothesis):
    sentences = get_sentences_from_mapping(document, sentence_mapping)
    index = create_temp_index()
    writer = index.writer()
    for sentence_number, sentence in sentences.items():
        #print(sentence)
        #print(sentence_number)
        writer.add_document(sentence_number = str(sentence_number), document=sentence)
    writer.commit()

    #with index.searcher(weighting=scoring.Frequency()) as searcher:
    #pos_weighting = scoring.FunctionWeighting(pos_score_fn)
    #with myindex.searcher(weighting=pos_weighting) as searcher:
    with index.searcher(weighting=scoring.BM25F(B=0.0, K1=1.5)) as searcher:
    #print(hypothesis)
    #print(document)
    #with index.searcher() as searcher:
        parser = whoosh.qparser.QueryParser("document", index.schema, group=whoosh.qparser.syntax.OrGroup)
        myquery = parser.parse(hypothesis)
        results = searcher.search(myquery, limit=5)
        return_object = []
        for result in results:
            return_object.append({"sentence_number" : result["sentence_number"], "document" : result["document"], "score" : result.score})
        return return_object

def pos_score_fn(searcher, fieldname, text, matcher):
    poses = matcher.value_as("positions")
    return 1.0 / (poses[0] + 1)


def add_data_to_index():
    #wiki_raw_data = {}
    #wiki_processed_data = {}
    #doc_term_freqs = {}
    #vocab = {}
    csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)

    #wiki_data_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-test\\*.txt'
    wiki_data_path = 'D:\\Web Search\\wiki-pages-text\\*.txt'
    wiki_files = glob.glob(wiki_data_path)

    ix = create_index()

    #writer.add_document(title=u"My document", content=u"This is my document!")
    #writer.add_document(title=u"My document2", content=u"This is my document!2")
    #writer.add_document(title=u"My document3", content=u"This is my document!3")

    #writer.commit()

    
    writer = ix.writer()

    for name in wiki_files: 
        current_ID = ''
        sentence_mapping = []
        document = ''
        with open(name, encoding='utf8') as wikifile:
            for row in csv.reader(wikifile, dialect='space'):
                #print(current_ID)
                if(current_ID != row[0]):
                    if(current_ID != ''):
                        writer.add_document(title=current_ID, document=document, sentence_mapping=sentence_mapping)
                    current_ID = row[0]
                    sentence_mapping = []
                    document = ''
                if(row[1].isdigit() and len(row) > 2):
                    sentence_mapping.append((int(row[1]), len(row) - 2))
                    document = document + " " + " ".join(row[2:])
        #print(name)

    writer.commit()
                            
                #print("Loop")

    #print(len(wiki_raw_data))
    #rint(len(doc_term_freqs))
    #print(doc_term_freqs["1986_NBA_Finals"])
    #print(len(vocab))

    #return (vocab, doc_term_freqs, wiki_raw_data)
    return ix

    
def get_index():
    ix = whoosh.index.open_dir("index")
    return ix


#ix = add_data_to_index()

def get_top_5_sentences(premise, searcher, parser):


    #ix = get_index()
    #print(ix.doc_count())


    myquery = parser.parse(premise)
    results = searcher.search(myquery)
    #print(len(results))
    all_sentence_results = []
    #print(len(results[:5]))
    for result in results[:5]:
        #print(result["document"])
        #print(result["sentence_mapping"])
        sentence_results = get_top5_sentences_for_document(result["document"], result["sentence_mapping"], premise)
        #print(len(sentence_results))
        for sentence_result in sentence_results:
            all_sentence_results.append((result["title"], sentence_result["sentence_number"], sentence_result["document"], sentence_result["score"]))

    all_sentence_results.sort(key=lambda x: x[3], reverse = True)

    return all_sentence_results[:5]
    #print(len(all_sentence_results))
    #print(all_sentence_results[0])
    #print(all_sentence_results[1])
    #print(all_sentence_results[2])
    #print(all_sentence_results[3])
    #print(all_sentence_results[4])
    #print(len(results))
    #print(results[0])
    #print(results[1])
#    print(results[2])

def create_test_input(filepath):
    file_json = read_json(filepath)
    input_file_name = os.path.basename(filepath) + "_input"

    ix = get_index()


    parser = whoosh.qparser.QueryParser("document", ix.schema, group = whoosh.qparser.syntax.OrGroup)
    #with ix.searcher() as searcher:
    #with ix.searcher(weighting=scoring.BM25F(B=0.0, K1=1.5)) as searcher:
    with ix.searcher() as searcher:
        #print(mapping_json)
        with open(input_file_name, 'w') as outfile:
            
            #json.dump(mapping_json, outfile)
            #json.dump(mapping, outfile)
            for key, value in file_json.items():
                data_line = {}
                data_line["hypothesis"] = value["claim"]
                #if(value["label"] == "NOT ENOUGH INFO"):
                #    data_line["sentence2"] = (" ".join(get_random_sentence()))
                #else:
                #    evidence = ""
                #    for e in value["evidence"]:
                #        evidence += (" ".join(get_evidence_text(e[0], str(e[1]), mapping_json)) + " ")
                sentences = get_top_5_sentences(value["claim"], searcher, parser)
                #premise_object = {}
                #for sentence in sentences:
                    #premise_object[sentence[0] + " " + sentence[1]] = sentence[2]
                
                #data_line["premise"] = premise_object
                premise = ""
                for sentence in sentences:
                    premise = premise + " " + sentence[2]
                data_line["premise"] = premise
                json_string = json.dumps(data_line)
                outfile.write(json_string + "\n")
                print(key)

#def build_query(input):


create_test_input("test-unlabelled.json")
#create_test_input("test-unlabelled - Copy.json")


#print("|" + " ".join(["a", "b", "c", "d"]) + "|")