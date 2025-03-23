import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os
import treetaggerwrapper
from flask import Flask, render_template, jsonify, request
import pandas as pd
from pymongo import MongoClient

conn_str = "mongodb+srv://itecidb2:iteci2021@clusteriteci.rnxhk.mongodb.net/"
#conn_str = 'mongodb://localhost:27017/'
client = MongoClient(conn_str)
db = client['db_perfilador']
col_nouns = db['nouns_collection']
col_verbs = db['verbs_collection']
os.environ['TAGDIR'] = '/app/treetagger'
my_tagdir = os.getenv('TAGDIR')
if not my_tagdir:
    raise EnvironmentError('Enviroment TAGDIR not set properly')
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR=my_tagdir)

# Función que realiza el tag a cada palabra del texto, busca en 
# la base de datos de MongoDB y además contabiliza los resultados
def TagAndCount(text_file):
    tags = tagger.tag_file(text_file)
    total_list = []
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
                found = {'suffix':"NF","complex_words":elem[0],
                         "PoS_tag":"NF","word_PoS":"NF"}
        if found is not None:
            total_list.append(found)
    df_words = pd.DataFrame(total_list)
    df_words = df_words[~df_words.isin(['NF']).any(axis=1)]
    counts_suffix = df_words['suffix'].value_counts()
    counts_words = df_words["complex_words"].value_counts()
    list_count_words = [f'{index} {count}' for index, count in counts_words.items()]
    result = df_words.groupby('suffix').agg({
                                            'complex_words':lambda x: list(set(x)),
                                            'PoS_tag': lambda x: list(set(x))
                                            }).reset_index()
    result['count_suffix'] = result["suffix"].map(counts_suffix)

    mapping = {item.split()[0]: item.split()[1] for item in list_count_words}
    # Subfunción para agregar los valores del conteo al dataframe final
    def append_numerals(word):
        if isinstance(word, list):  
            return [f"{a} ({mapping.get(a, '')})" for a in word]
        else:  # If it's a single animal
            return f"{word} ({mapping.get(word, '')})"
        
    result["complex_words"] = result["complex_words"].apply(append_numerals)
    return result

app = Flask(__name__, template_folder="views/templates", static_folder="views/static")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
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
        file.save(file_path)  # Save file to the upload folder
        file_names.append(filename)  # Collect file names
    return jsonify({'files':file_names})

@app.route('/process/<filename>', methods=['GET'])
def process_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    tager_counter_df = TagAndCount(filepath)
    table_html = tager_counter_df.to_html(index=False)
    return jsonify({'table': table_html})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
