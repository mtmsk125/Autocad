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
    if request.method == 'POST':
        try:
            f = request.files.get('dxf_file')
            if f and f.filename != '':
                f_name = f.filename
                fpath = os.path.join('/tmp', f_name)
                f.save(fpath)
                doc = ezdxf.readfile(fpath)
                msp = doc.modelspace()
                err = 0
                for e in msp.query('LWPOLYLINE LINE'):
                    if e.dxftype() == 'LWPOLYLINE' and not e.closed:
                        err += 1
                        e.close()
                        if len(e) > 0:
                            p = e.get_points()[0]
                            pts.append({"x": float(p[0]), "y": float(p[1])})
                            msp.add_circle((p[0], p[1]), radius=1.0, dxfattribs={'color': 1})
                    elif e.dxftype() == 'LINE':
                        err += 1
                        pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
                        msp.add_circle(e.dxf.start, radius=1.0, dxfattribs={'color': 1})
                f_name = 'fixed_' + f_name
                doc.saveas(os.path.join('/tmp', f_name))
                os.remove(fpath)
                if is_ar:
                    res = f'''<div class="rc"><h3>✓ تم الإصلاح التلقائي بنجاح!</h3><p>عدد الأخطاء: <strong>{err}</strong></p><button type="button" onclick="openPaymentModal()" class="btn" style="background:#10b981;">تحميل ملف DXF السليم 🚀</button></div>'''
                else:
                    res = f'''<div class="rc"><h3>✓ Scan & Fix Completed!</h3><p>Errors Fixed: <strong>{err}</strong></p><button type="button" onclick="openPaymentModal()" class="btn" style="background:#10b981;">Download Clean DXF 🚀</button></div>'''
        except Exception as e: res = f'<div class="ec">⚠️ Error: {str(e)}</div>'
    d_url = f"/download/{f_name}" if f_name else "#"
    dir_attr = "rtl" if is_ar else "ltr"
    t = "DXF Fixer" if is_ar else "DXF Fixer Platform"
    h1 = "إصلاح وتنظيف ملفات DXF تلقائياً بضغطة زر" if is_ar else "Auto-Fix DXF Files Instantly"
    p = "تكتشف منصتنا الأخطاء، وتغلق الخطوط المفتوحة، وتجهز ملفك للقص الفوري." if is_ar else "Our tool detects errors, closes open loops, and preps your file for cutting."
    lbl = "اسحب ملف DXF هنا أو اضغط للتصفح" if is_ar else "Drag & Drop DXF file here or Click to browse"
    btn = "ابدأ الفحص والإصلاح التلقائي الآن" if is_ar else "Start Auto-Scan & Repair Now"
    mh3 = "🔓 خطوة واحدة لتحميل ملفك الجاهز" if is_ar else "🔓 One Step to Download Your Ready File"
    mp = "يرجى تحويل مبلغ 1 دينار أردني (أو $1.5) عبر كليك لتفعيل التنزيل:" if is_ar else "Please transfer 1 JOD (or $1.5 USD) via CliQ to unlock your download:"
    v_lbl = "أدخل اسم المحوِّل للتأكيد والتنزيل:" if is_ar else "Enter sender name to verify & download:"
    v_ph = "مثال: محمد أحمد / 079xxxxxxx" if is_ar else "e.g., John Doe / Phone Number"
    v_btn = "تأكيد وتحميل الملف فوراً 📥" if is_ar else "Verify & Download File Instantly 📥"
    
    html = f'''<!DOCTYPE html><html dir="{dir_attr}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{t}</title>
    <style>:root{{--p:#2563eb;--d:#0f172a;--bg:#f8fafc;}}body{{font-family:system-ui,sans-serif;background:var(--bg);margin:0;padding:0;text-align:center;}}.nav{{background:#fff;padding:15px 5%;display:flex;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,0.05);font-weight:800;}}.hero{{background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);color:#fff;padding:50px 5% 120px;}}.hero h1{{font-size:26px;margin:0 0 10px;}}.hero p{{font-size:14px;color:#cbd5e1;margin:0;}}.wrap{{max-width:520px;margin:-80px auto 40px;padding:0 20px;}}.ctr{{background:#fff;padding:30px;border-radius:20px;box-shadow:0 20px 25px -5px rgba(0,0,0,0.1);}}.ua{{border:2px dashed #3498db;padding:40px 20px;border-radius:14px;cursor:pointer;background:#f8fafc;position:relative;}}.ua input[type="file"]{{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:pointer;}}.btn{{padding:14px;background:var(--p);color:#fff;border:none;border-radius:10px;font-size:16px;cursor:pointer;font-weight:600;margin-top:20px;width:100%;}}.rc{{margin-top:20px;padding:20px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;}}.ec{{margin-top:20px;padding:15px;background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;color:#991b1b;}}.pb{{display:none;background:#fff;max-width:520px;margin:20px auto;padding:20px;border-radius:20px;box-shadow:0 10px 15px rgba(0,0,0,0.05);}}.cc{{width:100%;height:260px;background:#111827;border-radius:10px;position:relative;overflow:hidden;}}.ft{{background:var(--d);color:#94a3b8;padding:20px;font-size:13px;}}.md{{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(15,23,42,0.6);backdrop-filter:blur(3px);}}.mc{{background:#fff;margin:12% auto;padding:30px;border-radius:16px;width:85%;max-width:400px;text-align:start;position:relative;box-sizing:border-box;}}.cb{{position:absolute;right:20px;top:15px;font-size:24px;cursor:pointer;color:#94a3b8;}}html[dir="rtl"] .cb{{left:20px;right:auto;}}.p-box{{background:#f8fafc;padding:15px;border-radius:12px;border-left:5px solid #10b981;margin:15px 0;text-align:center;}}html[dir="rtl"] .p-box{{border-left:none;border-right:5px solid #10b981;}}.num{{color:#10b981;font-size:22px;font-weight:700;display:block;margin-top:5px;}}.iv{{width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;margin-bottom:15px;text-align:center;font-size:16px;box-sizing:border-box;}}</style></head><body>
    <div class="nav"><div>🛠️ DXF Fixer</div><div>🚀 CNC Tools</div></div><div class="hero"><h1>{h1}</h1><p>{p}</p></div>
    <div class="wrap"><div class="ctr"><form method="POST" enctype="multipart/form-data"><div class="ua"><div style="font-size:40px;">📥</div><div id="fl" style="font-weight:600;margin-top:10px;">{lbl}</div><input type="file" name="dxf_file" accept=".dxf" required onchange="vFN(this)"></div><button type="submit" class="btn">{btn}</button></form>{res}</div></div>
    <div id="vpb" class="pb"><h4 style="margin:0 0 10px;text-align:center;">🔍 خريطة الأخطاء المصلحة / Fixed Errors Map</h4><div class="cc" id="c-ctr"></div></div><div class="ft">{t}</div>
    <div id="pM" class="md"><div class="mc"><span class="cb" onclick="cPM()">&times;</span><h3 style="text-align:center;">{mh3}</h3><p style="font-size:13px;color:#64748b;text-align:center;">{mp}</p><div class="p-box"><strong>🏦 CliQ (International & Local Support)</strong><span class="num">00962795156768</span></div>
    <div style="margin-top:15px;border-top:1px solid #e2e8f0;padding-top:15px;"><label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px;">{v_lbl}</label><input type="text" id="bI" class="iv" placeholder="{v_ph}"><button type="button" onclick="vAD()" class="btn" style="margin-top:0;">{v_btn}</button></div></div></div>
    <script>
        function vFN(i){{var l=document.getElementById('fl');if(i.files&&i.files.length>0){{l.innerText=i.files[0].name;l.style.color="#2563eb";}}}}
        function openPaymentModal(){{document.getElementById('pM').style.display='block';}} function closePaymentModal(){{document.getElementById('pM').style.display='none';}}
        function vAD(){{var v=document.getElementById('bI').value.trim();if(v===""){{alert("Verification required / الرجاء إدخال تفاصيل التأكيد");}}else{{window.location.href="{d_url}";closePaymentModal();}}}}
        window.onclick=function(e){{var m=document.getElementById('pM');if(e.target==m){{m.style.display="none";}}}}
        var pts={pts};if(pts.length>0){{document.getElementById('vpb').style.display='block';var c=document.getElementById('c-ctr');pts.forEach(function(p){{var d=document.createElement('div');d.style.position='absolute';d.style.width='12px';d.style.height='12px';d.style.background='#ef4444';d.style.borderRadius='50%';d.style.boxShadow='0 0 10px #ef4444';d.style.left=(Math.abs(p.x*25)%(c.clientWidth-40)+20)+'px';d.style.top=(Math.abs(p.y*25)%(c.clientHeight-40)+20)+'px';d.style.animation='bk 1s infinite alternate';c.appendChild(d);}});var s=document.createElement('style');s.innerHTML='@keyframes bk{{from{{opacity:0.3;transform:scale(0.9);}}to{{opacity:1;transform:scale(1.2);}}}}';document.head.appendChild(s);}}
    </script></body></html>'''
    return render_template_string(html, res=res, d_url=d_url)
if __name__ == '__main__':
    app.run(debug=True)


    
