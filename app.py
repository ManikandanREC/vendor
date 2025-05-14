from flask import Flask, render_template, request, redirect, jsonify, session, flash,url_for
import mysql.connector
from datetime import date, timedelta
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages and session

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="host",
        password="root",  # Correct if "root" is your password; change if needed
        database="k_final"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vendors')
def vendors():
    return redirect("/vendor-management")


@app.route("/contracts")
def contracts():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch contract details with vendor names
    cursor.execute("""
        SELECT contracts.contract_title, vendors.name, contracts.start_date, 
               contracts.end_date, contracts.contract_value
        FROM contracts
        JOIN vendors ON contracts.vendor_id = vendors.id
    """)
    contracts = cursor.fetchall()

    # Fetch vendors for the dropdown
    cursor.execute("SELECT id, name FROM vendors")
    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("contract-management.html", 
                           contracts=contracts,
                           vendors=vendors,  # <- Pass vendors to the template
                           current_date=date.today(),
                           near_expiry_date=date.today() + timedelta(days=30))

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/add_vendor", methods=["POST"])
def add_vendor():
    if request.method == "POST":
        # Extracting form data
        name = request.form["vendor-name"]
        business_id = request.form["business-id"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]
        category = request.form["category"]
        expiry_date = request.form["expiry-date"]

        # Connect to the database and insert the data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO vendors (name, business_id, phone, email, address, category, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, business_id, phone, email, address, category, expiry_date))
        conn.commit()

        cursor.close()
        conn.close()

        flash('Vendor added successfully!', 'success')
        return redirect("/vendor-profiles")

@app.route("/vendor-management")
def vendor_management():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to select vendor display data (name, category, email, phone)
    cursor.execute("SELECT name, category, email, phone FROM vendors")
    vendor_display_data = cursor.fetchall()

    # Query to select vendor ID and name for the contract form dropdown
    cursor.execute("SELECT id, name FROM vendors")
    vendor_choices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'vendor-management.html',
        vendors=vendor_display_data,
        vendor_choices=vendor_choices
    )



@app.route('/vendor-profiles')
def vProfile():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, category, email, phone, address, expiry_date FROM vendors")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    colors = ['#ee9e43', '#c9375e', '#4cc9f0', '#560bad', '#3a86ff', '#ff006e']

    vendors = []
    for i, row in enumerate(results):
        vendor = {
            'name': row[0],
            'category': row[1],
            'email': row[2],
            'phone': row[3],
            'address': row[4],
            'contract_expiry': row[5],
            'color': colors[i % len(colors)]
        }
        vendors.append(vendor)

    return render_template('vendor-profiles.html', vendors=vendors)


@app.route('/add_contract', methods=['POST'])
def add_contract():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get form data
        vendor_id = request.form.get("contract-vendor")
        contract_title = request.form.get("contract-title")
        contract_type = request.form.get("contract-type")
        start_date = request.form.get("start-date")
        end_date = request.form.get("end-date")
        contract_value = request.form.get("contract-value")
        terms_conditions = request.form.get("contract-terms")

        # Validate required fields
        if not all([vendor_id, contract_title, contract_type, start_date, end_date, contract_value]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("contracts"))

        # Debug: Print to console
        print(f"Contract Title: {contract_title}")
        print(f"Vendor ID: {vendor_id}, Type: {contract_type}, Start: {start_date}, End: {end_date}, Value: {contract_value}")

        # Insert query
        query = """
            INSERT INTO contracts 
            (vendor_id, contract_title, contract_type, start_date, end_date, contract_value, contract_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            vendor_id, contract_title, contract_type,
            start_date, end_date, contract_value, terms_conditions
        ))
        conn.commit()

        flash("Contract added successfully!", "success")

    except Exception as e:
        conn.rollback()  # rollback to avoid locking or partial insertions
        flash(f"Error adding contract: {str(e)}", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("contracts"))




if __name__ == '__main__':
    app.run(debug=True)
