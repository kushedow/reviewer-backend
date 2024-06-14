#!/bin/bash

# Step 0: Activate the virtual environment
source venv/bin/activate

# Load environment variables from .env
source .env

export SERVER=$(echo "$SERVER" | tr -d '\r')
export OPENAI_API_KEY=$(echo "$OPENAI_API_KEY" | tr -d '\r')
export CREDENTIALS_PATH=$(echo "$CREDENTIALS_PATH" | tr -d '\r')

# Step 1: Start the FastAPI application without caching
echo -e "\n### Step 1: Starting FastAPI application without caching..."
uvicorn main:app --host 127.0.0.1 --port 8000 &

# Sleep for a moment to allow the server to start
sleep 5

# Step 2: Run API tests without caching (expected to fail)
echo -e "\n### Step 2: Running API tests without caching..."
pytest_output=$(pytest -q -n 4 --disable-warnings \
    tests/test_api.py::test_checklist_full \
    tests/test_api.py::test_checklist_without_sheet_id \
    tests/test_api.py::test_checklist_with_sheet_id \
    tests/test_api.py::test_generate_motivation_with_python_simple \
    tests/test_api.py::test_explain_slug \
    tests/test_api.py::test_explain_slug_personalized)

# Count failed tests
failed_tests=$(echo "$pytest_output" | grep -c 'FAILED')

if [ "$failed_tests" -eq 6 ]; then
    echo -e "\n### All 6 tests failed as expected without caching. OK!"
else
    echo -e "\n!!! Unexpected result: $failed_tests out of 6 tests failed without caching."
fi

# Step 3: Trigger cache refresh (assuming /refresh endpoint triggers cache initialization)
echo -e "\n### Step 3: Triggering cache refresh..."
curl -X GET http://127.0.0.1:8000/refresh

# Wait for 30 seconds for cache to initialize
echo -e "\n### Step 4: Waiting for 30 seconds for cache initialization..."
sleep 30

# Step 5: Run API tests with caching (expected to pass)
echo -e "\n### Step 5: Running API tests with caching..."
pytest -n auto --disable-warnings tests/test_api.py

# Step 6: Run SheetPusher methods tests
echo -e "\n### Step 6: Running SheetPusher methods tests..."
pytest --disable-warnings tests/test_sheet_pusher.py

# Step 7: Stop the FastAPI application
echo -e "\n### Step 7: Stopping FastAPI application..."
kill $(lsof -t -i:8000)

echo -e "\n### ALL STEPS FINISHED ###"
