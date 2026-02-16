#!/usr/bin/env python
"""Example script demonstrating backend API usage."""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Rate Limit Headers:")
    print(f"  - Limit: {response.headers.get('X-RateLimit-Limit')}")
    print(f"  - Remaining: {response.headers.get('X-RateLimit-Remaining')}")
    print(f"  - Reset: {response.headers.get('X-RateLimit-Reset')} seconds")
    print()


def test_chat_send():
    """Test non-streaming chat endpoint."""
    print("Testing non-streaming chat endpoint...")
    
    # You'll need a valid specialist_id from your specialists.json
    # For demo purposes, we'll show what the request looks like
    payload = {
        "specialist_id": "your-specialist-id-here",
        "message": "What is 2+2?",
        "conversation_history": []
    }
    
    print(f"Request payload:\n{json.dumps(payload, indent=2)}")
    
    # Uncomment to actually make the request:
    # response = requests.post(f"{BASE_URL}/chat/send", json=payload)
    # print(f"Status: {response.status_code}")
    # if response.status_code == 200:
    #     data = response.json()
    #     print(f"Response: {data['content']}")
    #     print(f"Tokens: {data['input_tokens']} in, {data['output_tokens']} out")
    #     print(f"Cost: ${data['estimated_cost_usd']:.6f}")
    # else:
    #     print(f"Error: {response.json()}")
    print()


def test_streaming_chat():
    """Test streaming chat endpoint."""
    print("Testing streaming chat endpoint...")
    print("Note: This requires SSE client support")
    print()


def main():
    """Run example tests."""
    print("=" * 60)
    print("AI Portal Backend v2.0 - Example Usage")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_chat_send()
        test_streaming_chat()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend.")
        print("Make sure the backend is running:")
        print("  python -m uvicorn backend.main:app --reload")
        sys.exit(1)


if __name__ == "__main__":
    main()
