from flask import Flask, render_template, request, redirect, session, url_for, g, send_from_directory
from pdf_annotate import PdfAnnotator, Location, Appearance
import PyPDF2
import re
import boto3
import json
import os
import fitz


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'uploads/')
app = Flask(__name__)
app.secret_key = 'secretkey'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/load', methods=['POST', 'GET'])
def load():
    file1 = request.files['SpecFile']
    file2 = request.files['jsonFile']
    filename1 = file1.filename
    filename2 = file2.filename
    pdf_dest = "/".join([target, filename1])
    json_dest = "/".join([target, filename2])
    file1.save(pdf_dest)
    file2.save(json_dest)
    session['pdf_dest'] = pdf_dest
    session['json_dest'] = json_dest
    my_dic = {}
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        count = 0
        for entity in myfile['entities']:
            count = count+1
            for annot in myfile['annotations']:
                if entity['entity_id'] == annot['entity_id']:
                    my_dic[entity['entity_name']] = annot['words']
    return render_template("index.html", content=file1.filename, output=my_dic, entity_count=count)


@app.route('/load/<filename>')
def send_pdf(filename):
    return send_from_directory("uploads", filename)


@app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    if 'pdf_dest' in session:
        pdf_dest = session['pdf_dest']
    if 'json_dest' in session:
        json_dest = session['json_dest']

    a = PdfAnnotator(pdf_dest)
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        for annot in myfile['annotations']:
            pageNo = annot['page']
        x1, y1, x2, y2 = annot['bounding_box']
        a.add_annotation(
            'square',
            Location(x1=x1+150, y1=y1+150, x2=x2 *
                     300, y2=y2*300, page=pageNo),
            Appearance(stroke_color=(1, 0, 0), stroke_width=2),
        )
        output = a.write('Ann_output.pdf')
    my_dic = {}
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        for entity in myfile['entities']:
            for annot in myfile['annotations']:
                if entity['entity_id'] == annot['entity_id']:
                    my_dic[entity['entity_name']] = annot['words']
    return render_template("Annotation.html", content="Ann_output.pdf", output=my_dic)


@app.route('/annotate/<filename>')
def send_Apdf(filename):
    return send_from_directory("/", filename)


@app.route('/SearchText', methods=['GET', 'POST'])
def SearchText():
    if 'pdf_dest' in session:
        pdf_dest = session['pdf_dest']
    if 'json_dest' in session:
        json_dest = session['json_dest']

    doc = fitz.open(pdf_dest)
    for page in doc:
        text = request.form['text']
        text_instances = page.searchFor(text)
        for inst in text_instances:
            highlight = page.addHighlightAnnot(inst)
            highlight.update()
    out_pdf = "/".join([target, "output.pdf"])
    doc.save(out_pdf, garbage=4, deflate=True, clean=True)
    my_dic = {}
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        for entity in myfile['entities']:
            for annot in myfile['annotations']:
                if entity['entity_id'] == annot['entity_id']:
                    my_dic[entity['entity_name']] = annot['words']
    return render_template("result.html", content="output.pdf", output=my_dic)


@app.route('/SearchText/<filename>')
def send_Spdf(filename):
    return send_from_directory("uploads", filename)


@app.route('/uploads3', methods=['GET', 'POST'])
def uploads3():
    s3 = boto3.resource('s3')
    s3.Bucket('specification-upload').put_object(Key='spec',
                                                 Body=request.files['inputFile'])
    return "<h1>File saved to S3</h1>"


if __name__ == "__main__":
    app.run(debug=True)


''' @app.route('/entites', methods=['GET', 'POST'])
def entites():
    file = request.files['jsonFile']
    filename = file.filename
    json_dest = "/".join([target, filename])
    session['json_dest'] = json_dest
    file.save(json_dest)
    file_path = os.path.join(json_dest, filename)
    my_dic = {}
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        for entity in myfile['entities']:
            for annot in myfile['annotations']:
                if entity['entity_id'] == annot['entity_id']:
                    my_dic[entity['entity_name']] = annot['words']
    return render_template("index.html", output=my_dic)
 '''
''' 
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1, username='anilbabu', password='123'))
users.append(User(id=2, username='Becca', password='secret'))
users.append(User(id=3, username='Carlos', password='somethingsimple'))



@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('index.html') '''
''' @app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    if 'pdf_dest' in session:
        pdf_dest = session['pdf_dest']
    if 'json_dest' in session:
        json_dest = session['json_dest']
    doc = fitz.open(pdf_dest)
    my_dic = {}
    with open(json_dest, 'r') as output:
        myfile = json.load(output)
        for entity in myfile['entities']:
            for annot in myfile['annotations']:
                if entity['entity_id'] == annot['entity_id']:
                    my_dic[entity['entity_name']] = annot['words']
    dic_keys = list(my_dic.values())
    for page in doc:
        for i in dic_keys:
            text = i
            text_instances = page.searchFor(text)
            for inst in text_instances:
                highlight = page.addHighlightAnnot(inst)
                highlight.update()
    out_pdf = "/".join([target, "ann_output.pdf"])
    doc.save(out_pdf, garbage=4, deflate=True, clean=True)
    return send_from_directory("uploads", "ann_output.pdf") '''
