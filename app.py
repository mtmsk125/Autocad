from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 1. المسار الرئيسي للموقع (الصفحة الرئيسية)
@app.route('/')
def index():
    return render_template('index.html')

# 2. مسار صفحة شروط الخدمة الإلزامية
@app.route('/terms')
def terms():
    return render_template('terms.html')

# 3. مسار صفحة سياسة الخصوصية الإلزامية
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# 4. مسار صفحة سياسة الاسترداد الإلزامية
@app.route('/refund')
def refund():
    return render_template('refund.html')

# 5. مسار صفحة اتصل بنا (الدعم الفني)
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 6. مسار معالجة ورفع ملفات الـ DXF (مثال برمجى مبسط بناءً على مشروعك)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        # هنا يتم وضع منطق فحص وتصليح ملف الـ DXF الخاص بك
        return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
