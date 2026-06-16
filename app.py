from flask import Flask, request, send_file
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
    if request.method == 'POST':
        try:
            file = request.files['dxf_file']
            if file:
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
                <div style="margin-top:25px; border-top: 1px solid #eee; padding-top: 20px;">
                    <h3 style="color:#2ecc71;">تم الفحص بنجاح!</h3>
                    <p style="font-size:16px;">الأخطاء المكتشفة والمصححة بصرياً بدوائر حمراء: <strong>{errors}</strong></p>
                    <button onclick="openPaymentModal()" style="padding:15px 30px; background:#27ae60; color:white; border:none; border-radius:8px; font-size:18px; cursor:pointer; font-weight:bold; width:100%; transition:0.3s;">تحميل ملف DXF المصحح 🚀</button>
                </div>
                '''
                os.remove(filepath)

        except Exception as e:
            result = f'<p style="color:#e74c3c; margin-top:20px;">خطأ: {str(e)}</p>'

    download_url = f"/download/{fixed_filename}" if request.method == 'POST' and 'fixed_filename' in locals() else "#"

    page = f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>فاحص ومصلح ملفات DXF</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; padding: 20px; text-align: center; color: #333; }}
            .box {{ background: white; padding: 40px 30px; border-radius: 12px; max-width: 550px; margin: 60px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h2 {{ color: #2c3e50; margin-bottom: 10px; }}
            p.subtitle {{ color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
            input[type="file"] {{ border: 2px dashed #3498db; padding: 20px; border-radius: 8px; width: 80%; max-width: 100%; cursor: pointer; background: #fcfcfc; }}
            form button {{ padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 15px; width: 90%; transition: 0.3s; }}
            form button:hover {{ background: #2980b9; }}
            
            /* تصميم النافذة المنبثقة للدفع المحلي */
            .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }}
            .modal-content {{ background-color: #fff; margin: 12% auto; padding: 30px; border-radius: 12px; width: 85%; max-width: 450px; text-align: right; box-shadow: 0 5px 25px rgba(0,0,0,0.2); position: relative; animation: animatetop 0.3s; }}
            @keyframes animatetop {{ from {{top:-300px; opacity:0}} to {{top:0; opacity:1}} }}
            .close-btn {{ position: absolute; left: 20px; top: 15px; font-size: 24px; cursor: pointer; color: #aaa; }}
            .close-btn:hover {{ color: #000; }}
            .payment-detail {{ background: #f9f9f9; padding: 15px; border-radius: 8px; border-right: 4px solid #27ae60; margin: 15px 0; font-size: 16px; line-height: 1.8; text-align: center; }}
        </style>
    </head>
    <body>

    <div class="box">
        <h2>فاحص ومصلح ملفات DXF لـ CNC 🛠️</h2>
        <p class="subtitle">ارفع ملفك الـ DXF التالف لفحصه مجاناً، وتحديد خطوطه المفتوحة وإصلاحها تلقائياً لماكينات الليزر والراوتر.</p>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="dxf_file" accept=".dxf" required><br>
            <button type="submit">فحص وإصلاح الملف تلقائياً</button>
        </form>
        {result}
    </div>

    <!-- نافذة الدفع المنبثقة كليك -->
    <div id="paymentModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closePaymentModal()">&times;</span>
            <h3 style="color:#2c3e50; margin-top:10px; text-align: center;">🔓 خطوة واحدة لتحميل ملفك السليم</h3>
            <p style="font-size:14px; color:#666; text-align: center;">لدعم استمرار السيرفر وتطوير الخوارزمية، يرجى تحويل مبلغ <strong>1 دينار أردني فقط</strong> عبر كليك المباشر:</p>
            
            <div class="payment-detail">
                🏦 <strong>الدفع عبر كليك (CliQ)</strong><br>
                رقم الهاتف / المعرّف:<br>
                <span style="color:#27ae60; font-size: 20px; font-weight:bold; letter-spacing: 1px;">00962795156768</span>
            </div>
            
            <div style="margin-top:20px; border-top:1px solid #eee; padding-top:15px;">
                <label style="font-size:13px; font-weight:bold; color:#555; display:block; margin-bottom:5px;">أدخل اسم المحوّل أو رقم الهاتف للتفعيل الفوري:</label>
                <input type="text" id="buyerInfo" placeholder="مثال: محمد / 079xxxxxxx" style="width:95%; padding:10px; border:1px solid #ccc; border-radius:5px; margin-bottom:10px; text-align: center; font-size:16px;">
                <button onclick="verifyAndDownload()" style="width:100%; padding:12px; background:#27ae60; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer; font-size:16px;">تأكيد وتحميل الملف فوراً 📥</button>
            </div>
        </div>
    </div>

    <script>
        function openPaymentModal() {{
            document.getElementById('paymentModal').style.display = 'block';
        }}
        function closePaymentModal() {{
            document.getElementById('paymentModal').style.display = 'none';
        }}
        function verifyAndDownload() {{
            var info = document.getElementById('buyerInfo').value.trim();
            if(info === "") {{
                alert("الرجاء إدخال اسم أو رقم الهاتف المحوّل لتفعيل التحميل.");
            }} else {{
                window.location.href = "{download_url}";
                closePaymentModal();
            }}
        }}
        window.onclick = function(event) {{
            var modal = document.getElementById('paymentModal');
            if (event.target == modal) {{
                modal.style.display = "none";
            }}
        }}
    </script>

    </body>
    </html>'''

    return page

if __name__ == '__main__':
    app.run(debug=True)


    
