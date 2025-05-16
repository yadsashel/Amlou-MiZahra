import os
import sys
import csv, io
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, flash, jsonify, request, session, redirect, url_for, send_file, make_response, abort, json
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from functools import wraps
from flask_cors import CORS
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get secret keys
REGLOG_KEY = os.environ.get('REGLOG_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Initialize Firebase Admin
firebase_key = os.environ.get("FIREBASE_KEY")
firebase_dict = json.loads(firebase_key)
cred = credentials.Certificate(firebase_dict)
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()


# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)
CORS(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        secret_code = request.form.get("secret_code", "").strip()

        if secret_code != REGLOG_KEY:
            flash("رمز التسجيل غير صحيح. حاول مرة أخرى.", "error")
            return redirect(url_for("register"))

        # Check if user already exists in Firestore
        user_ref = db.collection("users").document(username)
        if user_ref.get().exists:
            flash("هذا المستخدم مسجل بالفعل.", "error")
            return redirect(url_for("register"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save to Firestore
        user_ref.set({
            "username": username,
            "password": hashed_password
        })

        flash("تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        secret_code = request.form.get("secret", "").strip()

        if secret_code != REGLOG_KEY:
            flash("رمز التسجيل غير صحيح. حاول مرة أخرى.", "error")
            return redirect(url_for("login"))

        # Fetch user from Firestore
        user_ref = db.collection("users").document(username)
        user_doc = user_ref.get()

        if user_doc.exists:
            stored_password = user_doc.to_dict().get("password")
            if check_password_hash(stored_password, password):
                session.permanent = True
                session["username"] = username
                flash("تم تسجيل الدخول بنجاح.", "success")
                return redirect(url_for("admin"))

        flash("بيانات الدخول غير صحيحة. حاول مرة أخرى.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return abort(404)
        return f(*args, **kwargs)
    return decorated_function

# Protect admin route
@app.route('/admin')
@login_required
def admin():
    orders_ref = db.collection("orders").stream()
    orders = []

    for doc in orders_ref:
        order = doc.to_dict()
        order["doc_id"] = doc.id  # ✅ Add document ID to each order
        orders.append(order)

    return render_template("admin.html", orders=orders, username=session["username"])


@app.route('/update-order', methods=['POST'])
@login_required
def update_order():
    try:
        doc_id = request.form.get("doc_id")
        updated_data = {
            "name": request.form.get("customer_name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "city": request.form.get("city", "").strip(),
            "address": request.form.get("address", "").strip(),
            "quantity": request.form.get("quantity", "").strip(),
            "product": request.form.get("product", "").strip(),
            "total": request.form.get("total", "").strip()
        }
        db.collection("orders").document(doc_id).update(updated_data)
        flash("✅ تم حفظ التغييرات بنجاح", "success")
    except Exception as e:
        print("Update error:", e)
        flash("❌ حدث خطأ أثناء تحديث الطلب", "error")
    return redirect(url_for("admin"))

@app.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    orders_ref = db.collection("orders")
    orders = [doc.to_dict() for doc in orders_ref.stream()]

    headers = ['الاسم الكامل', 'رقم الهاتف', 'المدينة', 'العنوان', 'الكمية', 'المنتج', 'الإجمالي']
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)

    for order in orders:
        writer.writerow([
            order.get("name", ""),
            f'="{order.get("phone", "")}"',
            order.get("city", ""),
            order.get("address", ""),
            order.get("quantity", ""),
            order.get("product", ""),
            f'="{order.get("total", "")}"'
        ])

    output = make_response('\ufeff' + si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=orders.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

@app.route('/submit_order/<int:product_id>', methods=['POST'])
def submit_order(product_id):
    name = request.form.get("customerName", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    address = request.form.get("address", "").strip()
    quantity = int(request.form.get("quantity", "1").strip())

    product_info = {
        1: ("أملو سبايسي بالأعشاب", 70),
        2: ("أملو بالتمر", 90),
        3: ("أملو أملو بالشوكولاتة الداكنة ", 77),
        4: ("أملو بالبستاش", 150),
        5: ("أملو ملكي فاخر", 190),
    }

    product_name, unit_price = product_info.get(product_id, ("منتج غير معروف", 0))
    total_price = unit_price * quantity

    db.collection("orders").add({
        "name": name,
        "phone": phone,
        "city": city,
        "address": address,
        "quantity": quantity,
        "product": product_name,
        "total": total_price
    })

    flash("✅ تم إرسال طلبك بنجاح، سنتواصل معك قريباً", "success")
    return redirect(url_for("product"))


@app.route('/order_1')
def order_1():
    return render_template('order_1.html')

@app.route('/order_2')
def order_2():
    return render_template('order_2.html')

@app.route('/order_3')
def order_3():
    return render_template('order_3.html')

@app.route('/order_4')
def order_4():
    return render_template('order_4.html')

@app.route('/order_5')
def order_5():
    return render_template('order_5.html')

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == "__main__":
    app.run(debug=True)