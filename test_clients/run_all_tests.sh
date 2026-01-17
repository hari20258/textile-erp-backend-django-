#!/bin/bash

# Run all test clients sequentially
# This script runs each client and shows the results

echo "========================================="
echo "Textile Backend API - Test Suite"
echo "========================================="
echo ""
echo "Make sure the Django server is running on http://localhost:8000"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "1/5 Testing Admin Client..."
echo "========================================="
python test_admin_client.py
echo ""
read -p "Press Enter for next test..."

echo ""
echo "2/5 Testing Manager Client..."
echo "========================================="
python test_manager_client.py
echo ""
read -p "Press Enter for next test..."

echo ""
echo "3/5 Testing Sales Staff Client..."
echo "========================================="
python test_staff_client.py
echo ""
read -p "Press Enter for next test..."

echo ""
echo "4/5 Testing Supplier Client..."
echo "========================================="
python test_supplier_client.py
echo ""
read -p "Press Enter for next test..."

echo ""
echo "5/5 Testing Customer Client..."
echo "========================================="
python test_customer_client.py
echo ""

echo "========================================="
echo "✅ All tests complete!"
echo "========================================="
