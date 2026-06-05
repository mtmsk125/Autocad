import os
import tempfile
from flask import Flask, request, send_file
import ezdxf
import fitz
import pandas as pd

app = Flask(__name__)
# استخدام المجلد المؤقت للنظام (يسمح Render بالكتابة فيه دائماً)
UPLOAD_FOLDER = tempfile.gettempdir()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file: return "الرجاء اختيار ملف", 400
        
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        out_path = os.path.join(UPLOAD_FOLDER, "Result.xlsx")
        
        try:
            # معالجة الملفات (DXF أو PDF)
            if file.filename.lower().endswith('.dxf'):
                doc = ezdxf.readfile(path)
                data = [{"الطبقة": e.dxf.layer, "النوع": e.dxftype()} for e in doc.modelspace()]
            else:
                doc = fitz.open(path)
                data = [{"الصفحة": i+1} for i in range(len(doc))]
            
            pd.DataFrame(data).to_excel(out_path, index=False)
            return send_file(out_path, as_attachment=True)
        except Exception as e:
            return f"حدث خطأ أثناء المعالجة: {str(e)}", 500
            
    return """
    <html dir='rtl'><body style='text-align:center; padding-top:50px; font-family:sans-serif;'>
        <h1>منصة الحصر الهندسي</h1>
        <form method='post' enctype='multipart/form-data'>
            <input type='file' name='file' accept='.dxf,.pdf' required>
            <br><br><button type='submit' style='padding:10px 20px;'>بدء المعالجة والتحميل</button>
        </form>
    </body></html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
        
