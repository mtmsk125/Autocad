from flask import Flask, request, send_file
import ezdxf, tempfile, os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        try:
            file = request.files['dxf_file']
            if not file:
                result = '<p style="color:red">ارفع ملف DXF</p>'
            else:
                temp_dir = '/tmp'
                filepath = os.path.join(temp_dir, file.filename)
                file.save(filepath)

                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace()
                errors = 0

                for e in msp.query('LWPOLYLINE LINE'):
                    if e.dxftype() == 'LWPOLYLINE':
                        if not e.closed:
                            errors += 1
                            p = e.get_points()[0]
                            msp.add_circle((p[0], p[1]), radius=0.5, dxfattribs={'color': 1})
                    elif e.dxftype() == 'LINE':
                        errors += 1
                        msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})

                fixed_path = os.path.join(temp_dir, 'fixed_' + file.filename)
                doc.saveas(fixed_path)

                result = '<div style="margin-top:20px"><h3>تم الفحص بنجاح!</h3><p>الأخطاء: ' + str(errors) + '</p><a href="/download/' + os.path.basename(fixed_path) + '"><button style="padding:15px 30px; background:green; color:white; border:none; border-radius:5px; font-size:18px;">تحميل DXF المصح</button></a><br><br><a href="/">فحص ملف ثاني</a></div>'
                os.remove(filepath)

        except Exception as e:
            result = '<p style="color:red">خطأ: ' + str(e) + '</p>'

    page = '''
    <!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:Arial;background:#f5f5f5;padding:20px;text-align:center;margin:0}
 .box{background:white;padding:30px;border-radius:10px;max-width:500px;margin:50px auto;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
    button{padding:12px 30px;background:#007bff;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer}
    button:hover{background:#0056b3}
 .loading{display:none;margin-top:20px;font-size:18px;color:#007bff}</style>
    </head><body><div class="box">
    <h2>فاحص DXF - إصلاح تلقائي</h2>
    <p>ارفع ملف DXF وسيتم فحصه وإصلاح الأخطاء</p>
    <form method="POST" enctype="multipart/form-data" onsubmit="document.getElementById('loading').style.display='block'">
    <input type="file" name="dxf_file" accept=".dxf" required><br><br>
    <button type="submit">فحص وإصلاح</button></form>
    <div id="loading" class="loading">جاري المعالجة... ⏳<br><small>الرجاء الانتظار</small></div>
    ''' + result + '</div></body></html>'

    return page

@app.route('/download/<filename>')
def download(filename):
    return send_file('/tmp/' + filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
    
