import json
import os
import csv
import glob
import random

def create_file_id_mapping():
    os.chdir("C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1" )
    csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)

    #wiki_data_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-test\\*.txt'
    wiki_data_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-pages-text\\*.txt'
    wiki_files = glob.glob(wiki_data_path)

    mapping = {}

    for name in wiki_files:
        with open(name, encoding='utf8') as wikifile:
            id_list = []
            for row in csv.reader(wikifile, dialect='space'):
                if row[0] not in id_list:
                    id_list.append(row[0])
            mapping[os.path.basename(name)] = id_list

    #mapping_json = json.dumps(mapping)

    #print(mapping_json)
    with open('file_document_mapping.txt', 'w') as outfile:  
        #json.dump(mapping_json, outfile)
        json.dump(mapping, outfile)

# document_id and sentence_number are both strings
def get_evidence_text(document_id, sentence_number, mapping_json):
    os.chdir("C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1" )
    document_name = ''
    
    #return type(mapping_json)
    for key, value in mapping_json.items():
        if document_id in value:
            document_name = key
            break

    csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)

    #document_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-test\\' + document_name
    document_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-pages-text\\' + document_name

    if document_path != 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-pages-text\\':

        with open(document_path, encoding='utf8') as file:
            for row in csv.reader(file, dialect='space'):
                if row[0] == document_id and row[1] == sentence_number:
                    return row[2:]

    return " "

def get_random_sentence():
    try:
        csv.register_dialect('space', delimiter=' ', quoting=csv.QUOTE_NONE)
        document_path = 'C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-pages-text\\' + random.choice(os.listdir("C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1\\wiki-pages-text\\"))
        filesize = os.path.getsize(document_path)
        offset = random.randrange(int(filesize-(filesize/20)))
        with open(document_path, encoding='utf8') as file:
            file.seek(offset)                  
            file.readline()        
            random_line = file.readline().rstrip()
            return (random_line.split(" ")[2:])
    except:
        return get_random_sentence()
                
# This helper method just reads a json file and returns the object
def read_json(filename):

    with open(filename) as json_file:  
        claims = json.load(json_file)
        
    #    for key, value in claims.items():
    #        print('Id: ' + key)
    #        print('claim:  ' + value['claim'])
    #        print('label:  ' + value['label'])
        return claims

def convert_to_allen_dataset(filepath):
    file_json = read_json(filepath)
    input_file_name = os.path.basename(filepath) + "_input"

    #print(mapping_json)
    with open(input_file_name, 'w') as outfile:
        with open('file_document_mapping.txt') as json_file:
        
            mapping_json = json.load(json_file)
            #json.dump(mapping_json, outfile)
            #json.dump(mapping, outfile)
            for key, value in file_json.items():
                data_line = {}
                data_line["gold_label"] = value["label"]
                data_line["sentence1"] = value["claim"]
                if(value["label"] == "NOT ENOUGH INFO"):
                    data_line["sentence2"] = (" ".join(get_random_sentence()))
                else:
                    evidence = ""
                    for e in value["evidence"]:
                        evidence += (" ".join(get_evidence_text(e[0], str(e[1]), mapping_json)) + " ")
                        data_line["sentence2"] = evidence.rstrip()
                json_string = json.dumps(data_line)
                outfile.write(json_string + "\n")
                print(key)

def convert_to_allen_dataset_for_test(filepath):
    file_json = read_json(filepath)
    input_file_name = os.path.basename(filepath) + "_input"

    #print(mapping_json)
    with open(input_file_name, 'w') as outfile:
        with open('file_document_mapping.txt') as json_file:
        
            mapping_json = json.load(json_file)
            #json.dump(mapping_json, outfile)
            #json.dump(mapping, outfile)
            for key, value in file_json.items():
                data_line = {}
                data_line["gold_label"] = ""
                data_line["sentence1"] = value["claim"]
                #if(value["label"] == "NOT ENOUGH INFO"):
                #    data_line["sentence2"] = (" ".join(get_random_sentence()))
                #else:
                #    evidence = ""
                #    for e in value["evidence"]:
                #        evidence += (" ".join(get_evidence_text(e[0], str(e[1]), mapping_json)) + " ")
                data_line["sentence2"] = ""
                json_string = json.dumps(data_line)
                outfile.write(json_string + "\n")
                print(key)

os.chdir("C:\\Users\\ranji.LAPTOP-LO7RC9LJ\\Documents\\Web Search\\Project1" )
convert_to_allen_dataset_for_test("test-unlabelled.json")
#convert_to_allen_dataset("train_test.json")



#create_file_id_mapping()
#print(" ".join(get_evidence_text("Marisara_Pont_Marchese", "6")))
#print(" ".join(get_random_sentence()))