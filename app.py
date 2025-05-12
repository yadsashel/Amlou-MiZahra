import os
import sys
import csv, io
from flask import Flask, render_template, flash, jsonify, request, session, redirect, url_for, send_file, make_response, abort
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from functools import wraps
from flask_cors import CORS

load_dotenv()

REGLOG_KEY = os.environ.get('REGLOG_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')


app = Flask(__name__)
CORS(app)

app.secret_key = SECRET_KEY

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
        secret_code = request.form.get("secret_code", "").strip()  # Get the secret from the form

        # Check if the secret is correct
        if secret_code != REGLOG_KEY:
            flash("رمز التسجيل غير صحيح. حاول مرة أخرى.", "error")
            return redirect(url_for("register"))

        # Check if the user already exists
        if os.path.exists('users.csv'):
            with open('users.csv', "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == username:
                        flash("هذا المستخدم مسجل بالفعل.", "error")
                        return redirect(url_for("register"))

        # Register the new user
        with open('users.csv', "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([username, password])  # Store only username and password

        flash("تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        secret_code = request.form.get("secret", "").strip()  # Get the secret from the form

        # Check if the secret is correct
        if secret_code != REGLOG_KEY:
            flash("رمز التسجيل غير صحيح. حاول مرة أخرى.", "error")
            return redirect(url_for("login"))

        # Check if the user exists in the CSV file
        if os.path.exists('users.csv'):
            with open('users.csv', "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == username and row[1] == password:
                        session["username"] = username  # Create a session for the logged-in user
                        flash("تم تسجيل الدخول بنجاح.", "success")
                        return redirect(url_for("admin"))  # Redirect to the admin page

        flash("بيانات الدخول غير صحيحة. حاول مرة أخرى.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return abort(404)  # Show 404 page if not logged in
        return f(*args, **kwargs)
    return decorated_function


# Protect admin route
@app.route("/admin")
@login_required
def admin():
    orders = []
    if os.path.exists("record.csv"):
        with open("record.csv", "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    orders.append(row)
    return render_template("admin.html", orders=orders)



@app.route('/update-order', methods=['POST'])
def update_order():
    try:
        index = int(request.form.get("row_index", -1))
        if index < 0:
            flash("رقم الطلب غير صالح", "error")
            return redirect(url_for("admin"))

        updated_row = [
            request.form.get("customer_name", "").strip(),
            request.form.get("phone", "").strip(),
            request.form.get("city", "").strip(),
            request.form.get("address", "").strip(),
            request.form.get("quantity", "").strip(),
            request.form.get("product", "").strip(),
            request.form.get("total", "").strip()
        ]

        # Read all orders
        with open("record.csv", "r", encoding="utf-8") as file:
            lines = list(csv.reader(file))

        if 0 <= index < len(lines):
            lines[index] = updated_row  # Update the order
        else:
            flash("رقم الطلب غير موجود", "error")
            return redirect(url_for("admin"))

        # Write back updated data
        with open("record.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(lines)

        flash("✅ تم حفظ التغييرات بنجاح", "success")

    except Exception as e:
        print("Update error:", e)
        flash("❌ حدث خطأ أثناء تحديث الطلب", "error")

    return redirect(url_for("admin"))


@app.route('/export_csv', methods=['POST'])
def export_csv():
    with open('record.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    headers = ['الاسم الكامل', 'رقم الهاتف', 'المدينة', 'العنوان', 'الكمية', 'المنتج', 'الإجمالي']

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(headers)

    for row in rows:
        # Force phone and total to be text using ="..."
        clean_row = [
            row[0],                            # Name
            f'="{row[1]}"',                   # Phone as text
            row[2],                            # City
            row[3],                            # Address
            row[4],                            # Quantity
            row[5],                            # Product
            f'="{row[6]}"'                    # Total (optional)
        ]
        writer.writerow(clean_row)

    output = make_response('\ufeff' + si.getvalue())  # Add BOM for Arabic
    output.headers["Content-Disposition"] = "attachment; filename=orders.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"

    return output


@app.route('/submit_order/<int:product_id>', methods=['POST'])
def submit_order(product_id):
    name = request.form.get("customerName", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    address = request.form.get("address", "").strip()
    quantity = request.form.get("quantity", "1").strip()

    # Optional: Add validation here

    # Define product names and prices
    product_info = {
        1: ("أملو تقليدي", 120),
        2: ("أملو خاص", 150),
        3: ("أملو بزيت الزيتون", 180),
        4: ("أملو بالعسل الحر", 200),
        5: ("أملو ممتاز", 220),
        6: ("أملو بريميوم", 250)
    }

    product_name, unit_price = product_info.get(product_id, ("منتج غير معروف", 0))
    total_price = unit_price * int(quantity)

    with open("record.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, phone, city, address, quantity, product_name, total_price])

    flash("✅ تم إرسال طلبك بنجاح، سنتواصل معك قريباً", "success")
    return redirect(url_for("product"))


# Protect view-workers route
@app.route('/view-workers')
@login_required
def view_workers():
    workers = []
    if os.path.exists('users.csv'):
        with open('users.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            workers = list(reader)
    return render_template('view_workers.html', workers=workers)


# Protect view-orders route
@app.route('/view-orders')
@login_required
def view_orders():
    orders = []
    if os.path.exists('record.csv'):
        with open('record.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            orders = list(reader)
    return render_template('view_orders.html', orders=orders)


@app.route('/delete-worker/<int:index>')
@login_required
def delete_worker(index):
    if os.path.exists('users.csv'):
        with open('users.csv', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if 0 <= index < len(rows):
            del rows[index]
            with open('users.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
    return redirect(url_for('view_workers'))


@app.route('/delete-order/<int:index>')
@login_required
def delete_order(index):
    if os.path.exists('record.csv'):
        with open('record.csv', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if 0 <= index < len(rows):
            del rows[index]
            with open('record.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
    return redirect(url_for('view_orders'))

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

@app.route('/order_6')
def order_6():
    return render_template('order_6.html')

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)