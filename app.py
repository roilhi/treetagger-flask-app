import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os
import treetaggerwrapper
from flask import Flask, render_template, jsonify, request
import pandas as pd
from pymongo import MongoClient

# MongoDB connection
conn_str = "mongodb+srv://itecidb2:iteci2021@clusteriteci.rnxhk.mongodb.net/"
client = MongoClient(conn_str)
db = client['db_perfilador']
col_nouns = db['nouns_collection']
col_verbs = db['verbs_collection']
col_adjectives = db['adjectives_collection']
col_adverbs = db['adverbs_collection']

# TreeTagger setup
os.environ['TAGDIR'] = '/app/treetagger'
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR=os.getenv('TAGDIR'))
if not os.getenv('TAGDIR'):
    raise EnvironmentError('Environment TAGDIR not set properly')

# Optimized TagAndCount function
def TagAndCount(text_file):
    tags = tagger.tag_file(text_file)
    tagged_text = []
    total_list = []

    # Build noun/verb lookup sets
    noun_keys = set()
    verb_keys = set()
    adjective_keys = set()
    adverb_keys = set()
    parsed_tags = []

    for tag in tags:
        elem = tag.split('\t')
        if len(elem) == 3:
            word, pos = elem[0].upper(), elem[1]
            parsed_tags.append((word, pos, elem[0]))  # (upper_word, PoS, original_word)
            if pos.startswith("N"):
                noun_keys.add((word, pos))
            elif pos.startswith("V"):
                verb_keys.add((word, pos))
            elif pos.startswith("JJ"):
                adjective_keys.add((word, pos))
            elif pos.startswith("RB"):
                adverb_keys.add((word,pos)) 

    # Perform bulk queries
    noun_docs = list(col_nouns.find({"$or": [{"complex_words": w, "PoS_tag": p} for w, p in noun_keys]}, {"_id": 0}))
    verb_docs = list(col_verbs.find({"$or": [{"complex_words": w, "PoS_tag": p} for w, p in verb_keys]}, {"_id": 0}))
    adjective_docs = list(col_adjectives.find({"$or": [{"complex_words": w, "PoS_tag": p} for w, p in adjective_keys]}, {"_id": 0}))
    adverb_docs = list(col_adverbs.find({"$or": [{"complex_words": w, "PoS_tag": p} for w, p in adverb_keys]}, {"_id": 0}))

    # Create lookup dictionary
    lookup = {(doc["complex_words"], doc["PoS_tag"]): 
              doc for doc in noun_docs + verb_docs + adjective_docs + adverb_docs}

    for word_upper, pos, original_word in parsed_tags:
        found = lookup.get((word_upper, pos))
        if found:
            total_list.append(found)
            tagged_text.append(f"{found['complex_words']}_{found['PoS_tag']}_<{found['suffix']}>")
        else:
            tagged_text.append(f"{original_word}_{pos}_<NF>")

    # Prepare DataFrame and statistics
    df_words = pd.DataFrame(total_list)
    df_words = df_words[~df_words.isin(['NF']).any(axis=1)]
    counts_suffix = df_words['suffix'].value_counts()
    counts_words = df_words["complex_words"].value_counts()
    list_count_words = [f'{index} {count}' for index, count in counts_words.items()]
    mapping = {item.split()[0]: item.split()[1] for item in list_count_words}

    def append_numerals(word):
        if isinstance(word, list):  
            return [f"{a} ({mapping.get(a, '')})" for a in word]
        return f"{word} ({mapping.get(word, '')})"

    result = df_words.groupby('suffix').agg({
        'complex_words': lambda x: list(set(x)),
        'PoS_tag': lambda x: list(set(x))
    }).reset_index()
    # NEW COLUMN: count how many complex words are in the list
    result['count types'] = result["complex_words"].apply(
        lambda x: len(x) if isinstance(x, list) else 1
    )

    result["complex_words"] = result["complex_words"].apply(append_numerals)
    result['count_suffix'] = result["suffix"].map(counts_suffix)
    
    return result, tagged_text

# Flask setup
app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('files')
    file_names = []
    for file in uploaded_files:
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        file_names.append(filename)
    return jsonify({'files': file_names})

@app.route('/process/<filename>', methods=['GET'])
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    tager_counter_df, tagged_list_text = TagAndCount(filepath)
    table_html = tager_counter_df.to_html(index=False)
    return jsonify({'table': table_html, 'tag_list': tagged_list_text})

@app.route('/suff_table')
def suff_table():
    return render_template('suff_table.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
