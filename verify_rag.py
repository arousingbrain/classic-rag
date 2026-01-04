import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("\n--- Checking API Health ---")
    response = requests.get(f"{BASE_URL}/health")
    print(response.json())

def test_ingest():
    print("\n--- Ingesting Knowledge Base Data ---")
    data = {
        "chunks": [
            {
                "id": "hr_policy_1",
                "content": "The standard work hours are 9:00 AM to 5:00 PM, Monday through Friday.",
                "metadata": {"source": "manual", "section": "HR"}
            },
            {
                "id": "hr_policy_2",
                "content": "Our remote work policy allows employees to work from home on Tuesdays and Thursdays.",
                "metadata": {"source": "manual", "section": "HR"}
            },
            {
                "id": "it_policy_1",
                "content": "Laptops must be returned to the IT department within 24 hours of an employee's last day.",
                "metadata": {"source": "manual", "section": "IT"}
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/ingest", json=data)
    print(response.json())

def test_chat(query):
    print(f"\n--- Asking Query: '{query}' ---")
    data = {"message": query}
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    print(f"ANSWER: {result.get('answer')}")
    print(f"SOURCES: {[s['id'] for s in result.get('sources', [])]}")

def test_delete(ids):
    print(f"\n--- Deleting Chunks: {ids} ---")
    data = {"ids": ids}
    # Using delete method with json body
    response = requests.delete(f"{BASE_URL}/documents", json=data)
    print(response.json())

if __name__ == "__main__":
    try:
        test_health()
        
        # Define IDs to track for cleanup
        test_ids = ["hr_policy_1", "hr_policy_2", "it_policy_1"]
        
        test_ingest()
        
        # Give Chroma a split second if needed
        time.sleep(1)
        
        test_chat("When can I work from home?")
        test_chat("What should I do with my laptop when I leave?")
        
        # Clean up
        test_delete(test_ids)
        
        # Verify deletion
        print("\n--- Verifying Deletion (Should find no context) ---")
        test_chat("When can I work from home?")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: API is not running. Start it with 'uv run uvicorn src.api.main:app --reload' first.")
