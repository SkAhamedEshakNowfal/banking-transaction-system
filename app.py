import os
import json
import boto3
import pymysql
from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_HOST = os.environ.get('DB_HOST', '')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'BankingApp2026!')
DB_NAME = os.environ.get('DB_NAME', 'bankingapp')

# SNS configuration
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:818593257957:ahamed-payment-events'
AWS_REGION = 'ap-south-1'

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def publish_to_sns(transaction_data):
    """Publish transaction event to SNS for async processing"""
    try:
        sns_client = boto3.client('sns', region_name=AWS_REGION)
        message = {
            'transaction_id': str(transaction_data.get('id', 'UNKNOWN')),
            'account_number': transaction_data.get('account_number'),
            'amount': float(transaction_data.get('amount', 0)),
            'transaction_type': transaction_data.get('transaction_type'),
            'description': transaction_data.get('description', ''),
            'status': transaction_data.get('status'),
            'event_type': 'TRANSACTION_CREATED',
            'source': 'banking-web-app',
            'timestamp': datetime.utcnow().isoformat()
        }
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject='Banking Transaction Event',
            MessageAttributes={
                'event_type': {
                    'DataType': 'String',
                    'StringValue': 'TRANSACTION_CREATED'
                },
                'transaction_status': {
                    'DataType': 'String',
                    'StringValue': transaction_data.get('status', 'UNKNOWN')
                }
            }
        )
        print(f"SNS published: MessageId={response['MessageId']}")
        return response['MessageId']
    except Exception as e:
        # Log but do not fail the transaction — SNS publish is async/secondary
        print(f"SNS publish failed (non-critical): {str(e)}")
        return None

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
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .approved { background: #00ff88; color: #000; }
        .flagged { background: #ffa502; color: #000; }
        .event-indicator { font-size: 11px; color: #aaa; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🏦 Banking Transaction Dashboard</h1>
    <p>Engineer: Shaik Ahamed Eshak Nowfal | Region: ap-south-1 Mumbai | Pipeline: EC2 → RDS → SNS → Lambda</p>

    <div class="card">
        <h3>Submit New Transaction</h3>
        <input type="text" id="account" placeholder="Account Number" value="ACC001234">
        <input type="number" id="amount" placeholder="Amount (₹)" value="25000">
        <select id="type">
            <option value="credit">Credit</option>
            <option value="debit">Debit</option>
        </select>
        <input type="text" id="description" placeholder="Description" value="Test transaction">
        <button onclick="addTransaction()">Submit Transaction</button>
        <div id="result"></div>
    </div>

    <div class="card">
        <h3>Transaction History (from RDS MySQL)</h3>
        <table>
            <tr><th>ID</th><th>Account</th><th>Amount</th><th>Type</th>
                <th>Description</th><th>Status</th><th>Date</th></tr>
            {% for txn in transactions %}
            <tr>
                <td>{{ txn.id }}</td>
                <td>{{ txn.account_number }}</td>
                <td class="{{ txn.transaction_type }}">₹{{ "{:,.2f}".format(txn.amount) }}</td>
                <td>{{ txn.transaction_type.upper() }}</td>
                <td>{{ txn.description }}</td>
                <td><span class="badge {{ 'flagged' if txn.amount > 100000 else 'approved' }}">
                    {{ 'FLAGGED' if txn.amount > 100000 else 'APPROVED' }}</span></td>
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
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '<p>Processing...</p>';

        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();

        const snsInfo = result.sns_message_id
            ? `<br><small class="event-indicator">✓ Event published to SNS → SQS → Lambda (ID: ${result.sns_message_id.substring(0,8)}...)</small>`
            : '<br><small class="event-indicator">⚠ SNS publish skipped</small>';

        resultDiv.innerHTML = `
            <p>Status: <strong>${result.status}</strong> |
               Transaction ID: ${result.id} |
               Amount: ₹${result.amount.toLocaleString()}
               ${snsInfo}
            </p>`;
        setTimeout(() => location.reload(), 2000);
    }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 20"
            )
            transactions = cursor.fetchall()
        conn.close()
        for txn in transactions:
            txn['amount'] = float(txn['amount'])
        return render_template_string(DASHBOARD_HTML, transactions=transactions)
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 50"
            )
            transactions = cursor.fetchall()
        conn.close()
        for txn in transactions:
            if txn.get('created_at'):
                txn['created_at'] = str(txn['created_at'])
            txn['amount'] = float(txn['amount'])
        return jsonify({'transactions': transactions, 'count': len(transactions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        account_number = data.get('account_number')
        amount = float(data.get('amount', 0))
        transaction_type = data.get('transaction_type', 'debit')
        description = data.get('description', '')

        if not account_number:
            return jsonify({'error': 'account_number required'}), 400
        if amount <= 0:
            return jsonify({'error': 'amount must be positive'}), 400
        if transaction_type not in ['credit', 'debit']:
            return jsonify({'error': 'invalid transaction_type'}), 400

        status = 'FLAGGED_FOR_REVIEW' if amount > 100000 else 'APPROVED'

        # Step 1: Save to RDS
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

        transaction_data = {
            'id': new_id,
            'account_number': account_number,
            'amount': amount,
            'transaction_type': transaction_type,
            'description': description,
            'status': status
        }

        # Step 2: Publish to SNS (async — does not block response)
        sns_message_id = publish_to_sns(transaction_data)

        return jsonify({
            'id': new_id,
            'account_number': account_number,
            'amount': amount,
            'status': status,
            'message': 'Transaction recorded and event published',
            'sns_message_id': sns_message_id,
            'processed_at': datetime.utcnow().isoformat()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM transactions")
            result = cursor.fetchone()
        conn.close()
        db_status = "connected"
        tx_count = result['count']
    except Exception as e:
        db_status = f"error: {str(e)}"
        tx_count = 0

    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'database': db_status,
        'transaction_count': tx_count,
        'service': 'banking-dashboard',
        'pipeline': 'EC2 → RDS → SNS → SQS → Lambda',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
