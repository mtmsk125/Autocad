    if not file: return "لا يوجد ملف", 400
    ipath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(ipath)
    oname = "BOQ_" + file.filename.rsplit('.', 1)[0] + ".xlsx"
    opath = os.path.join(UPLOAD_FOLDER, oname)
    
    success = run_cad(ipath, opath) if file.filename.lower().endswith('.dxf') else run_pdf(ipath, opath)
    if success: return send_file(opath, as_attachment=True)
    return "خطأ في المعالجة", 500

def run_cad(ipath, opath):
    try:
        doc = ezdxf.readfile(ipath)
        msp = doc.modelspace()
        recs = [{"الموقع": e.dxf.layer, "الطبقة": e.dxftype(), "الوحدة": "عدد", "الكمية": 1} for e in msp]
        return save_xl(recs, opath)
    except: return False

def run_pdf(ipath, opath):
    try:
        doc = fitz.open(ipath)
        recs = [{"الموقع": f"صفحة {i+1}", "الطبقة": "نص", "الوحدة": "عدد", "الكمية": 1} for i, p in enumerate(doc)]
        return save_xl(recs, opath)
    except: return False

def save_xl(recs, opath):
    try:
        pd.DataFrame(recs).to_excel(opath, index=False)
        return True
    except: return False

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run()
    
