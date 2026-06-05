import os
from flask import Flask, request, send_file

app = Flask(__name__)

# إنشاء المجلد تلقائياً عند التشغيل
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return """
    <html><body>
        <h1>منصة الحصر الهندسي</h1>
        <form action='/upload' method='post' enctype='multipart/form-data'>
            <input type='file' name='file'>
            <button type='submit'>معالجة الملف</button>
        </form>
    </body></html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file: return "الرجاء اختيار ملف", 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    # هنا سيتم لاحقاً إضافة كود المعالجة (الآن نقوم بالتأكد من الرفع)
    return "تم رفع الملف بنجاح!"

if __name__ == '__main__':
    # يعمل على المنفذ الذي يحدده Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
