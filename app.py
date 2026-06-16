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
    fixed_filename = ''
    js_pts = []
    
    lang_header = request.headers.get('Accept-Language', '')
    is_ar = 'ar' in lang_header.lower()

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
                        e.close()
                        if len(e) > 0:
                            p = e.get_points()
                            js_pts.append({"x": float(p), "y": float(p)})
                    elif e.dxftype() == 'LINE':
                        errors += 1
                        js_pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
                        msp.add_circle(e.dxf.start, radius=1.0, dxfattribs={'color': 1})

                fixed_filename = 'fixed_' + filename
                doc.saveas(os.path.join('/tmp', fixed_filename))
                os.remove(filepath)

                if is_ar:
                    result = f'''<div id="result-section" class="result-card"><div class="success-icon">✓</div><h3>تم الفحص والإصلاح التلقائي بنجاح!</h3><div class="error-counter">عدد الأخطاء المصلحة: <strong>{{errors}}</strong></div><p class="notice-text">شاهد خريطة الأخطاء المصلحة بالدوائر الحمراء في المعاين بالأسفل 👇</p><button type="button" onclick="openPaymentModal()" class="btn-download">تحميل ملف DXF السليم الآن 🚀</button></div>'''
                else:
                    result = f'''<div id="result-section" class="result-card"><div class="success-icon">✓</div><h3>Scan & Fix Completed!</h3><div class="error-counter">Errors Fixed: <strong>{{errors}}</strong></div><p class="notice-text">See fixed errors highlighted in red circles below 👇</p><button type="button" onclick="openPaymentModal()" class="btn-download">Download Clean DXF Now 🚀</button></div>'''
            else:
                result = '<div class="error-card">⚠️ File error / خطأ في الملف</div>'
        except Exception as e:
            result = f'<div id="result-section" class="error-card">⚠️ Error / خطأ: {str(e)}</div>'

    # قراءة واجهة الموقع الكاملة كملف نصي مباشر لحل مشكلة السيرفر تماماً
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
    except FileNotFoundError:
        return "File index.html missing / ملف الواجهة مفقود", 500

    download_url = f"/download/{{fixed_filename}}" if fixed_filename else "#"
    return render_template_string(html_template, result=result, download_url=download_url, js_pts=str(js_pts), is_ar=is_ar)

if __name__ == '__main__':
    app.run(debug=True)

            

    
