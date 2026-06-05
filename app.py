import os
import tempfile
from flask import Flask, request, send_file, render_template_string
import ezdxf
import pandas as pd
from fpdf import FPDF
import zipfile

app = Flask(__name__)
TEMP_DIR = tempfile.gettempdir()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl"><head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{background:#f8f9fa; padding-top:50px;}</style></head><body>
<div class="container text-center">
    <h1>نظام الحصر الهندسي المتكامل</h1>
    <form method='post' enctype='multipart/form-data' class="mt-4">
        <input type='file' name='file' class="form-control mb-3" accept='.dxf' required>
        <button type='submit' class="btn btn-primary btn-lg">بدء المعالجة واستخراج التقارير</button>
    </form>
</div></body></html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        path = os.path.join(TEMP_DIR, file.filename)
        file.save(path)
        
        # 1. التدقيق البصري (إضافة دوائر للأخطاء)
        doc = ezdxf.readfile(path)
        msp = doc.modelspace()
        errors = []
        for e in msp:
            if e.dxftype() == 'LWPOLYLINE' and not e.closed:
                msp.add_circle(e.get_point_at(0), radius=0.5, dxfattribs={'color': 1})
                errors.append({'خطأ': 'غير مغلق', 'موقع': str(e.get_point_at(0))})
        
        marked_dxf = os.path.join(TEMP_DIR, "Checked_" + file.filename)
        doc.saveas(marked_dxf)
        
        # 2. إنشاء الإكسل
        excel_path = os.path.join(TEMP_DIR, "Report.xlsx")
        pd.DataFrame(errors).to_excel(excel_path)
        
        # 3. إنشاء الـ PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Project Report", ln=True, align='C')
        pdf.output(os.path.join(TEMP_DIR, "Report.pdf"))
        
        return "تمت المعالجة. <br> <a href='/download_dxf'>تحميل ملف الأوتوكاد المصحح</a> <br> <a href='/download_excel'>تحميل الإكسل</a> <br> <a href='/download_pdf'>تحميل تقرير الـ PDF</a>"
    return render_template_string(HTML_PAGE)

@app.route('/download_dxf')
def download_dxf(): return send_file(os.path.join(TEMP_DIR, "Checked_file.dxf"), as_attachment=True)
@app.route('/download_excel')
def download_excel(): return send_file(os.path.join(TEMP_DIR, "Report.xlsx"), as_attachment=True)
@app.route('/download_pdf')
def download_pdf(): return send_file(os.path.join(TEMP_DIR, "Report.pdf"), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        
