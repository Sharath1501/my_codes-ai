# app.py
from flask import Flask, render_template, request
import pandas as pd
from ml_model import random_forest_classification

app = Flask(__name__)

def get_results_classification(df):
    rf_result = random_forest_classification(df)

    
    results = {
        'Random Forest Classifier': {
            'accuracy': rf_result[0],
            'classification_report_str': rf_result[1]
        }
        
    }

    return results

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            results = get_results_classification(df)
            return render_template('result_classification.html', results=results)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

