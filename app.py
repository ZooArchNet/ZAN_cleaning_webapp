from flask import Flask
from flask_cors import CORS
from flask import request
from flask import render_template, redirect, send_file
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('clean.html')

@app.route('/clean', methods=['POST'])
def clean_file():

    verbatim_name = request.form.get('verbatim-name')
    verbatim_element = request.form.get('verbatim-element')
    element_id = request.form.get('element-id')

    file = request.files['file']

    mimetype = file.content_type
    
    if mimetype == 'text/csv' or mimetype == 'application/vnd.ms-excel':
      df = pd.read_csv(file)
    else:
      df = pd.read_excel(file)

    if verbatim_name:
      df=df.assign(scientificName = "")
      names = pd.read_csv("./mapping_files/scientific_names.csv", index_col = False)
      name_dict = names.set_index('old_names').to_dict()['cleaned_names']

      def clean_name(name): 
        """Matches verbatimScientificName to cleaned scientificName with dictionary"""
        if name in name_dict.values():
          return name
        elif name in name_dict.keys():
          return name_dict[name]
        else:
          return ""
    
      df["scientificName"] = df["verbatimScientificName"].apply(clean_name) 


    if verbatim_element:
      df=df.assign(element = "")
      elements = pd.read_csv("./mapping_files/element_names.csv", index_col = False)
      element_dict = elements.set_index('old_elements').to_dict()['cleaned_elements']

      def clean_element(element): 
        """Matches verbatimElement to cleaned element with dictionary"""
        if element in element_dict.values():
          return element
        elif element in element_dict.keys():
          return element_dict[element]
        else:
          return ""
    
      df["element"] = df["verbatimElement"].apply(clean_element)

    if element_id:
      df=df.assign(elementID = "")
      id_dict = elements.set_index('cleaned_elements').to_dict()['element_ID']

      def add_ID(element): 
        """Matches element to UBERON element ID with dictionary"""
        if element in id_dict.keys():
          return id_dict[element]
        else:
         return ""

      df["elementID"] = df["element"].apply(add_ID)
      
    redirect('http://localhost:5000')
    if mimetype == 'text/csv' or mimetype == 'application/vnd.ms-excel':
      df.to_csv('./data.csv')
      return send_file('./data.csv',
                     mimetype='text/csv',
                     attachment_filename='data.csv',
                     as_attachment=True)
    else:
      df.to_excel('./data.xlsx')
      return send_file('./data.xlsx',
                     mimetype='text/xlsx',
                     attachment_filename='data.xlsx',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
