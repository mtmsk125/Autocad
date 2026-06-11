from flask import Flask, request, send_file
import ezdxf, tempfile, os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فاحص DXF</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; text-align: center; }
        .box { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input[type="file"] { margin: 15px 0; }
        button { padding: 12px 30px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .loading { display: none; margin-top: 20px; font-size: 18px; color: #007bff; }
        .success { margin-top: 20px; }
        .download-btn { background: #28a745; padding: 15px 30px; font-size: 18px; display: inline-block; text-decoration: none; color: white; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🔧 فاحص DXF - إصلاح تلقائي</h2>
        <p>ارفع ملف DXF وسيتم فحصه وإصلاح الأخطاء تلقائياً</p>
        
        <form method="POST" enctype="multipart/form-data" onsubmit="showLoading()">
            <input type="file" name="dxf_file" accept=".dxf" required><br>
            <button type="submit">فحص وإصلاح</button>
        </form>

        <div id="loading" class="loading">
            جاري المعالجة... ⏳<br>
            <small>الرجاء الانتظار</small>
        </div>

        {result}
    </div>

    <script>
    function showLoading() {
        document.getElementById('loading').style.display = 'block';
    }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        try:
            file = request.files['dxf_file']
            if not file:
                result = '<p style="color:red">ارفع ملف DXF</p>'
            else:
                temp_dir = '/tmp'
                filepath = os.path.join(temp_dir, file.filename)
                file.save(filepath)

                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace
