from flask import Flask, request, send_file, render_template_string
import ezdxf, os
app = Flask(__name__)
@app.route('/download/<filename>')
def download(filename):
    p = os.path.join('/tmp', filename)
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("Not found", 404)
@app.route('/', methods=['GET', 'POST'])
def index():
    res, f_name, pts = '', '', []
    is_ar = 'ar' in request.headers.get('Accept-Language', '').lower()
    if request.method == 'POST' or 'test_mode' in request.args:
        try:
            if 'test_mode' in request.args:
                f_name = 'test_broken.dxf'
                fpath = os.path.join('/tmp', f_name)
                doc = ezdxf.new('R2000')
                msp = doc.modelspace()
                e1 = msp.add_lwpolyline([(0, 0), (10, 0), (10, 10)])
                e1.closed = False
                doc.saveas(fpath)
            else:
                f = request.files.get('dxf_file')
                if f and f.filename != '':
                    f_name = f.filename
                    fpath = os.path.join('/tmp', f_name)
                    f.save(fpath)
                else: return "No file", 400
            doc = ezdxf.readfile(fpath)
            msp = doc.modelspace()
            err = 0
            for e in msp.query('LWPOLYLINE LINE'):
                if e.dxftype() == 'LWPOLYLINE' and not e.closed:
                    err += 1
                    e.close()
                    points = e.get_points()
                    if points:
                        first_pt = points
                        pts.append({"x": float(first_pt[0]), "y": float(first_pt[1])})
                elif e.dxftype() == 'LINE':
                    err += 1
                    pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
            f_name = 'fixed_' + f_name
            doc.saveas(os.path.join('/tmp', f_name))
            if os.path.exists(fpath): os.remove(fpath)
            if err == 0:
                if is_ar: res = f'<div id="result-section" class="rc"><div class="success-icon">✓</div><h3>ملفك سليم ومثالي 100%!</h3><p class="notice-text" style="color:#15803d;">الملف سليم تماماً وجاهز للقص، يمكنك تحميله مجاناً.</p><a href="/download/{f_name}" class="btn-d" style="display:block; text-decoration:none; line-height:45px; background:#2563eb;">تحميل مجاناً 📥</a></div>'
                else: res = f'<div id="result-section" class="rc"><div class="success-icon">✓</div><h3>Your File is 100% Clean!</h3><a href="/download/{f_name}" class="btn-d" style="display:block; text-decoration:none; line-height:45px; background:#2563eb;">Download Free 📥</a></div>'
            else:
                if is_ar: res = f'<div id="result-section" class="rc"><div class="success-icon" style="background:#f59e0b;">!</div><h3>تم الإصلاح التلقائي بنجاح!</h3><div class="error-counter">الأخطاء المصححة والمغلقة: <strong>{err}</strong></div><button type="button" onclick="openPaymentModal()" class="btn-d">تحميل ملف DXF السليم الآن 🚀</button></div>'
                else: res = f'<div id="result-section" class="rc"><div class="success-icon" style="background:#f59e0b;">!</div><h3>Scan & Auto-Fix Completed!</h3><div class="error-counter">Errors Fixed: <strong>{err}</strong></div><button type="button" onclick="openPaymentModal()" class="btn-d">Download Fixed DXF Now 🚀</button></div>'
        except Exception as e: res = f'<div class="ec">⚠️ Error: {str(e)}</div>'
    d_url = f"/download/{f_name}" if f_name else "#"
    try:
        cd = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cd, 'index.html'), 'r', encoding='utf-8') as f_obj: html = f_obj.read()
    except: return "index.html missing", 500
    p_table = ''
    if is_ar:
        p_table = '''<div class="pricing-container"><h3 class="pricing-title">💎 اختر خطة التحميل والاشتراك لورشتك</h3><div class="pricing-grid">
        <div class="price-card"><h5>الملف الواحد</h5><div class="price">1 د.أ<span>/ ملف</span></div><p>يناسب المصممين العابرين</p><button onclick="openPaymentModal()" class="btn-price">دفع ملف واحد</button></div>
        <div class="price-card popular"><div class="badge">الأكثر طلباً</div><h5>الاشتراك الشهري</h5><div class="price">10 د.أ<span>/ شهرياً</span></div><p>تحميل <strong>ملفات غير محدودة</strong> طوال الشهر</p><a href="https://wa.me شهري" target="_blank" class="btn-price" style="background:var(--p);color:#fff;text-decoration:none;display:block;">اشترك واتساب</a></div>
        <div class="price-card"><h5>الاشتراك السنوي</h5><div class="price">70 د.أ<span>/ سنوياً</span></div><p>وفر 40% واستمتع بخدمة غير محدودة عام كامل</p><a href="https://wa.me سنوي" target="_blank" class="btn-price" style="text-decoration:none;display:block;">تفعيل سنوي</a></div>
        </div></div>'''
    else:
        p_table = '''<div class="pricing-container"><h3 class="pricing-title">💎 Choose Best Plan</h3><div class="pricing-grid">
        <div class="price-card"><h5>Single File</h5><div class="price">$2.00<span>/ file</span></div><button onclick="openPaymentModal()" class="btn-price">Pay per File</button></div>
        <div class="price-card popular"><div class="badge">Popular</div><h5>Monthly Plan</h5><div class="price">$15.00<span>/ mo</span></div><p><strong>Unlimited DXF files</strong></p><a href="https://wa.me" target="_blank" class="btn-price" style="background:var(--p);color:#fff;text-decoration:none;display:block;">Subscribe</a></div>
        <div class="price-card"><h5>Annual Plan</h5><div class="price">$99.00<span>/ yr</span></div><a href="https://wa.me" target="_blank" class="btn-price" style="text-decoration:none;display:block;">Get Annual</a></div>
        </div></div>'''
    t_btn = f'''<div style="margin-top:20px;"><a href="/?test_mode=1" style="color:var(--p);font-weight:600;text-decoration:none;font-size:14px;">{"⚙️ اضغط هنا لتوليد ملف تالف واختبار خريطة الأخطاء والأسعار فوراً" if is_ar else "⚙️ Click here to generate a broken file and test instantly"}</a></div>'''
    html = html.replace('USE_RESULT', res).replace('USE_DOWNLOAD_URL', d_url).replace('USE_JS_PTS', str(pts))
    html = html.replace('USE_DIR', 'rtl' if is_ar else 'ltr').replace('USE_LANG', 'ar' if is_ar else 'en')
    html = html.replace('USE_NAV', '🚀 منصة DXF Fixer الذكية للـ CNC' if is_ar else '🚀 DXF Fixer Platform')
    html = html.replace('USE_H1', 'إصلاح وتنظيف ملفات DXF تلقائياً بضغطة زر' if is_ar else 'Auto-Fix DXF Files Instantly')
    html = html.replace('USE_P', 'تكتشف منصتنا الأخطاء وتجهز ملفك للقص الفوري.' if is_ar else 'Our platform preps your file for cutting.')
    html = html.replace('USE_LBL', 'اسحب ملف DXF هنا أو اضغط للتصفح' if is_ar else 'Drag & Drop DXF file here')
    html = html.replace('USE_BTN', 'ابدأ الفحص والإصلاح تلقائياً' if is_ar else 'Start Auto-Repair')
    html = html.replace('USE_MH3', '🔓 خطوة واحدة لتنزيل ملفك السليم' if is_ar else '🔓 One Quick Step to Download')
    html = html.replace('USE_MP', 'يرجى تحويل قيمة الخدمة (1 دينار محلي / أو $2 للأجانب) عبر كليك لتفعيل التحميل:' if is_ar else 'Please transfer the fee ($2 USD / 1 JOD) via CliQ to unlock:')
    html = html.replace('USE_VLBL', 'أدخل اسم المحوِّل للتأكيد التلقائي والتنزيل:' if is_ar else 'Enter sender name to verify:')
    html = html.replace('USE_VPH', 'مثال: محمد أحمد / 079xxxxxxx' if is_ar else 'e.g., John Doe')
    html = html.replace('USE_VBTN', 'تأكيد وتحميل الملف فوراً 📥' if is_ar else 'Confirm & Download 📥')
    html = html.replace('USE_F1H', '⚡ إصلاح تلقائي فوري' if is_ar else '⚡ Instant Auto-Repair')
    html = html.replace('USE_F1P', 'تغلق الخوارزمية الخطوط المفتوحة في أجزاء من الثانية.' if is_ar else 'Closes open vectors in milliseconds.')
    html = html.replace('USE_F2H', '🎯 خريطة بصرية تفاعلية للأخطاء' if is_ar else '🎯 Precise Visual Map')
    html = html.replace('USE_F2P', 'عرض خريطة تفاعلية تومض باللون الأحمر فوق أماكن المشاكل.' if is_ar else 'Flashing red map over fixed coordinates.')
    html = html.replace('USE_FOOTER', 'جميع الحقوق محفوظة © 2026 منصة DXF Fixer.' if is_ar else 'All Rights Reserved © 2026 DXF Fixer.')
    html = html.replace('USE_ALIGN', 'right' if is_ar else 'left').replace('<!-- PRICING_TABLE_PLACEHOLDER -->', p_table + t_btn)
    return render_template_string(html)
if __name__ == '__main__':
    app.run(debug=True)
