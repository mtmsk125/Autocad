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

        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, file.filename)
        file.save(filepath)

        errors_found = []

        try:
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()

            for e in msp.query('LWPOLYLINE LINE ARC'):
                if e.dxftype() == 'LWPOLYLINE':
                    if not e.closed:
                        errors_found.append(f"خط متعدد مفتوح - Layer: {e.dxf.layer}")
                        first_point = e.get_points()[0]
                        msp.add_circle(first_point, radius=0.5, dxfattribs={'color': 1})

                elif e.dxftype() == 'LINE':
                    errors_found.append(f"خط مفرد - Layer: {e.dxf.layer}")
                    msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})

            fixed_path = os.path.join(temp_dir, 'fixed_' + file.filename)
            doc.saveas(fixed_path)

            df = pd.DataFrame(errors_found, columns=['الأخطاء'])
            excel_path = os.path.join(temp_dir, 'report.xlsx')
            df.to_excel(excel_path, index=False)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', size=12)
            pdf.cell(200, 10, txt=f"عدد الأخطاء: {len(errors_found)}", ln=True)
            pdf_path = os.path.join(temp
