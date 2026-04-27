from flask import Flask, request
import pandas as pd
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Home</h1>
    <a href="/store1">Μαγαζί 1</a><br>
    <a href="/store2">Μαγαζί 2</a><br>
    <a href="/store3">Μαγαζί 3</a>
    '''




system_data = None
store_data = None
result_html = ""

@app.route('/store1', methods=['GET', 'POST'])
def store1():
    global system_data, store_data, result_html

    # Upload System
    if request.method == 'POST' and 'system_file' in request.files:
        file = request.files['system_file']
        system_data = pd.read_excel(file)[['Κωδικός', 'Όνομα', 'Υπόλοιπο']]

    # Upload Store
    if request.method == 'POST' and 'store_file' in request.files:
        file = request.files['store_file']
        store_data = pd.read_excel(file)[['Κωδικός', 'ΣΥΝΟΛΟ']]

    # Compare
    if request.method == 'POST' and 'compare' in request.form:
        if system_data is not None and store_data is not None:

            merged = pd.merge(system_data, store_data, on='Κωδικός', how='inner')
            merged['Διαφορά'] = merged['Υπόλοιπο'] - merged['ΣΥΝΟΛΟ']

            result = merged[merged['Διαφορά'] != 0]

            result_html = result.to_html(index=False)

    return f'''
    <h1>Store 1</h1>

    <h3>System Excel</h3>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="system_file">
        <button type="submit">Upload System</button>
    </form>

    <h3>Store Excel</h3>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="store_file">
        <button type="submit">Upload Store</button>
    </form>

    <br>

    <form method="POST">
        <button name="compare" value="1">Compare</button>
    </form>

    <br>

    {result_html}
    '''
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))