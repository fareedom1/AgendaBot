"""
Quick smoke test for litellm multi-provider connectivity.
Usage: GROQ_API_KEY=your_key python tests/test_litellm.py
"""
import os
import sys
from litellm import completion

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Set GROQ_API_KEY env var to run this test.")
    sys.exit(1)

try:
    response = completion(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("Success:", response)
except Exception as e:
    print("Error:", type(e), e)
