from flask import Flask, request, render_template, send_file
import ezdxf, os, uuid

app = Flask(__name__)

UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# DXF ENGINE (MVP)
# =========================
def analyze_and_fix(path):
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    issues = {"splines":0, "blocks":0, "open":0, "dup":0}
    seen = set()

    # SPLINE → POLYLINE
    for s in list(msp.query("SPLINE")):
        try:
            pts = list(s.flattening(0.5))
            msp.add_lwpolyline(pts)
            msp.delete_entity(s)
            issues["splines"] += 1
        except:
            pass

    # BLOCKS
    for b in list(msp.query("INSERT")):
        try:
            b.explode()
            msp.delete_entity(b)
            issues["blocks"] += 1
        except:
            pass

    # OPEN POLYLINES
    for p in msp.query("LWPOLYLINE"):
        try:
            if not p.closed:
                p.close()
                issues["open"] += 1
        except:
            pass

    # DUPLICATES
    for e in list(msp):
        try:
            k = (e.dxftype(), getattr(e.dxf, "layer", "0"))
            if k in seen:
                msp.delete_entity(e)
                issues["dup"] += 1
            else:
                seen.add(k)
        except:
            pass

    score = 100
    score -= issues["splines"] * 10
    score -= issues["blocks"] * 8
    score -= issues["open"] * 5
    score -= issues["dup"] * 3

    status = "READY" if score >= 85 else "FIXED" if score >= 60 else "RISKY"

    return doc, issues, max(score, 0), status


# =========================
# LANDING PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# UPLOAD + PROCESS
# =========================
@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    uid = str(uuid.uuid4())

    in_path = os.path.join(UPLOAD_DIR, uid + "_" + f.filename)
    out_path = os.path.join(OUTPUT_DIR, "fixed_" + uid + "_" + f.filename)

    f.save(in_path)

    doc, issues, score, status = analyze_and_fix(in_path)
    doc.saveas(out_path)

    return render_template(
        "result.html",
        score=score,
        status=status,
        file=os.path.basename(out_path),
        issues=issues
    )


# =========================
# DOWNLOAD
# =========================
@app.route("/download/<file>")
def download(file):
    path = os.path.join(OUTPUT_DIR, file)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
