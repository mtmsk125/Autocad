from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import stripe, ezdxf, fitz, os, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

app = Flask(__name__)
app.config.update(SECRET_KEY='key999', SQLALCHEMY_DATABASE_URI='sqlite:///users.db')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

stripe.api_key = "sk_test_YOUR_STRIPE_SECRET_KEY"
STRIPE_PRICE_ID = "price_YOUR_STRIPE_PLAN_ID"
YOUR_DOMAIN = "https://YOUR_APP_NAME.onrender.com"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))

# [هنا نضع دالة الـ STYLE المذكورة سابقاً]

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if not current_user.is_premium: return "غير مصرح لك", 403
    file = request.files.get('file')
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
