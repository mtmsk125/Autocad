from flask import Flask, render_template_string, request, send_file
import os
import ezdxf
import fitz
import pandas as pd

app = Flask(__name__)

# هذا السطر ينشئ المجلد تلقائياً إذا لم يكن موجوداً
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return """
    <div style='text-align:center; padding-top:50px; font-family:sans-serif;'>
        <h1>منصة الحصر الهندسي</h1>
        <p>ارفع ملف مخطط (DXF) أو (PDF) لتحويله إلى جدول كميات (Excel).</p>
        <form action='/upload' method='post' enctype='multipart/form-data'>
            <input type='file' name='file' accept='.dxf,.pdf' style='margin:20px;'>
            <br><button type='submit' style='padding:10px 20px; background:#007bff; color:white; border:none; border-radius:5px;'>بدء المعالجة</button>
        </form>
    </div>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return "الرجاء اختيار ملف صالح!", 400
    
    # حفظ الملف داخل المجلد الذي تم إنشاؤه برمجياً
    ipath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(ipath)
    opath = os.path.join(UPLOAD_FOLDER, "BOQ_" + file.filename.rsplit('.', 1)[0] + ".xlsx")
    
    try:
        if file.filename.lower().endswith('.dxf'):
            doc = ezdxf.readfile(ipath)
            recs = [{"الطبقة": e.dxf.layer, "نوع العنصر": e.dxftype()} for e in doc.modelspace()]
            pd.DataFrame(recs).to_excel(opath, index=False)
            return send_file(opath, as_attachment=True)
        else:
            doc = fitz.open(ipath)
            recs = [{"الصفحة": i+1, "المحتوى": "نص مستخرج"} for i in range(len(doc))]
            pd.DataFrame(recs).to_excel(opath, index=False)
            return send_file(opath, as_attachment=True)
    except Exception as e:
        return f"حدث خطأ أثناء المعالجة: {str(e)}", 500

if __name__ == '__main__':
    app.run()
    
