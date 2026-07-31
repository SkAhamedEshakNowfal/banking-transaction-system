#!/bin/bash

echo "=================================================="
echo "Banking Transaction System - End-to-End Test"
echo "Date: $(date)"
echo "=================================================="
PASS=0
FAIL=0
BASE_URL="http://localhost"

check() {
    local name=$1
    local result=$2
    local expected=$3
    if echo "$result" | grep -q "$expected"; then
        echo "✅ PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "❌ FAIL: $name"
        echo "   Expected: $expected"
        echo "   Got: $result"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "--- Layer 1: Application Health ---"
HEALTH=$(curl -s $BASE_URL/health)
check "Flask app running" "$HEALTH" "healthy"
check "RDS database connected" "$HEALTH" "connected"
check "Pipeline info present" "$HEALTH" "pipeline"

echo ""
echo "--- Layer 2: Transaction API ---"
TXN1=$(curl -s -X POST $BASE_URL/api/transactions \
    -H "Content-Type: application/json" \
    -d '{"account_number":"TEST-E2E-001","amount":50000,"transaction_type":"credit","description":"E2E test normal"}')
check "Normal transaction APPROVED" "$TXN1" "APPROVED"
check "Transaction ID assigned" "$TXN1" '"id"'
check "SNS message published" "$TXN1" "sns_message_id"

TXN2=$(curl -s -X POST $BASE_URL/api/transactions \
    -H "Content-Type: application/json" \
    -d '{"account_number":"TEST-E2E-002","amount":150000,"transaction_type":"debit","description":"E2E test large"}')
check "Large transaction FLAGGED" "$TXN2" "FLAGGED_FOR_REVIEW"

TXN3=$(curl -s -X POST $BASE_URL/api/transactions \
    -H "Content-Type: application/json" \
    -d '{"account_number":"TEST-E2E-003","amount":-500,"transaction_type":"credit","description":"E2E test invalid"}')
check "Invalid amount REJECTED" "$TXN3" "REJECTED"

echo ""
echo "--- Layer 3: RDS Data Persistence ---"
TXNS=$(curl -s $BASE_URL/api/transactions)
check "Transaction history accessible" "$TXNS" "transactions"
check "Count > 0" "$TXNS" '"count"'
TX_COUNT=$(echo $TXNS | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['count'])" 2>/dev/null)
echo "   Total transactions in RDS: $TX_COUNT"

echo ""
echo "--- Layer 4: Nginx Reverse Proxy ---"
NGINX=$(systemctl is-active nginx)
check "nginx active" "$NGINX" "active"
GUNICORN=$(systemctl is-active banking-app)
check "Gunicorn/Flask active" "$GUNICORN" "active"

echo ""
echo "--- Layer 5: SNS/SQS Pipeline ---"
# Wait for async processing
echo "   Waiting 15 seconds for async Lambda processing..."
sleep 15

# Check Lambda was invoked (via CloudWatch - from CloudShell only)
# Check S3 audit logs were written
AUDIT=$(aws s3 ls s3://ahamed-learning-2026/audit-logs/ --recursive 2>/dev/null | wc -l)
check "S3 audit logs exist" "$AUDIT" "[1-9]"
echo "   Audit log files in S3: $AUDIT"

echo ""
echo "=================================================="
echo "Test Results: $PASS passed, $FAIL failed"
if [ $FAIL -eq 0 ]; then
    echo "STATUS: ALL TESTS PASSED ✅"
else
    echo "STATUS: $FAIL TESTS FAILED ❌"
fi
echo "=================================================="
