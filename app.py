import re

from flask import Flask, request ,send_file
import pandas as pd
import io
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Home</h1>
    <a href="/store1">Απογραφή</a><br>
    <a href="/store2">Ημερομηνίες</a><br>
    
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
    <form method="GET" action="/download">
    <input type="text" name="filename" placeholder="Όνομα αρχείου">
    <button type="submit">Download</button>
</form>


    <br>

    {result_html}
    '''
@app.route('/download')
def download():
    global system_data, store_data
    filename = request.args.get("filename")
    if not filename:
        filename = "result"
    
    filename += ".xlsx"    
    if system_data is None or store_data is None:
        return "No data"

    merged = pd.merge(system_data, store_data, on='Κωδικός', how='inner')
    merged['Διαφορά'] = merged['Υπόλοιπο'] - merged['ΣΥΝΟΛΟ']

    result = merged[merged['Διαφορά'] != 0]

    output = io.BytesIO()
    result.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=int(os.environ.get("PORT", 5000)))