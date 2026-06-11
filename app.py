from flask import Flask, request
import ezdxf, tempfile, os, traceback

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            file = request.files['dxf_file']
            if not file:
                return "ارفع ملف DXF"

            temp_dir = tempfile.mkdtemp()
            filepath = os.path.join(temp_dir, file.filename)
            file.save(filepath)

            errors = []
            doc = ezdxf.readfile(filepath)
            msp = doc.modelspace()

            for e in msp.query('LWPOLYLINE LINE'):
                try:
                    if e.dxftype() == 'LWPOLYLINE':
                        if not e.closed:
                            errors.append("خط مفتوح")
                            msp.add_circle(e.get_points()[0], radius=0.5, dxfattribs={'color': 1})
                    elif e.dxftype() == 'LINE':
                        errors.append("خط مفرد")
                        msp.add_circle(e.dxf.start, radius=0.5, dxfattribs={'color': 1})
                except Exception as e2:
                    errors.append(f"خطأ بمعالجة عنصر: {str(e2)}")

            return f"فحص انتهى بنجاح. الأخطاء: {len(errors)}<br>{'<br>'.join(errors)}"

        except Exception as e:
            return f"خطأ عام: {str(e)}<br><pre>{traceback.format_exc()}</pre>"

    return '<form method="POST" enctype="multipart/form-data"><input type="file" name="dxf_file"><input type="submit" value="فحص"></form>'

if __name__ == '__main__':
    app.run()
