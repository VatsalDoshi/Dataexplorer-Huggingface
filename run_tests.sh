#!/bin/bash

echo "🧪 Running Data Explorer Test Suite"
echo "===================================="

echo ""
echo "📋 Backend Tests (pytest):"
echo "-------------------------"
cd backend
python -m pytest tests/ -v --tb=short
backend_exit_code=$?

echo ""
echo "⚛️  Frontend Tests (Jest):"
echo "------------------------"
cd ../frontend
npm test -- --watchAll=false --passWithNoTests
frontend_exit_code=$?

echo ""
echo "📊 Test Results Summary:"
echo "----------------------"
if [ $backend_exit_code -eq 0 ]; then
    echo "✅ Backend tests: PASSED"
else
    echo "❌ Backend tests: FAILED"
fi

if [ $frontend_exit_code -eq 0 ]; then
    echo "✅ Frontend tests: PASSED"
else
    echo "❌ Frontend tests: FAILED"
fi

echo ""
if [ $backend_exit_code -eq 0 ] && [ $frontend_exit_code -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "💥 Some tests failed!"
    exit 1
fi 