from flask import Flask, request, send_file, render_template_string
import urllib.request, ezdxf, os, sqlite3, datetime

app = Flask(__name__)
DB_PATH = '/tmp/dxf_fixer.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS codes (code TEXT PRIMARY KEY, expires TEXT, owner TEXT)')
        exp = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        conn.execute('INSERT OR IGNORE INTO codes VALUES (?,?,?)', ("MAOWIA_VIP", exp, "ورشة تجريبية"))
init_db()

@app.route('/download/<filename>')
def download(filename):
    p = os.path.join('/tmp', filename)
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("File not found", 404)

@app.route('/admin_moawia', methods=['GET', 'POST'])
def admin():
    msg = ''
    if request.method == 'POST':
        c = request.form.get('code_name', '').strip()
        d = request.form.get('days', '').strip()
        o = request.form.get('owner_name', '').strip()
        if c and d:
            exp = (datetime.datetime.now() + datetime.timedelta(days=int(d))).strftime('%Y-%m-%d')
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('INSERT OR REPLACE INTO codes VALUES (?,?,?)', (c, exp, o))
            msg = f'✓ تم إضافة الكود {c} بنجاح وينتهي بتاريخ {exp}'
            
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute('SELECT * FROM codes').fetchall()
    table_rows = ''.join([f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>' for r in rows])
    return render_template_string(f'''
    <!DOCTYPE html><html dir="rtl"><head><title>لوحة المدير</title><style>body{{font-family:sans-serif;padding:30px;background:#f1f5f9;text-align:center;}}input{{padding:10px;margin:10px;width:80%;max-width:300px;border-radius:6px;border:1px solid #ccc;}}table{{width:100%;max-width:600px;margin:20px auto;background:#fff;border-collapse:collapse;}}th,td{{border:1px solid #ddd;padding:12px;text-align:center;}}th{{background:#1e293b;color:white;}}</style></head><body>
    <h2>🛠️ لوحة تحكم معاوية لإدارة الأكواد والاشتراكات</h2><p style="color:green;font-weight:bold;">{msg}</p>
    <form method="POST">
        <input type="text" name="code_name" placeholder="كود التفعيل (مثال: AHMED_VIP)" required><br>
        <input type="number" name="days" placeholder="عدد أيام الصلاحية (مثال: 30)" required><br>
        <input type="text" name="owner_name" placeholder="اسم صاحب الورشة" required><br>
        <button type="submit" style="padding:10px 20px;background:#2563eb;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">إضافة وتفعيل الكود الآن</button>
    </form>
    <h3>📋 الأكواد الحالية الفعالة</h3>
    <table><tr><th>الكود السرّي</th><th>تاريخ الانتهاء</th><th>اسم المشترك</th></tr>{table_rows}</table>
    <br><a href="/" style="text-decoration:none;color:#64748b;">← العودة لصفحة الفحص الرئيسية</a>
    </body></html>''')

@app.route('/check_promo_api')
def check_promo():
    user_code = request.args.get('code', '').strip()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute('SELECT expires FROM codes WHERE code = ?', (user_code,)).fetchone()
    if row:
        exp_date = datetime.datetime.strptime(row[0], '%Y-%m-%d')
        if datetime.datetime.now() <= exp_date: return "VALID"
    return "INVALID"

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
                    if points and len(points) > 0:
                        pts.append({"x": float(points[0][0]), "y": float(points[0][1])})
                elif e.dxftype() == 'LINE':
                    err += 1
                    pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
            f_name = 'fixed_' + f_name
            doc.saveas(os.path.join('/tmp', f_name))
            if os.path.exists(fpath): os.remove(fpath)
            if err == 0:
                if is_ar: res = f'<div id="result-section" class="rc"><div class="success-icon">✓</div><h3>ملفك سليم ومثالي 100%!</h3><p class="notice-text" style="color:#15803d;">المخطط سليم وجاهز للقص، يمكنك تحميله مجاناً كهدية.</p><a href="/download/{f_name}" class="btn-d" style="display:block; text-decoration:none; line-height:45px; background:#2563eb;">تحميل مجاناً 📥</a></div>'
                else: res = f'<div id="result-section" class="rc"><div class="success-icon">✓</div><h3>Your File is Clean!</h3><a href="/download/{f_name}" class="btn-d" style="display:block; text-decoration:none; line-height:45px; background:#2563eb;">Download Free 📥</a></div>'
            else:
                if is_ar: res = f'<div id="result-section" class="rc"><div class="success-icon" style="background:#f59e0b;">!</div><h3>تم الإصلاح التلقائي بنجاح!</h3><div class="error-counter">الأخطاء المصلحة: <strong>{err}</strong></div><button type="button" onclick="openPaymentModal()" class="btn-d">تحميل ملف DXF السليم الآن 🚀</button></div>'
                else: res = f'<div id="result-section" class="rc"><div class="success-icon" style="background:#f59e0b;">!</div><h3>Scan Completed!</h3><div class="error-counter">Errors Fixed: <strong>{err}</strong></div><button type="button" onclick="openPaymentModal()" class="btn-d">Download Fixed DXF Now 🚀</button></div>'
        except Exception as e: res = f'<div class="ec">⚠️ Error: {str(e)}</div>'
    
    # استدعاء آمن ومحمي 100% للواجهة الفخمة والمكتملة بالكامل من السيرفر السحابي لمنع القص للأبد
    try:
        req = urllib.request.Request("https://pastebin.com", headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
    except:
        return "Server Template Missing / خطأ في تحميل الواجهة", 500

    d_url = f"/download/{f_name}" if f_name else "#"
    
    # دمج البيانات والترجمات بأمان وشفافية داخل القالب
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
    html = html.replace('USE_ALIGN', 'right' if is_ar else 'left')
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
