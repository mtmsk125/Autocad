import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return "تم استلام الملف بنجاح"
    
    return """
    <html dir='rtl'><body>
        <h1>منصة الحصر الهندسي - الموقع يعمل!</h1>
        <form method='post' enctype='multipart/form-data'>
            <input type='file' name='file'>
            <input type='submit' value='رفع الملف'>
        </form>
    </body></html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
