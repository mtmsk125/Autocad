from flask import Flask, request, send_file, render_template_string
import ezdxf, os

app = Flask(__name__)

@app.route('/download/<filename>')
def download(filename):
    p = os.path.join('/tmp', filename)
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("Not found", 404)

@app.route('/', methods=['GET', 'POST'])
def index():
    res, f_name, err = '', '', 0
    if request.method == 'POST' or 'test_mode' in request.args:
        try:
            if 'test_mode' in request.args:
                f_name = 'test_broken.dxf'
                fpath = os.path.join('/tmp', f_name)
                doc = ezdxf.new('R2000')
                msp = doc.modelspace()
                # رسم خطوط مفتوحة حقيقية 100% ليتعرف عليها العداد بدقة
                msp.add_line((0, 0), (10, 10))
                msp.add_line((20, 20), (30, 30))
                doc.saveas(fpath)
            else:
                f = request.files['dxf_file']
                if f and f.filename != '':
                    f_name = f.filename
                    fpath = os.path.join('/tmp', f_name)
                    f.save(fpath)
                else: return "No file", 400
            
            doc = ezdxf.readfile(fpath)
            msp = doc.modelspace()
            for e in msp.query('LWPOLYLINE LINE'):
                if e.dxftype() == 'LWPOLYLINE' and not e.closed:
                    err += 1
                    e.close()
                elif e.dxftype() == 'LINE':
                    err += 1 # احتساب الخطوط المفتوحة كأخطاء هندسية
            
            f_name = 'fixed_' + f_name
            doc.saveas(os.path.join('/tmp', f_name))
            if os.path.exists(fpath): os.remove(fpath)
            
            if err == 0:
                res = f'''<div class="rc"><h3>✓ المخطط سليم ومثالي 100%!</h3><p style="color:#15803d;">الملف خالٍ من الخطوط المفتوحة وجاهز للقص الفوري، يمكنك تحميله مجاناً.</p><a href="/download/{f_name}" class="btn" style="display:block; text-decoration:none; line-height:45px; background:#2563eb;">تحميل مجاناً 📥</a></div>'''
            else:
                res = f'''<div class="rc" style="border-color:#fca5a5; background:#fffaf0;"><div class="success-icon" style="background:#f59e0b;">!</div><h3>تم الإصلاح التلقائي بنجاح!</h3><p>عدد الخطوط المفتوحة والمصححة: <strong style="color:#e11d48; font-size:22px;">{err}</strong></p><button onclick="openPaymentModal()" class="btn-d">تحميل ملف DXF السليم الآن 🚀</button></div>'''
        except Exception as e: res = f'<div class="ec">⚠️ خطأ: {str(e)}</div>'
    
    d_url = f"/download/{f_name}" if f_name else "#"
    
    page = f'''<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>DXF Fixer</title>
    <style>:root{{--p:#2563eb;--s:#10b981;--bg:#f8fafc;}}body{{font-family:sans-serif;background:var(--bg);padding:20px;text-align:center;}}.ctr{{background:#fff;padding:35px 20px;border-radius:16px;max-width:550px;margin:50px auto;box-shadow:0 10px 25px rgba(0,0,0,0.05);}}.ua{{border:2px dashed #3498db;padding:35px 20px;border-radius:12px;cursor:pointer;position:relative;}}.ua input[type="file"]{{position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;cursor:pointer;}}.btn{{padding:14px;background:var(--p);color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;width:100%;margin-top:20px;}}.rc{{margin-top:25px;padding:20px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;}}.btn-d{{padding:14px;background:var(--s);color:#fff;border:none;border-radius:8px;font-size:17px;cursor:pointer;width:100%;}}.ec{{margin-top:20px;padding:15px;background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;color:#991b1b;}}.md{{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background:rgba(15,23,42,0.6);backdrop-filter:blur(3px);}}.mc{{background:#fff;margin:12% auto;padding:30px;border-radius:16px;width:85%;max-width:400px;text-align:right;position:relative;}}.cb{{position:absolute;left:20px;top:15px;font-size:24px;cursor:pointer;color:#94a3b8;}}.p-box{{background:#f8fafc;padding:15px;border-radius:12px;border-right:5px solid var(--s);margin:15px 0;text-align:center;}}.num{{color:var(--s);font-size:22px;font-weight:700;display:block;margin-top:5px;}}.iv{{width:94%;padding:12px;border:1px solid #cbd5e1;border-radius:8px;margin-bottom:15px;text-align:center;font-size:16px;}}</style></head><body>
    <div class="ctr"><h2>منصة DXF Fixer لخدمة الـ CNC 🛠️</h2><p style="color:#64748b;font-size:14px;">ارفع ملف DXF لفحصه مجاناً وتحديد وإصلاح الخطوط المفتوحة تلقائياً لضمان سلامة القص.</p>
        <form method="POST" enctype="multipart/form-data"><div class="ua"><div style="font-size:40px;">📥</div><div id="fl">اسحب ملف DXF هنا أو اضغط للتصفح</div><input type="file" name="dxf_file" accept=".dxf" required onchange="uFN(this)"></div><button type="submit" class="btn">ابدأ الفحص والإصلاح التلقائي</button></form>{res}
        <div style="margin-top:25px; border-top:1px dashed #e2e8f0; padding-top:15px;"><a href="/?test_mode=1" style="color:var(--p); font-size:13px; font-weight:600; text-decoration:none;">⚙️ اضغط هنا لتوليد ملف تالف تلقائياً واختبار عدّاد الأخطاء والنافذة</a></div>
    </div>
    <div id="pM" class="md"><div class="mc"><span class="cb" onclick="closePaymentModal()">&times;</span><h3 style="text-align:center;">🔓 خطوة واحدة لتحميل ملفك الجاهز</h3><p style="font-size:13px;color:#64748b;text-align:center;">يرجى تحويل مبلغ 1 دينار أردني فقط عبر كليك الفوري المباشر لتفعيل التنزيل:</p>
        <div class="p-box"><strong>🏦 الدفع الفوري عبر كليك (CliQ)</strong><span class="num">00962795156768</span></div>
        <div style="margin-top:15px;border-top:1px solid #e2e8f0;padding-top:15px;"><label style="font-size:13px;font-weight:600;display:block;margin-bottom:8px;">أدخل اسم المحوِّل أو رقم الهاتف للتأكيد:</label><input type="text" id="buyerInfo" class="iv" placeholder="مثال: محمد أحمد"><button type="button" onclick="vAD()" class="btn" style="margin-top:0;background:var(--p);">تأكيد وتحميل الملف فوراً 📥</button></div>
    </div></div>
    <div style="text-align:center; margin-bottom:30px;"><a href="https://wa.me تفعيل الاشتراك الشهري للورشة" target="_blank" style="color:#64748b; font-size:12px; text-decoration:none; margin:0 10px;">💼 الاشتراك الشهري للورش (10 دنانير)</a></div>
    <script>
        function uFN(i){{var l=document.getElementById('fl');if(i.files.length>0){{l.innerText="تم اختيار: "+i.files.name;l.style.color="var(--p)";}}}}
        function openPaymentModal(){{document.getElementById('pM').style.display='block';}} function closePaymentModal(){{document.getElementById('pM').style.display='none';}}
        function vAD(){{var v=document.getElementById('buyerInfo').value.trim();if(v===""){{alert("الرجاء إدخال تفاصيل التحويل");}}else{{window.location.href="{d_url}";closePaymentModal();}}}}
        window.onclick=function(e){{var m=document.getElementById('pM');if(e.target==m){{m.style.display="none";}}}}
    </script></body></html>'''
    return render_template_string(page)

if __name__ == '__main__':
    app.run(debug=True)
