import os
import tempfile
from flask import Flask, request, send_file
import ezdxf
import pandas as pd

app = Flask(__name__)
TEMP_DIR = tempfile.gettempdir()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file: return "الرجاء اختيار ملف", 400
        
        path = os.path.join(TEMP_DIR, file.filename)
        file.save(path)
        out_path = os.path.join(TEMP_DIR, "تقرير_الحصر.xlsx")
        
        try:
            doc = ezdxf.readfile(path)
            msp = doc.modelspace()
            lines, areas, blocks, errors = [], [], [], []
            
            for e in msp:
                if e.dxftype() == 'LINE':
                    lines.append({'الطبقة': e.dxf.layer, 'الطول': round((e.dxf.start - e.dxf.end).magnitude, 2)})
                elif e.dxftype() == 'LWPOLYLINE':
                    if e.closed:
                        areas.append({'الطبقة': e.dxf.layer, 'المساحة': round(e.area, 2)})
                    else:
                        errors.append({'السبب': 'بوليلاين غير مغلق', 'الطبقة': e.dxf.layer, 'إحداثيات': str(e.get_point_at(0))})
                elif e.dxftype() == 'INSERT':
                    blocks.append({'الرمز': e.dxf.name, 'الطبقة': e.dxf.layer})
            
            with pd.ExcelWriter(out_path) as writer:
                pd.DataFrame(lines).groupby('الطبقة')['الطول'].sum().reset_index().to_excel(writer, sheet_name='الأطوال', index=False)
                pd.DataFrame(areas).groupby('الطبقة')['المساحة'].sum().reset_index().to_excel(writer, sheet_name='المساحات', index=False)
                pd.DataFrame(blocks).groupby(['الرمز', 'الطبقة']).size().reset_index(name='العدد').to_excel(writer, sheet_name='الرموز', index=False)
                pd.DataFrame(errors).to_excel(writer, sheet_name='تنبيهات_التعديل', index=False)
            
            return send_file(out_path, as_attachment=True)
        except Exception as e:
            return f"خطأ في الحصر: {str(e)}"
            
    return "<html dir='rtl'><body><h1>أداة الحصر الهندسي</h1><form method='post' enctype='multipart/form-data'><input type='file' name='file' accept='.dxf' required><button type='submit'>تصدير الحصر</button></form></body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
                    
