import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
#import pprint
import pandas as pd
import treetaggerwrapper
from pymongo import MongoClient

conn_str = 'mongodb://localhost:27017/'
client = MongoClient(conn_str)
db = client['db_perfilador']
col_nouns = db['nouns_collection']
col_verbs = db['verbs_collection']

tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')

# hacer un conteo global de todos los textos
tags = tagger.tag_file('CORPUS A2.txt')
#tags2 = tagger.tag_file('sample2.txt')
#pprint.pprint(tags)
#pprint.pprint(tags2)
total_list = []
ttags = []
for tag in tags:
    elem = tag.split('\t')
    if len(elem) ==3:
        if elem[1].startswith("N"):
            found = col_nouns.find_one({"$and":[{"complex_words":elem[0].upper()},
                                                {"PoS_tag":elem[1]}]},{"_id":0})
        elif elem[1].startswith("V"):
            found = col_verbs.find_one({"$and":[{"complex_words":elem[0].upper()},
                                                {"PoS_tag":elem[1]}]}, {"_id":0})
        else:
            found = {'suffix':"NF","complex_words":elem[0],"PoS_tag":"NF","word_PoS":"NF"}
            # contar sufijos y palabras complejas 
            # hacer una distribución con todos los textos 
    if found is not None:
        total_list.append(found)
df_words = pd.DataFrame(total_list)
df_words = df_words[~df_words.isin(['NF']).any(axis=1)]
#df_words.to_csv('found_A2.csv', index=False)
counts_suffix = df_words['suffix'].value_counts()
counts_words = df_words["complex_words"].value_counts()
list_count_words = [f'{index} {count}' for index, count in counts_words.items()]
result = df_words.groupby('suffix').agg({
    'complex_words':lambda x: list(set(x)),
    'PoS_tag': lambda x: list(set(x))
}).reset_index()
result['count_prefix'] = result["suffix"].map(counts_suffix)

mapping = {item.split()[0]: item.split()[1] for item in list_count_words}

def append_numerals(word):
    if isinstance(word, list):  
        return [f"{a} ({mapping.get(a, '')})" for a in word]
    else:  # If it's a single animal
        return f"{word} ({mapping.get(word, '')})"

result["complex_words"] = result["complex_words"].apply(append_numerals)


print(result)
