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
                            p = e.get_points()[0]
                            js_pts.append({"x": float(p[0]), "y": float(p[1])})
                    elif e.dxftype() == 'LINE':
                        errors += 1
                        js_pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
                        msp.add_circle(e.dxf.start, radius=1.0, dxfattribs={'color': 1})

                fixed_filename = 'fixed_' + filename
                doc.saveas(os.path.join('/tmp', fixed_filename))
                os.remove(filepath)

                if is_ar:
                    result = f'<div id="result-section" class="result-card"><div class="success-icon">✓</div><h3>تم الفحص والإصلاح بنجاح!</h3><div class="error-counter">عدد الأخطاء المصلحة: <strong>{errors}</strong></div><p class="notice-text">شاهد خريطة الأخطاء المصلحة بالأسفل 👇</p><button type="button" onclick="openPaymentModal()" class="btn-download">تحميل ملف DXF السليم 🚀</button></div>'
                else:
                    result = f'<div id="result-section" class="result-card"><div class="success-icon">✓</div><h3>Scan & Fix Completed!</h3><div class="error-counter">Errors Fixed: <strong>{errors}</strong></div><p class="notice-text">See fixed errors highlighted below 👇</p><button type="button" onclick="openPaymentModal()" class="btn-download">Download Clean DXF 🚀</button></div>'
            else:
                result = '<div class="error-card">⚠️ File error</div>'
        except Exception as e:
            result = f'<div class="error-card">⚠️ Error: {str(e)}</div>'

    # قراءة ملف index.html المستقل والمتواجد بجانب الكود الرئيسي مباشرة
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
    except FileNotFoundError:
        return "File index.html missing / ملف الواجهة مفقود في المسار الرئيسي", 500

    download_url = f"/download/{fixed_filename}" if fixed_filename else "#"
    
    # دمج البيانات مع الواجهة المستقلة وتخصيص النصوص بالكامل
    html_template = html_template.replace('USE_RESULT', result)
    html_template = html_template.replace('USE_DOWNLOAD_URL', download_url)
    html_template = html_template.replace('USE_JS_PTS', str(js_pts))
    html_template = html_template.replace('USE_DIR', 'rtl' if is_ar else 'ltr')
    html_template = html_template.replace('USE_LANG', 'ar' if is_ar else 'en')
    html_template = html_template.replace('USE_NAV', '🚀 أداة سحابية ذكية لماكينات الـ CNC' if is_ar else '🚀 Smart Cloud Tool for CNC')
    html_template = html_template.replace('USE_H1', 'إصلاح وتنظيف ملفات DXF تلقائياً بضغطة زر' if is_ar else 'Auto-Fix DXF Files Instantly')
    html_template = html_template.replace('USE_P', 'تكتشف منصتنا الأخطاء، وتسد الخطوط المفتوحة، وتجهز ملفك للقص الفوري وبأعلى دقة.' if is_ar else 'Our tool detects errors, closes open loops, and preps your file.')
    html_template = html_template.replace('USE_LBL', 'اسحب ملف DXF هنا أو اضغط للتصفح' if is_ar else 'Drag & Drop DXF file here')
    html_template = html_template.replace('USE_BTN', 'ابدأ الفحص والإصلاح التلقائي الآن' if is_ar else 'Start Auto-Scan & Repair Now')
    html_template = html_template.replace('USE_MH3', '🔓 خطوة واحدة لتحميل ملفك الجاهز' if is_ar else '🔓 One Step to Download Your File')
    html_template = html_template.replace('USE_MP', 'يرجى تحويل مبلغ 1 دينار أردني فقط عبر كليك لتفعيل التنزيل:' if is_ar else 'Please transfer 1 JOD via instant CliQ to unlock:')
    html_template = html_template.replace('USE_VLBL', 'أدخل اسم المحوِّل للتأكيد والتنزيل:' if is_ar else 'Enter sender name to verify:')
    html_template = html_template.replace('USE_VPH', 'مثال: محمد أحمد' if is_ar else 'e.g., John Doe')
    html_template = html_template.replace('USE_VBTN', 'تأكيد وتحميل الملف فوراً 📥' if is_ar else 'Verify & Download Instantly 📥')
    html_template = html_template.replace('USE_F1H', '⚡ إصلاح تلقائي فوري' if is_ar else '⚡ Instant Auto-Repair')
    html_template = html_template.replace('USE_F1P', 'الخوارزمية تكتشف الخطوط المفتوحة وتقوم بإغلاقها تلقائياً.' if is_ar else 'The algorithm automatically detects and seals open loops.')
    html_template = html_template.replace('USE_F2H', '🎯 تحديد دقيق للأخطاء' if is_ar else '🎯 Precise Error Tracking')
    html_template = html_template.replace('USE_F2P', 'يتم رسم دوائر منبّهة حول أماكن المشاكل لتسهيل فحصها البصري.' if is_ar else 'Red alert circles are highlighted around problematic vectors.')
    html_template = html_template.replace('USE_FOOTER', 'جميع الحقوق محفوظة © 2026 منصة DXF Fixer - الأردن.' if is_ar else 'All Rights Reserved © 2026 DXF Fixer.')
    html_template = html_template.replace('USE_ALIGN', 'right' if is_ar else 'left')

    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True)
