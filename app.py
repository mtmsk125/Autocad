from flask import Flask, request, send_file, render_template_string
import urllib.request
import ezdxf
import os

app = Flask(__name__)

@app.route('/download/<filename>')
def download(filename):
    p = os.path.join('/tmp', filename)
    return send_file(p, as_attachment=True) if os.path.exists(p) else ("File not found", 404)

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
                            p = e.get_points()
                            pts.append({"x": float(p[0][0]), "y": float(p[0][1])})
                    elif e.dxftype() == 'LINE':
                        err += 1
                        pts.append({"x": float(e.dxf.start.x), "y": float(e.dxf.start.y)})
                f_name = 'fixed_' + f_name
                doc.saveas(os.path.join('/tmp', f_name))
                os.remove(fpath)
                
                if is_ar:
                    res = f'''<div class="rc"><h3>✓ تم الفحص والإصلاح بنجاح!</h3><p>الأخطاء المصححة: <strong>{err}</strong></p><button type="button" onclick="openPaymentModal()" class="btn" style="background:#10b981;margin-top:10px;">تحميل ملف DXF السليم 🚀</button></div>'''
                else:
                    res = f'''<div class="rc"><h3>✓ Scan & Fix Completed!</h3><p>Errors Fixed: <strong>{err}</strong></p><button type="button" onclick="openPaymentModal()" class="btn" style="background:#10b981;margin-top:10px;">Download Clean DXF 🚀</button></div>'''
        except Exception as e: res = f'<div class="ec">⚠️ Error: {str(e)}</div>'

    # استدعاء الواجهة الفخمة والكاملة المخزنة سحابياً بأمان عبر مكتبة بايثون الأساسية
    try:
        req = urllib.request.Request("https://pastebin.com", headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
    except:
        return "Server Error / خطأ في السيرفر", 500

    d_url = f"/download/{f_name}" if f_name else "#"
    
    # دمج البيانات والخيارات بذكاء وأمان داخل الصفحة السحابية الجاهزة
    html_page = html_page.replace('USE_RESULT', res)
    html_page = html_page.replace('USE_DOWNLOAD_URL', d_url)
    html_page = html_page.replace('USE_JS_PTS', str(pts))
    html_page = html_page.replace('USE_DIR', 'rtl' if is_ar else 'ltr')
    html_page = html_page.replace('USE_LANG', 'ar' if is_ar else 'en')

    return render_template_string(html_page)

if __name__ == '__main__':
    app.run(debug=True)


             
