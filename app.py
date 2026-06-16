from flask import Flask, request, send_file, Response
import ezdxf, os, sqlite3, datetime

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
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("Not found", 404)

@app.route('/admin_moawia', methods=['GET', 'POST'])
def admin():
    msg = ''
    if request.method == 'POST':
        c, d, o = request.form.get('code_name', '').strip(), request.form.get('days', '').strip(), request.form.get('owner_name', '').strip()
        if c and d:
            exp = (datetime.datetime.now() + datetime.timedelta(days=int(d))).strftime('%Y-%m-%d')
            with sqlite3.connect(DB_PATH) as conn: conn.execute('INSERT OR REPLACE INTO codes VALUES (?,?,?)', (c, exp, o))
            msg = f'✓ تم إضافة الكود {c} بنجاح وينتهي بتاريخ {exp}'
    with sqlite3.connect(DB_PATH) as conn: rows = conn.execute('SELECT * FROM codes').fetchall()
    t_rows = ''.join([f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>' for r in rows])
    return f'''<!DOCTYPE html><html dir="rtl"><head><title>المدير</title><style>body{{font-family:sans-serif;padding:30px;background:#f1f5f9;text-align:center;}}input{{padding:10px;margin:10px;width:80%;max-width:300px;border-radius:6px;border:1px solid #ccc;}}table{{width:100%;max-width:600px;margin:20px auto;background:#fff;border-collapse:collapse;}}th,td{{border:1px solid #ddd;padding:12px;text-align:center;}}th{{background:#1e293b;color:#fff;}}</style></head><body><h2>🛠️ لوحة تحكم معاوية لإدارة الاشتراكات</h2><p style="color:green;font-weight:bold;">{msg}</p><form method="POST"><input type="text" name="code_name" placeholder="كود التفعيل" required><br><input type="number" name="days" placeholder="الأيام (مثال: 30)" required><br><input type="text" name="owner_name" placeholder="اسم صاحب الورشة" required><br><button type="submit" style="padding:10px 20px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">تفعيل الكود</button></form><h3>📋 الأكواد الحالية الفعالة</h3><table><tr><th>الكود السرّي</th><th>تاريخ الانتهاء</th><th>اسم المشترك</th></tr>{t_rows}</table><br><a href="/" style="text-decoration:none;color:#64748b;">← العودة لصفحة الفحص الرئيسية</a></body></html>'''

@app.route('/check_promo_api')
def check_promo():
    c = request.args.get('code', '').strip()
    with sqlite3.connect(DB_PATH) as conn: row = conn.execute('SELECT expires FROM codes WHERE code = ?', (c,)).fetchone()
    if row and datetime.datetime.now() <= datetime.datetime.strptime(row[0], '%Y-%m-%d'): return "VALID"
    return "INVALID"

@app.route('/', methods=['GET', 'POST'])
def index():
    res, f_name, pts = '', '', []
    if request.method == 'POST':
        try:
            f = request.files.get('dxf_file')
            if f and f.filename != '':
                f_name = f.filename; fpath = os.path.join('/tmp', f_name); f.save(fpath)
                doc = ezdxf.readfile(fpath); msp = doc.modelspace(); err = 0
                for e in msp.query('LWPOLYLINE LINE'):
                    if e.dxftype() == 'LWPOLYLINE' and not e.closed: err += 1; e.close()
                    elif e.dxftype() == 'LINE': err += 1; pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
                f_name = 'fixed_' + f_name; doc.saveas(os.path.join('/tmp', f_name))
                if os.path.exists(fpath): os.remove(fpath)
                if err == 0: res = f'<div class="rc"><h3>✓ المخطط سليم 100%!</h3><p style="color:#15803d;">جاهز للقص، يمكنك تحميله مجاناً.</p><a href="/download/{f_name}" class="btn-d" style="display:block;text-decoration:none;line-height:45px;background:#2563eb;color:#fff;border-radius:10px;">تحميل مجاناً 📥</a></div>'
                else: res = f'<div class="rc" style="border-color:#fca5a5;background:#fffaf0;"><div class="success-icon" style="background:#f59e0b;">!</div><h3>تم الإصلاح بنجاح!</h3><p>الخطوط المصلحة: <strong>{err}</strong></p><button onclick="openPaymentModal()" class="btn-d" style="width:100%;padding:14px;background:#10b981;color:white;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">تحميل ملف DXF السليم الآن 🚀</button></div>'
        except Exception as e: res = f'<div class="ec">⚠️ خطأ: {str(e)}</div>'
    
    try:
        cd = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(cd, 'index.html'), 'r', encoding='utf-8') as f_obj: html = f_obj.read()
    except: return "index.html missing", 500

    html = html.replace('USE_RESULT', res).replace('USE_DOWNLOAD_URL', f"/download/{f_name}" if f_name else "#").replace('USE_JS_PTS', str(pts))
    return Response(html, mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
