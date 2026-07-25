import os
import json
import pymysql
from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Database configuration
# In production: use AWS Secrets Manager
# For this lab: environment variables
DB_HOST = os.environ.get('DB_HOST', 'ahamed-banking-db.cb2sy22mueo0.ap-south-1.rds.amazonaws.com')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'BankingApp2026!')
DB_NAME = os.environ.get('DB_NAME', 'bankingapp')

def get_db_connection():
    """Create and return a database connection"""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

# HTML template for the banking dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Banking Dashboard - Ahamed Eshak</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { color: #e94560; }
        .card { background: #0f3460; padding: 20px; border-radius: 8px; margin: 15px 0; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #16213e; padding: 10px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #16213e; }
        .credit { color: #00ff88; }
        .debit { color: #ff4757; }
        input, select { padding: 8px; margin: 5px; border-radius: 4px; border: none; }
        button { background: #e94560; color: white; padding: 10px 20px;
                 border: none; border-radius: 4px; cursor: pointer; }
        .status { padding: 3px 8px; border-radius: 4px; font-size: 12px; }
        .approved { background: #00ff88; color: #000; }
        .flagged { background: #ffa502; color: #000; }
    </style>
</head>
<body>
    <h1>🏦 Banking Transaction Dashboard</h1>
    <p>Engineer: Shaik Ahamed Eshak Nowfal | Region: ap-south-1 Mumbai</p>

    <div class="card">
        <h3>Add New Transaction</h3>
        <input type="text" id="account" placeholder="Account Number" value="ACC001234">
        <input type="number" id="amount" placeholder="Amount (₹)" value="25000">
        <select id="type">
            <option value="credit">Credit</option>
            <option value="debit">Debit</option>
        </select>
        <input type="text" id="description" placeholder="Description" value="Test transaction">
        <button onclick="addTransaction()">Submit Transaction</button>
        <p id="result"></p>
    </div>

    <div class="card">
        <h3>Transaction History</h3>
        <table>
            <tr><th>ID</th><th>Account</th><th>Amount</th><th>Type</th>
                <th>Description</th><th>Date</th></tr>
            {% for txn in transactions %}
            <tr>
                <td>{{ txn.id }}</td>
                <td>{{ txn.account_number }}</td>
                <td class="{{ txn.transaction_type }}">₹{{ "{:,.2f}".format(txn.amount) }}</td>
                <td>{{ txn.transaction_type.upper() }}</td>
                <td>{{ txn.description }}</td>
                <td>{{ txn.created_at }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <script>
    async function addTransaction() {
        const data = {
            account_number: document.getElementById('account').value,
            amount: parseFloat(document.getElementById('amount').value),
            transaction_type: document.getElementById('type').value,
            description: document.getElementById('description').value
        };
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        document.getElementById('result').innerHTML =
            `Status: <strong>${result.status}</strong> | ID: ${result.id}`;
        setTimeout(() => location.reload(), 1500);
    }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard showing all transactions"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 20"
            )
            transactions = cursor.fetchall()
        conn.close()
        return render_template_string(DASHBOARD_HTML, transactions=transactions)
    except Exception as e:
        return f"<h1>Database Error</h1><p>{str(e)}</p><p>Check RDS connection</p>", 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """API endpoint returning transactions as JSON"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 50"
            )
            transactions = cursor.fetchall()
        conn.close()
        # Convert datetime objects to strings for JSON
        for txn in transactions:
            if txn.get('created_at'):
                txn['created_at'] = str(txn['created_at'])
            txn['amount'] = float(txn['amount'])
        return jsonify({'transactions': transactions, 'count': len(transactions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """API endpoint to add a new transaction"""
    try:
        data = request.get_json()

        account_number = data.get('account_number')
        amount = float(data.get('amount', 0))
        transaction_type = data.get('transaction_type', 'debit')
        description = data.get('description', '')

        # Validate
        if not account_number:
            return jsonify({'error': 'account_number required'}), 400
        if amount <= 0:
            return jsonify({'error': 'amount must be positive'}), 400
        if transaction_type not in ['credit', 'debit']:
            return jsonify({'error': 'invalid transaction_type'}), 400

        # Determine status
        status = 'FLAGGED_FOR_REVIEW' if amount > 100000 else 'APPROVED'

        # Insert into RDS
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO transactions
                   (account_number, amount, transaction_type, description)
                   VALUES (%s, %s, %s, %s)""",
                (account_number, amount, transaction_type, description)
            )
            new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'id': new_id,
            'account_number': account_number,
            'amount': amount,
            'status': status,
            'message': 'Transaction recorded successfully',
            'processed_at': datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint for ALB"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        'status': 'healthy' if 'connected' in db_status else 'degraded',
        'database': db_status,
        'service': 'banking-dashboard',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

