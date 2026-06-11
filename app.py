from flask import Flask, render_template, request, send_file
import ezdxf
import pandas as pd
from fpdf import FPDF
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['dxf_file']
        if not file:
            return "ارفع ملف DXF أولاً"
        
        # مجلد مؤقت عشان Render
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, file.filename)
        file.save(filepath)
        
        errors_found = []
        fixed_entities = []
        
        try:
            doc = e
