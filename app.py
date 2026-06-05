from flask import Flask, request, send_file
import os
import ezdxf
import fitz
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return """
    <html dir='rtl'>
    <body style='text-align:center; padding-top:50px; font-family:sans-serif;'>
        <h1>منصة الحصر الهندسي</h1>
        <form action='/upload' method='post' enctype='multipart/form-data'>
            <input type='file' name='file' required>
            <button type='submit'>معالجة الملف</button>
        </form>
    </body>
    </html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "لا يوجد ملف مرفوع", 400
    file = request.files['file']
    if file.filename == '':
        return "لم يتم اختيار ملف", 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # تحديد مسار ملف الإكسل الناتج
    output_path = os.path.join(UPLOAD_FOLDER, "Output_" + file.filename.rsplit('.', 1)[0] + ".xlsx")
    
    # معالجة بسيطة بناءً على نوع الملف
    try:
        if file.filename.lower().endswith('.dxf'):
            doc = ezdxf.readfile(file_path)
            # استخراج بيانات الطبقات كنموذج أولي للحصر
            data = [{"Layer": e.dxf.layer} for e in doc.modelspace()]
            pd.DataFrame(data).to_excel(output_path, index=False)
        else:
            # معالجة PDF
            doc = fitz.open(file_path)
            data = [{"Page": i+1} for i in range(len(doc))]
            pd.DataFrame(data).to_excel(output_path, index=False)
            
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"حدث خطأ أثناء المعالجة: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
