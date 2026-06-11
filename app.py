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
                msp = doc.modelspace() # انتبه القوسين هون ()
                errors = 0

                for e in msp.query('LWPOLYLINE LINE'):
                    if e.dxftype() == 'LWPOLYLINE':
                        if not e.closed:
                            errors += 1
                            msp.add_circle(e.get_points()[0], radius=0.5, dxfattribs={'color': 1})
                    elif e.dxftype() == 'LINE':
                        errors += 1
                        msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})

                fixed_path = os.path.join(temp_dir, 'fixed_' + file.filename)
                doc.saveas(fixed_path)

                result = '<div><h3>تم الفحص بنجاح!</h3><p>الأخطاء: ' + str(errors) + '</p><a href="/download/' + os.path.basename(fixed_path) + '"><button style="padding:15px; background:green; color:white;">تحميل DXF المصح</button></a></div>'
                os.remove(filepath)

        except Exception as e:
            result = '<p style="color:red">خطأ: ' + str(e) + '</p>'

    # الصفحة الأساسية مع "جاري المعالجة"
    page = '''
    <!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
    <style>body{font-family:Arial;background:#f5f5f5;padding:20px;text-align:center}
   .box{background:white;padding:30px;border-radius:10px;max-width:500px;margin:auto}
    button{padding:12px 30px;background:#007bff;color:white;border:none;border-radius:5px;font-size:16px}
   .loading{display:none;margin-top:20px;font-size:18px;color:#007bff}</style>
    </head><body><div class="box">
    <h2>فاحص DXF</h2>
    <form method="POST" enctype="multipart/form-data" onsubmit="document.getElementById('loading').style.display='block'">
    <input type="file" name="dxf_file" accept=".dxf" required><br><br>
    <button>فحص وإصلاح</button></form>
    <div id="loading" class="loading">جاري المعالجة... ⏳</div>
    ''' + result + '</div></body></html>'

    return page

@app.route('/download/<filename>')
def download(filename):
    return send_file('/tmp/' + filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
    
