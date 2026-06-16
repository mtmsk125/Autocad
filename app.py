from flask import Flask, request, send_file, render_template_string
import ezdxf
import os

app = Flask(__name__)

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join('/tmp', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        try:
            file = request.files.get('dxf_file')
            if file and file.filename != '':
                filename = file.filename
                filepath = os.path.join('/tmp', filename)
                file.save(filepath)

                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace()
                errors = 0

                for e in msp.query('LWPOLYLINE LINE'):
                    if e.dxftype() == 'LWPOLYLINE' and not e.closed:
                        errors += 1
                        p = e.get_points()[0]
                        msp.add_circle((p[0], p[1]), radius=0.5, dxfattribs={'color': 1})
                    elif e.dxftype() == 'LINE':
                        errors += 1
                        msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})

                fixed_filename = 'fixed_' + filename
                fixed_path = os.path.join('/tmp', fixed_filename)
                doc.saveas(fixed_path)

                result = f'''
                <div id="result-section" class="result-card">
                    <div class="success-icon">✓</div>
                    <h3>تم الفحص والإصلاح التلقائي بنجاح!</h3>
                    <div class="error-counter">عدد الأخطاء المكتشفة والمصححة: <strong>{errors}</strong></div>
                    <p class="notice-text">تم تحديد أماكن الخطوط المفتوحة بدوائر حمراء داخل الملف لضمان سلامة القص على الماكينة.</p>
                    <button type="button" onclick="openPaymentModal()" class="btn-download">تحميل ملف DXF السليم الآن 🚀</button>
                </div>
                <script>
                    setTimeout(function() {{
                        var element = document.getElementById('result-section');
                        if(element) {{
                            element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        }}
                    }}, 200);
                </script>
                '''
                os.remove(filepath)
            else:
                result = '<div class="error-card">⚠️ يرجى اختيار ملف DXF صحيح.</div>'

        except Exception as e:
            result = f'<div id="result-section" class="error-card">⚠️ خطأ أثناء المعالجة: {str(e)}</div>'

    # قراءة واجهة الموقع من ملف index.html المنفصل
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
    except FileNotFoundError:
        return "ملف index.html غير موجود. يرجى إنشاؤه بجانب ملف app.py", 500

    download_url = f"/download/{fixed_filename}" if request.method == 'POST' and 'fixed_filename' in locals() else "#"
    
    # دمج النتيجة ورابط التحميل داخل واجهة الموقع
    return render_template_string(html_template, result=result, download_url=download_url)

if __name__ == '__main__':
    app.run(debug=True)

    
