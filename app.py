from flask import Flask, request, send_file
import ezdxf, os

app = Flask(__name__)

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

                result = f'<div style="margin-top:20px"><h3>تم الفحص بنجاح!</h3><p>الأخطاء: {errors}</p><a href="/download/{fixed_filename}"><button style="padding:15px 30px; background:green; color:white; border:none; border-radius:5px; font-size:18px;">تحميل DXF المصح</button></a></div>'
                os.remove(filepath)

        except Exception as e:
            result = f'<p style="color:red">خطأ: {str(e)}</p>'

    page = f'''
    <!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{{font-family:Arial;background:#f5f5f5;padding:20px;text-align:center}}
   .box{{background:white;padding:30px;border-radius:10px;max-width:500px;margin:50px auto}}</style>
    </head><body><div class="box">
    <h2>فاحص DXF</h2>
    <form method="POST" enctype="multipart/form-data">
    <input type="file" name="dxf_file" accept=".dxf" required><br><br>
    <button type="submit">فحص وإصلاح</button></form>
    {result}</div></body></html>'''

    return page

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join('/tmp', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return 'الملف انتهت صلاحيته. ارفع الملف مرة ثانية وفحصه', 404

if __name__ == '__main__':
    app.run()
    
