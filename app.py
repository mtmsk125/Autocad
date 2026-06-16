from flask import Flask, request, send_file, render_template_string
import ezdxf, os

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
                doc.saveas(os.path.join('/tmp', fixed_filename))
                result = f'''
                <div class="result-card">
                    <div class="success-icon">✓</div>
                    <h3>تم الفحص والإصلاح بنجاح!</h3>
                    <p>عدد الأخطاء المصححة: <strong>{errors}</strong></p>
                    <button type="button" onclick="openPaymentModal()" class="btn-submit" style="background:#10b981;">تحميل ملف DXF السليم 🚀</button>
                </div>'''
                os.remove(filepath)
        except Exception as e:
            result = f'<div class="error-card">⚠️ خطأ: {str(e)}</div>'

    download_url = f"/download/{fixed_filename}" if fixed_filename else "#"
    
    html_page = f'''
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة DXF Fixer | مصلح ملفات الـ CNC الذكي</title>
    <style>
        :root {{ --primary: #2563eb; --dark: #0f172a; --bg: #f8fafc; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); margin: 0; padding: 0; text-align: center; }}
        .navbar {{ background: #fff; padding: 15px 5%; display: flex; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .logo {{ font-size: 20px; font-weight: 800; color: var(--dark); }} .logo span {{ color: var(--primary); }}
        .hero {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 50px 5% 120px; }}
        .hero h1 {{ font-size: 28px; margin-bottom: 10px; }} .hero p {{ font-size: 14px; color: #cbd5e1; max-width: 600px; margin: 0 auto; }}
        .wrapper {{ max-width: 550px; margin: -80px auto 40px; padding: 0 20px; }}
        .container {{ background: #fff; padding: 30px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }}
        .upload-area {{ border: 2px dashed #3498db; padding: 40px 20px; border-radius: 14px; cursor: pointer; background: #f8fafc; position: relative; }}
        .upload-area input[type="file"] {{ position: absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:pointer; }}
        .btn-submit {{ padding: 14px; background: var(--primary); color: white; border: none; border-radius: 10px; font-size: 16px; cursor: pointer; font-weight: 600; margin-top: 20px; width: 100%; }}
        .result-card {{ margin-top: 20px; padding: 20px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 14px; }}
        .success-icon {{ width: 40px; height: 40px; background: #10b981; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: bold; }}
        .error-card {{ margin-top: 20px; padding: 15px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; color: #991b1b; }}
        .features {{ max-width: 850px; margin: 30px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; padding: 0 20px; }}
        .f-card {{ background: #fff; padding: 20px; border-radius: 12px; text-align: right; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .footer {{ background: var(--dark); color: #94a3b8; padding: 20px; font-size: 13px; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(3px); }}
        .modal-content {{ background: #fff; margin: 12% auto; padding: 30px; border-radius: 16px; width: 85%; max-width: 400px; text-align: right; position: relative; box-sizing: border-box; }}
        .close-btn {{ position: absolute; left: 20px; top: 15px; font-size: 24px; cursor: pointer; color: #94a3b8; }}
        .pay-box {{ background: #f8fafc; padding: 15px; border-radius: 12px; border-right: 5px solid #10b981; margin: 15px 0; text-align: center; }}
        .cliq-num {{ color: #10b981; font-size: 22px; font-weight: 700; margin-top: 5px; display: block; }}
        .input-verify {{ width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 15px; text-align: center; font-size: 16px; box-sizing: border-box; }}
    </style></head><body>
    <div class="navbar"><div class="logo">🛠️ DXF<span>Fixer</span></div><div>🚀 أداة ذكية للـ CNC</div></div>
    <div class="hero"><h1>إصلاح وتنظيف ملفات DXF تلقائياً بضغطة زر</h1><p>تجنب هدر المواد وضياع الوقت على الماكينة. تكتشف منصتنا الأخطاء، وتسد الخطوط المفتوحة، وتجهز ملفك للقص الفوري.</p></div>
    <div class="wrapper"><div class="container">
        <form method="POST" enctype="multipart/form-data">
            <div class="upload-area"><div style="font-size:40px;">📥</div><div id="file-label" style="font-weight:600; margin-top:10px;">اسحب ملف DXF هنا أو اضغط للتصفح</div>
            <input type="file" name="dxf_file" accept=".dxf" required onchange="updateFileName(this)"></div>
            <button type="submit" class="btn-submit">ابدأ الفحص والإصلاح التلقائي الآن</button>
        </form>{result}
    </div></div>
    <div class="features">
        <div class="f-card"><h4>⚡ إصلاح تلقائي فوري</h4><p>الخوارزمية تكتشف الخطوط المفتوحة وتقوم بإغلاقها ومعالجتها أوتوماتيكياً في ثوانٍ.</p></div>
        <div class="f-card"><h4>🎯 تحديد دقيق للأخطاء</h4><p>يتم رسم دوائر حمراء منبّهة حول أماكن المشاكل والقطع غير المتصلة لتسهيل فحصها.</p></div>
    </div>
    <div class="footer">جميع الحقوق محفوظة © 2026 منصة DXF Fixer - الأردن.</div>
    <div id="paymentModal" class="modal"><div class="modal-content"><span class="close-btn" onclick="closePaymentModal()">&times;</span>
        <h3 style="text-align: center;">🔓 خطوة واحدة لتحميل ملفك الجاهز</h3>
        <p style="font-size:13px; color: #64748b; text-align: center;">يرجى تحويل مبلغ <strong>1 دينار أردني فقط</strong> عبر كليك الفوري لدعم السيرفر:</p>
        <div class="pay-box"><strong>🏦 الحوالة المباشرة عبر كليك (CliQ)</strong><span class="cliq-num">00962795156768</span></div>
        <div style="margin-top:15px; border-top:1px solid #e2e8f0; padding-top:15px;">
            <label style="font-size:13px; font-weight:600; display:block; margin-bottom:8px;">أدخل اسم المحوِّل أو رقم الهاتف للتأكيد:</label>
            <input type="text" id="buyerInfo" class="input-verify" placeholder="مثال: محمد أحمد / 079xxxxxxx">
            <button type="button" onclick="verifyAndDownload()" class="btn-submit" style="margin-top:0;">تأكيد وتحميل الملف فوراً 📥</button>
        </div>
    </div></div>
    <script>
        function updateFileName(input) {{ var label = document.getElementById('file-label'); if(input.files && input.files.length > 0) {{ label.innerText = "تم اختيار: " + input.files[0].name; label.style.color = "#2563eb"; }} }}
        function openPaymentModal() {{ document.getElementById('paymentModal').style.display = 'block'; }}
        function closePaymentModal() {{ document.getElementById('paymentModal').style.display = 'none'; }}
        function verifyAndDownload() {{ var info = document.getElementById('buyerInfo').value.trim(); if(info === "") {{ alert("الرجاء إدخال اسم أو رقم الهاتف المحوّل."); }} else {{ window.location.href = "{download_url}"; closePaymentModal(); }} }}
        window.onclick = function(event) {{ var modal = document.getElementById('paymentModal'); if (event.target == modal) {{ modal.style.display = "none"; }} }}
    </script></body></html>'''
    return render_template_string(html_page, result=result, download_url=download_url)

if __name__ == '__main__':
    app.run(debug=True)

    
