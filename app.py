from flask import Flask, render_template_string, request, send_file
import os, ezdxf, fitz, pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return """
    <html dir='rtl'><body style='text-align:center; padding-top:50px; font-family:sans-serif;'>
    <h1>منصة الحصر الهندسي</h1>
    <p>ارفع مخططك (DXF أو PDF) وسأقوم بتحويله لملف كميات إكسل.</p>
    <form action='/upload' method='post' enctype='multipart/form-data'>
        <input type='file' name='file' accept='.dxf,.pdf' style='margin:20px;'>
        <br><button type='submit' style='padding:10px 20px;'>بدء المعالجة</button>
    </form>
    </body></html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file: return "الرجاء اختيار ملف", 400
    
    # حفظ الملف مؤقتاً
    ipath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(ipath)
    opath = os.path.join(UPLOAD_FOLDER, "BOQ_" + file.filename.rsplit('.', 1)[0] + ".xlsx")
    
    # المعالجة
    success = run_cad(ipath, opath) if file.filename.lower().endswith('.dxf') else run_pdf(ipath, opath)
    
    if success: 
        return send_file(opath, as_attachment=True)
    return "حدث خطأ أثناء معالجة الملف، تأكد من سلامة صيغته.", 500

def run_cad(ipath, opath):
    try:
        doc = ezdxf.readfile(ipath)
        recs = [{"الطبقة": e.dxf.layer, "نوع العنصر": e.dxftype(), "الكمية": 1} for e in doc.modelspace()]
        pd.DataFrame(recs).to_excel(opath, index=False)
        return True
    except: return False

def run_pdf(ipath, opath):
    try:
        doc = fitz.open(ipath)
        recs = [{"الصفحة": i+1, "المحتوى": "نص مستخرج"} for i in range(len(doc))]
        pd.DataFrame(recs).to_excel(opath, index=False)
        return True
    except: return False

if __name__ == '__main__':
    app.run()
    
