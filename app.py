from flask import Flask, request, send_file
import ezdxf, tempfile, os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            file = request.files['dxf_file']
            if not file:
                return "ارفع ملف DXF"

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
                        msp.add_circle(e.get_points()[0], radius=0.5, dxfattribs={'color': 1})
                elif e.dxftype() == 'LINE':
                    errors += 1
                    msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})

            fixed_path = os.path.join(temp_dir, 'fixed_' + file.filename)
            doc.saveas(fixed_path)

            return f'''
            <h3>تم الفحص بنجاح!</h3>
            <p>عدد الأخطاء: {errors}</p>
            <a href="/download/{os.path.basename(fixed_path)}">
                <button style="padding:10px 20px; background:green; color:white; border:none; font-size:16px;">
                    تحميل الملف المصح DXF
                </button>
            </a>
            <br><br>
            <a href="/">فحص ملف ثاني</a>
            '''

        except Exception as e:
            return f"خطأ: {str(e)}"

    return '''
    <h3>فاحص DXF - إصلاح تلقائي</h3>
    <form method="POST" enctype="multipart/form-data" onsubmit="showLoading()">
        <input type="file" name="dxf_file" accept=".dxf" required>
        <input type="submit" value="فحص وإصلاح" style="padding:8px 15px;">
    </form>

    <div id="loading" style="display:none; margin-top:20px;">
        <p style="font-size:18px;">جاري المعالجة... ⏳</p>
    </div>

    <script>
    function showLoading() {
        document.getElementById('loading').style.display = 'block';
    }
    </script>
    '''

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join('/tmp', filename), as_attachment=True)

if __name__ == '__main__':
    app.run()
