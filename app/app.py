from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy Data
account = {
    "account_number": "1234567890",
    "name": "John Doe",
    "balance": 50000
}

transactions = [
    {"id": 1, "type": "credit", "amount": 10000},
    {"id": 2, "type": "debit", "amount": 5000}
]

@app.route('/')
def home():
    return "Finance System API is Running"

@app.route('/balance', methods=['GET'])
def get_balance():
    return jsonify(account)

@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(transactions)

@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    transactions.append(data)
    return jsonify({"message": "Transaction added successfully"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
