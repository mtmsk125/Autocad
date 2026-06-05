import os
from flask import Flask, request, send_file
import ezdxf
import fitz
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            if file.filename.endswith('.dxf'):
                doc = ezdxf.readfile(path)
                data = [{"Layer": e.dxf.layer} for e in doc.modelspace()]
            else:
                doc = fitz.open(path)
                data = [{"Page": i+1} for i in range(len(doc))]
            
            pd.DataFrame(data).to_excel(out_path, index=False)
            return send_file(out_path, as_attachment=True)
        except Exception as e:
            return str(e), 500
            
    return """
    <html dir='rtl'><body>
        <h1>منصة الحصر الهندسي</h1>
        <form method='post' enctype='multipart/form-data'>
            <input type='file' name='file'>
            <input type='submit' value='معالجة الملف'>
        </form>
    </body></html>
    """

if __name__ == '__main__':
    # لا تقم بتشغيل app.run() مباشرة في الإنتاج، gunicorn سيتولى ذلك
    app.run()
            
