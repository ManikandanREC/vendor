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
    return render_template('vendor.html')

@app.route("/add_vendor", methods=["POST"])
def add_vendor():
    name = request.form["vendor-name"]
    business_id = request.form["business-id"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]
    category = request.form["category"]
    expiry_date = request.form["expiry-date"]

    query = "INSERT INTO vendors (name, business_id, phone, email, address, category,  contract_expiry) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (name, business_id, phone, email, address, category, expiry_date))
    db.commit()
    return redirect("/")

@app.route('/vendor_p')
def vendor_p():
    cursor.execute("SELECT name, business_id, category, phone, contract_expiry FROM vendors")
    vendors = cursor.fetchall()
    return render_template('vendor_p.html', vendors=vendors)


@app.route('/contract')
def contract():
    cursor.execute("SELECT id, business_id FROM vendors")  # Fetch vendor id and business_id
    vendors = cursor.fetchall()
    return render_template('contract.html', vendors=vendors)



@app.route('/add_contract', methods=['POST'])
def add_contract():
    vendor_id = request.form["contract-vendor"]  # Ensure vendor_id is from vendors.id
    contract_type = request.form["contract-type"]
    start_date = request.form["start-date"]
    end_date = request.form["end-date"]
    contract_value = request.form["contract-value"]
    terms_conditions = request.form["contract-terms"]

    query = "INSERT INTO contracts (vendor_id, contract_type, start_date, end_date, contract_value, contract_terms) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (vendor_id, contract_type, start_date, end_date, contract_value, terms_conditions))
    db.commit()
    
    return redirect("/contract")

@app.route('/contract-management')
def contract_management():
    cursor.execute("SELECT c.id, v.business_id, c.contract_type, c.start_date, c.end_date, c.contract_value FROM contracts c JOIN vendors v ON c.vendor_id = v.id")
    contracts = cursor.fetchall()

    today = datetime.today().date()
    contract_list = []
    
    for contract in contracts:
        contract_id, vendor_name, contract_type, start_date, end_date, contract_value = contract
        end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
        
        if end_date < today:
            status_class = "expired"
            status_text = "Expired"
        elif end_date < today + timedelta(days=30):
            status_class = "expiring"
            status_text = "Expiring Soon"
        else:
            status_class = "active"
            status_text = "Active"
        
        contract_list.append({
            "contract_id": contract_id,
            "vendor_name": vendor_name,
            "contract_type": contract_type,
            "start_date": start_date,
            "end_date": end_date,
            "contract_value": contract_value,
            "status_class": f"status-{status_class}",
            "status_text": status_text
        })

    return render_template("contract-management.html", contracts=contract_list)


@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
