import os
import tempfile
from flask import Flask, request, send_file
import ezdxf
import fitz
import pandas as pd

app = Flask(__name__)
# استخدام المجلد المؤقت للنظام لضمان عدم حدوث خطأ في الكتابة
UPLOAD_FOLDER = tempfile.gettempdir()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files: return "لا يوجد ملف", 400
        file = request.files['file']
        if file.filename == '': return "لم يتم اختيار ملف", 400
        
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        out_path = os.path.join(UPLOAD_FOLDER, "Result.xlsx")
        
        try:
            # معالجة الملفات
            if file.filename.lower().endswith('.dxf'):
                doc = ezdxf.readfile(path)
                data = [{"Layer": e.dxf.layer} for e in doc.modelspace()]
            else:
                doc = fitz.open(path)
                data = [{"Page": i+1} for i in range(len(doc))]
            
            pd.DataFrame(data).to_excel(out_path, index=False)
            return send_file(out_path, as_attachment=True)
        except Exception as e:
            return f"خطأ في المعالجة: {str(e)}", 500
            
    return """
    <html dir='rtl'><body>
        <h1>منصة الحصر الهندسي</h1>
        <form method='post' enctype='multipart/form-data'>
            <input type='file' name='file' accept='.dxf,.pdf'>
            <input type='submit' value='بدء المعالجة'>
        </form>
    </body></html>
    """

if __name__ == '__main__':
    app.run()
                
