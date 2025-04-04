from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime, timedelta
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="host",
    password="root",
    database="vendor"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vendor')
def vendor():
    # Fetch vendors for the contract dropdown
    cursor.execute("SELECT id, name FROM vendors")
    vendors = cursor.fetchall()
    return render_template('vendor.html', vendors=vendors)

@app.route("/add_vendor", methods=["POST"])
def add_vendor():
    name = request.form["vendor-name"]
    business_id = request.form["business-id"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]
    category = request.form["category"]
    expiry_date = request.form["expiry-date"]

    query = "INSERT INTO vendors (name, business_id, phone, email, address, category, contract_expiry) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (name, business_id, phone, email, address, category, expiry_date))
    db.commit()
    return redirect("/")

@app.route('/vendor_p')
def vendor_p():
    cursor.execute("SELECT name, business_id, category, phone, contract_expiry, address, email FROM vendors")
    vendors = cursor.fetchall()
    return render_template('vendor_p.html', vendors=vendors)


@app.route('/delete_vendor')
def delete_vendor():
    business_id = request.args.get('business_id')
    cursor = db.cursor()
    cursor.execute("DELETE FROM vendors WHERE business_id = %s", (business_id,))
    db.commit()
    return '', 204

@app.route("/update_vendor", methods=["POST"])
def update_vendor():
    data = request.get_json()
    # Extract fields from `data` and update in MySQL
    query = """
        UPDATE vendors SET 
            name=%s, category=%s, contact=%s, expiry=%s, address=%s, email=%s
        WHERE business_id=%s
    """
    values = (
        data["name"],
        data["category"],
        data["contact"],
        data["expiry"],
        data["address"],
        data["email"],
        data["id"]
    )
    cursor.execute(query, values)
    db.commit()
    return jsonify({"message": "Vendor updated"})



@app.route('/contract')
def contract():
    # Fetch vendors for the dropdown
    cursor.execute("SELECT id, name FROM vendors")
    vendors = cursor.fetchall()
    
    # Fetch contracts
    cursor.execute("SELECT * FROM contracts")
    contracts = cursor.fetchall()
    
    return render_template('contract.html', vendors=vendors, contracts=contracts)

@app.route('/add_contract', methods=['POST'])
def add_contract():
    vendor_id = request.form["contract-vendor"]
    contract_type = request.form["contract-type"]
    start_date = request.form["start-date"]
    end_date = request.form["end-date"]
    contract_value = request.form["contract-value"]
    terms_conditions = request.form["contract-terms"]

    query = "INSERT INTO contracts (vendor_id, contract_type, start_date, end_date, contract_value, contract_terms) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (vendor_id, contract_type, start_date, end_date, contract_value, terms_conditions))
    db.commit()
    
    return redirect("/contract")

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)