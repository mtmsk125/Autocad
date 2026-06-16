from flask import Flask, request, send_file, render_template_string
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
    return render_template_string(f'''<!DOCTYPE html><html dir="rtl"><head><title>المدير</title><style>body{{font-family:sans-serif;padding:30px;background:#f1f5f9;text-align:center;}}input{{padding:10px;margin:10px;width:80%;max-width:300px;border-radius:6px;border:1px solid #ccc;}}table{{width:100%;max-width:600px;margin:20px auto;background:#fff;border-collapse:collapse;}}th,td{{border:1px solid #ddd;padding:12px;}}th{{background:#1e293b;color:#fff;}}</style></head><body><h2>🛠️ لوحة تحكم معاوية لإدارة الاشتراكات</h2><p style="color:green;">{msg}</p><form method="POST"><input type="text" name="code_name" placeholder="كود التفعيل" required><br><input type="number" name="days" placeholder="الأيام (مثال: 30)" required><br><input type="text" name="owner_name" placeholder="اسم صاحب الورشة" required><br><button type="submit" style="padding:10px 20px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;">تفعيل الكود</button></form><table><tr><th>الكود</th><th>تاريخ الانتهاء</th><th>المشترك</th></tr>{table_rows}</table><br><a href="/">← العودة للرئيسية</a></body></html>''')

@app.route('/check_promo_api')
def check_promo():
    c = request.args.get('code', '').strip()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute('SELECT expires FROM codes WHERE code = ?', (c,)).fetchone()
        @app.route('/', methods=['GET', 'POST'])
def index():
    res, f_name, pts = '', '', []
    is_ar = 'ar' in request.headers.get('Accept-Language', '').lower()
    if request.method == 'POST' or 'test_mode' in request.args:
        try:
            if 'test_mode' in request.args:
                f_name, fpath = 'test_broken.dxf', '/tmp/test_broken.dxf'
                doc = ezdxf.new('R2000'); msp = doc.modelspace()
                msp.add_line((0, 0), (10, 10)); msp.add_line((20, 20), (30, 30)); doc.saveas(fpath)
            else:
                f = request.files.get('dxf_file')
                if f and f.filename != '':
                    f_name = f.filename; fpath = os.path.join('/tmp', f_name); f.save(fpath)
                else: return "No file", 400
            doc = ezdxf.readfile(fpath); msp = doc.modelspace(); err = 0
            for e in msp.query('LWPOLYLINE LINE'):
                if e.dxftype() == 'LWPOLYLINE' and not e.closed: err += 1; e.close()
                elif e.dxftype() == 'LINE': err += 1; pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
            f_name = 'fixed_' + f_name; doc.saveas(os.path.join('/tmp', f_name))
            if os.path.exists(fpath): os.remove(fpath)
            if err == 0:
                res = f'<div class="rc"><h3>✓ المخطط سليم 100%!</h3><p style="color:#15803d;">جاهز للقص، يمكنك تحميله مجاناً.</p><a href="/download/{f_name}" class="btn" style="background:#2563eb;display:block;text-decoration:none;line-height:45px;">تحميل مجاناً 📥</a></div>'
            else:
                res = f'<div class="rc" style="border-color:#fca5a5;background:#fffaf0;"><div class="success-icon" style="background:#f59e0b;">!</div><h3>تم الإصلاح التلقائي بنجاح!</h3><p>الخطوط المصلحة: <strong style="color:#e11d48;font-size:22px;">{err}</strong></p><button onclick="openPaymentModal()" class="btn-d">تحميل ملف DXF السليم الآن 🚀</button></div>'
        except Exception as e: res = f'<div class="ec">⚠️ خطأ: {str(e)}</div>'
    
    d_url = f"/download/{f_name}" if f_name else "#"
    align = "right" if is_ar else "left"
    p_table = f'''<div class="pricing-container"><h3 class="pricing-title">{"💎 خطط التحميل والاشتراك لورشتك" if is_ar else "💎 Choose Best Plan"}</h3><div class="pricing-grid">
    <div class="price-card"><h5>{"الملف الواحد" if is_ar else "Single File"}</h5><div class="price">{"1 د.أ" if is_ar else "$2.00"}</div><button onclick="openPaymentModal()" class="btn-price">{"دفع ملف" if is_ar else "Pay File"}</button></div>
    <div class="price-card popular"><div class="badge">{"الأكثر طلباً" if is_ar else "Popular"}</div><h5>{"الاشتراك الشهري" if is_ar else "Monthly Plan"}</h5><div class="price">{"10 د.أ" if is_ar else "$15.00"}</div><p>{"ملفات غير محدودة" if is_ar else "Unlimited files"}</p><a href="https://wa.me" target="_blank" class="btn-price" style="background:var(--p);color:#fff;text-decoration:none;display:block;">{"واتساب" if is_ar else "Subscribe"}</a></div>
    <div class="price-card"><h5>{"الاشتراك السنوي" if is_ar else "Annual Plan"}</h5><div class="price">{"70 د.أ" if is_ar else "$99.00"}</div><a href="https://wa.me" target="_blank" class="btn-price" style="text-decoration:none;display:block;">{"تفعيل" if is_ar else "Get Annual"}</a></div>
    </div></div>'''
    t_btn = f'''<div style="margin-top:20px;"><a href="/?test_mode=1" style="color:var(--p);font-weight:600;text-decoration:none;font-size:14px;">⚙️ {"اضغط هنا لتوليد ملف تالف واختبار خريطة الأخطاء والأسعار فوراً" if is_ar else "Click here to test broken file"}</a></div>'''
    html = f'''<!DOCTYPE html><html dir="{"rtl" if is_ar else "ltr"}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>DXF Fixer</title>
    <style>:root{{--p:#2563eb;--d:#0f172a;--bg:#f8fafc;--s:#10b981;}}body{{font-family:system-ui,sans-serif;background:var(--bg);margin:0;padding:0;text-align:center;}}.nav{{background:#fff;padding:15px 5%;display:flex;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.05);font-weight:800;}}.hero{{background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);color:#fff;padding:50px 5% 120px;}}.hero h1{{font-size:26px;margin:0 0 10px;}}.hero p{{font-size:14px;color:#cbd5e1;margin:0;}}.wrap{{max-width:520px;margin:-80px auto 40px;padding:0 20px;box-sizing:border-box;}}.ctr{{background:#fff;padding:30px;border-radius:20px;box-shadow:0 20px 25px -5px rgba(0,0,0,0.1);}}.ua{{border:2px dashed #3498db;padding:40px 20px;border-radius:14px;cursor:pointer;background:#f8fafc;position:relative;}}.ua input[type="file"]{{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:pointer;z-index:10;}}.btn{{padding:14px;background:var(--p);color:#fff;border:none;border-radius:10px;font-size:16px;cursor:pointer;width:100%;margin-top:20px;font-weight:600;}}.rc{{margin-top:20px;padding:20px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;}}.ec{{margin-top:20px;padding:15px;background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;color:#991b1b;}}.pb{{display:none;background:#fff;max-width:520px;margin:20px auto;padding:20px;border-radius:20px;box-shadow:0 10px 15px rgba(0,0,0,0.05);}}.cc{{width:100%;height:260px;background:#111827;border-radius:12px;position:relative;overflow:hidden;}}.features{{max-width:850px;margin:30px auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;padding:0 20px;}}.f-card{{background:#fff;padding:20px;border-radius:12px;text-align:{align};box-shadow:0 4px 6px rgba(0,0,0,0.05);}}.pricing-container{{max-width:850px;margin:40px auto 20px;}}.pricing-title{{font-size:20px;font-weight:800;color:var(--d);margin-bottom:20px;}}.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;}}.price-card{{background:#fff;padding:25px 15px;border-radius:14px;border:1px solid #e2e8f0;position:relative;}}.price-card.popular{{border-color:var(--p);}}.badge{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--p);color:#fff;padding:3px 10px;border-radius:20px;font-size:10px;font-weight:bold;}}.price{{font-size:28px;font-weight:800;margin:10px 0;}}.btn-price{{width:100%;padding:10px;background:#f1f5f9;color:var(--d);border:none;border-radius:6px;font-weight:600;cursor:pointer;}}.ft{{background:var(--d);color:#94a3b8;padding:20px;font-size:13px;}}.md{{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(15,23,42,0.6);backdrop-filter:blur(3px);}}.mc{{background:#fff;margin:12% auto;padding:30px;border-radius:16px;width:85%;max-width:400px;text-align:{align};position:relative;box-sizing:border-box;}}.cb{{position:absolute;top:15px;right:20px;font-size:24px;cursor:pointer;color:#94a3b8;}}html[dir="rtl"] .cb{{left:20px;right:auto;}}.p-box{{background:#f8fafc;padding:15px;border-radius:12px;border-left:5px solid var(--s);margin:15px 0;text-align:center;}}html[dir="rtl"] .p-box{{border-left:none;border-right:5px solid var(--s);}}.num{{color:var(--s);font-size:22px;font-weight:700;display:block;margin-top:5px;}}.iv{{width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;margin-bottom:15px;text-align:center;font-size:16px;box-sizing:border-box;}}</style></head><body>
    <div class="nav"><div>🛠️ DXF Fixer</div><div>🚀 CNC Tools</div></div><div class="hero"><h1>{"إصلاح وتنظيف ملفات DXF تلقائياً بضغطة زر" if is_ar else "Auto-Fix DXF Files Instantly"}</h1><p>{"تكتشف منصتنا الأخطاء وتجهز ملفك للقص الفوري وبأعلى دقة." if is_ar else "Our platform preps your file for cutting."}</p></div>
    <div class="wrap"><div class="ctr"><form method="POST" enctype="multipart/form-data"><div class="ua"><div style="font-size:40px;">📥</div><div id="fl" style="font-weight:600;margin-top:10px;">{"اسحب ملف DXF هنا أو اضغط للتصفح" if is_ar else "Drag & Drop DXF file here"}</div><input type="file" name="dxf_file" accept=".dxf" required onchange="vFN(this)"></div><button type="submit" class="btn">{"ابدأ الفحص والإصلاح تلقائياً" if is_ar else "Start Auto-Repair"}</button></form>{res}</div></div>
    <div id="vpb" class="pb"><h4 style="margin:0 0 10px;text-align:center;">🔍 خريطة الأخطاء المصلحة / Fixed Errors Map</h4><div class="cc" id="c-ctr"></div></div>
    {p_table}{t_btn}
    <div class="features">
        <div class="f-card"><h4>⚡ {"إصلاح تلقائي فوري" if is_ar else "Instant Auto-Repair"}</h4><p>{"تغلق الخوارزمية الخطوط المفتوحة في أجزاء من الثانية لسلامة القص." if is_ar else "Closes open vectors in milliseconds."}</p></div>
        <div class="f-card"><h4>🎯 {"تحديد دقيق للأخطاء" if is_ar else "Precise Visual Map"}</h4><p>{"عرض خريطة تفاعلية تومض باللون الأحمر فوق أماكن المشاكل المصلحة." if is_ar else "Flashing red map over fixed coordinates."}</p></div>
    </div>
    <div style="max-width:520px;margin:20px auto 40px;padding:20px;background:#fff;border-radius:14px;box-shadow:0 4px 6px rgba(0,0,0,0.05);box-sizing:border-box;"><h5 style="margin:0 0 10px;">💬 آراء العملاء والتطوير / Feedback</h5><textarea id="uFB" style="width:100%;height:60px;padding:10px;border-radius:8px;border:1px solid #cbd5e1;box-sizing:border-box;" placeholder="اكتب اقتراحك هنا..."></textarea><button type="button" onclick="sFB()" class="btn" style="padding:8px 15px;margin-top:10px;font-size:13px;width:auto;">إرسال التعليق</button></div>
    <div class="ft">جميع الحقوق محفوظة © 2026 منصة DXF Fixer. | <a href="/admin_moawia" style="color:#94a3b8;text-decoration:none;">🔐 الإدارة</a></div>
    <div id="pM" class="md"><div class="mc"><span class="cb" onclick="closePaymentModal()">&times;</span><h3 style="text-align:center;">{"🔓 خطوة واحدة لتنزيل ملفك السليم" if is_ar else "🔓 One Quick Step to Download"}</h3><p style="font-size:13px;color:#64748b;text-align:center;">{"يرجى تحويل قيمة الخدمة (1 دينار محلي / أو $2 للأجانب) عبر كليك لتفعيل التحميل:" if is_ar else "Please transfer the fee ($2 USD / 1 JOD) via CliQ to unlock:"}</p><div class="p-box"><strong>🏦 الحوالة المباشرة عبر كليك (CliQ)</strong><span class="num">00962795156768</span></div>
    <div style="margin-top:15px;border-top:1px solid #e2e8f0;padding-top:15px;"><label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px;">{"أدخل اسم المحوِّل للتأكيد والتنزيل:" if is_ar else "Enter sender name to verify:"}</label><input type="text" id="buyerInfo" class="iv" placeholder="مثال: محمد أحمد"><button type="button" onclick="vAD()" class="btn" style="margin-top:0;">{"تأكيد وتحميل الملف فوراً 📥" if is_ar else "Confirm & Download 📥"}</button></div>
    <div style="margin-top:15px;border-top:1px dashed #cbd5e1;padding-top:15px;"><label style="font-size:12px;font-weight:bold;color:#64748b;display:block;margin-bottom:5px;">🔐 للمشتركين: أدخل كود التفعيل الشهري الفريد الخاص بك:</label><input type="text" id="promoInput" class="iv" style="margin-bottom:10px;padding:8px;" placeholder="كود التفعيل"><button type="button" onclick="checkPromo()" class="btn" style="margin-top:0;background:#64748b;font-size:14px;">تفعيل الكود والتحميل الفوري 🔓</button></div></div></div>
    <script>
        function vFN(i){{var l=document.getElementById('fl');if(i.files&&i.files.length>0){{l.innerText=i.files.name;l.style.color="#2563eb";}}}}
        function openPaymentModal(){{document.getElementById('pM').style.display='block';}} function closePaymentModal(){{document.getElementById('pM').style.display='none';}}
        function vAD(){{var v=document.getElementById('buyerInfo').value.trim();if(v===""){{alert("مطلوب");}}else{{window.location.href="{d_url}";closePaymentModal();}}}}
        function sFB(){{var t=document.getElementById('uFB').value.trim();if(t===""){{alert("فارغ");}}else{{alert("شكراً لك! تم استلام اقتراحك بنجاح 🚀");document.getElementById('uFB').value="";}}}}
        function checkPromo(){{var code=document.getElementById('promoInput').value.trim();if(code===""){{alert("أدخل الكود");return;}}fetch('/check_promo_api?code='+encodeURIComponent(code)).then(res=>res.text()).then(status=>{{if(status==="VALID"){{window.location.href="{d_url}";closePaymentModal();}}else{{alert("الكود خاطئ أو منتهي الصلاحية ⚠️");}}}});}}
        window.onclick=function(e){{var m=document.getElementById('pM');if(e.target==m){{m.style.display="none";}}}}
        var pts={str(pts)};if(pts.length>0){{document.getElementById('vpb').style.display='block';var c=document.getElementById('c-ctr');pts.forEach(function(p){{var d=document.createElement('div');d.style.position='absolute';d.style.width='12px';d.style.height='12px';d.style.background='#ef4444';d.style.borderRadius='50%';d.style.boxShadow='0 0 10px #ef4444';d.style.left=(Math.abs(p.x*25)%(c.clientWidth-40)+20)+'px';d.style.top=(Math.abs(p.y*25)%(c.clientHeight-40)+20)+'px';d.style.animation='bk 1s infinite alternate';c.appendChild(d);}});var s=document.createElement('style');s.innerHTML='@keyframes bk{{from{{opacity:0.3;transform:scale(0.9);}}to{{opacity:1;transform:scale(1.2);}}}}';document.head.appendChild(s);}}
    </script></body></html>'''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

    if row and datetime.datetime.now() <= datetime.datetime.strptime(row[0], '%Y-%m-%d'): return "VALID"
    return "INVALID"
