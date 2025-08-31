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

def TagAndCount(text_file):
    import re
    import pandas as pd
    from collections import Counter

    tags = tagger.tag_file(text_file)
    tagged_text = []

    # Parse text into word_upper, pos, original_word
    parsed_tags = []
    noun_keys, verb_keys, adjective_keys, adverb_keys = set(), set(), set(), set()
    for tag in tags:
        elem = tag.split('\t')
        if len(elem) == 3:
            word_upper, pos, word_orig = elem[0].upper(), elem[1], elem[0]
            parsed_tags.append((word_upper, pos, word_orig))
            if pos.startswith("N"):
                noun_keys.add((word_upper, pos))
            elif pos.startswith("V"):
                verb_keys.add((word_upper, pos))
            elif pos.startswith("JJ"):
                adjective_keys.add((word_upper, pos))
            elif pos.startswith("RB"):
                adverb_keys.add((word_upper, pos))

    # Count occurrences per word+PoS in text
    word_pos_counter = Counter((w, pos) for w, pos, _ in parsed_tags)

    # Helper function to process a single collection
    def process_collection(keys, collection):
        if not keys:
            return pd.DataFrame(columns=['suffix', 'PoS_tag', 'complex_words', 'fine_pos_tags',
                                         'count_complex_words', 'sum_numerals'])
        docs = list(collection.find(
            {"$or": [{"complex_words": w, "PoS_tag": p} for w, p in keys]},
            {"_id": 0}
        ))
        if not docs:
            return pd.DataFrame(columns=['suffix', 'PoS_tag', 'complex_words', 'fine_pos_tags',
                                         'count_complex_words', 'sum_numerals'])

        df = pd.DataFrame(docs)

        # Append numerals based on word+PoS occurrences in the text
        df['complex_words_num'] = df.apply(
            lambda r: f"{r['complex_words']} ({word_pos_counter.get((r['complex_words'].upper(), r['PoS_tag']),0)})", axis=1
        )
        return df

    # Process each collection
    df_nouns = process_collection(noun_keys, col_nouns)
    df_verbs = process_collection(verb_keys, col_verbs)
    df_adjectives = process_collection(adjective_keys, col_adjectives)
    df_adverbs = process_collection(adverb_keys, col_adverbs)

    # Concatenate all tables
    df_all = pd.concat([df_nouns, df_verbs, df_adjectives, df_adverbs], ignore_index=True)

    # Map fine PoS → coarse family
    pos_map = {
        "NN": "NN", "NNS": "NN",
        "JJ": "JJ", "JJR": "JJ", "JJS": "JJ",
        "VV": "VV", "VVD": "VV", "VVG": "VV", "VVN": "VV", "VVP": "VV", "VVZ": "VV",
        "RB": "RB", "RBR": "RB", "RBS": "RB"
    }
    df_all['CoarsePoS'] = df_all['PoS_tag'].map(pos_map).fillna(df_all['PoS_tag'])

    # Group by suffix + coarse PoS, merge words and fine PoS tags
    df_grouped = df_all.groupby(['suffix', 'CoarsePoS']).agg({
        'complex_words_num': lambda x: sorted(set(x)),
        'PoS_tag': lambda x: sorted(set(x))  # Collect fine PoS tags
    }).reset_index()

    df_grouped['count_complex_words'] = df_grouped['complex_words_num'].apply(len)
    df_grouped['sum_numerals'] = df_grouped['complex_words_num'].apply(
        lambda lst: sum(int(m.group(1)) for w in lst if (m := re.search(r'\((\d+)\)', w)))
    )

    df_grouped = df_grouped.rename(columns={
        'CoarsePoS': 'PoS_tag',
        'complex_words_num': 'complex_words',
        'PoS_tag': 'fine_pos_tags'
    })

    # Sort by PoS order and suffix
    pos_order = ["NN", "JJ", "VV", "RB", "NF"]
    pos_rank = {tag: i for i, tag in enumerate(pos_order)}
    df_grouped['__pos_rank'] = df_grouped["PoS_tag"].map(pos_rank).fillna(len(pos_order))
    result = df_grouped.sort_values(by=["__pos_rank", "suffix"]).drop(columns=["__pos_rank"]).reset_index(drop=True)

    # Build tagged_text with correct counts per word+PoS
    all_docs = list(col_nouns.find({}, {"_id": 0})) + \
               list(col_verbs.find({}, {"_id": 0})) + \
               list(col_adjectives.find({}, {"_id": 0})) + \
               list(col_adverbs.find({}, {"_id": 0}))
    lookup = {(doc["complex_words"], doc["PoS_tag"]): doc for doc in all_docs}

    for word_upper, pos, word_orig in parsed_tags:
        count = word_pos_counter.get((word_upper, pos), 0)
        if (word_upper, pos) in lookup:
            tagged_text.append(f"{word_orig}_{pos}_<{count}>")
        else:
            tagged_text.append(f"{word_orig}_{pos}_<NF>")

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
