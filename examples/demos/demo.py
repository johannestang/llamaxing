# Adapted from: https://github.com/openai/openai-python/blob/main/examples/demo.py
from openai import OpenAI

# Point the client at our local instance of llamaxing.
# A dummy API key must be provided for it to work.
client = OpenAI(base_url="http://localhost:8000/v1", api_key="1234")

# Non-streaming:
print("----- standard request -----")
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(completion.choices[0].message.content)

# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue

    print(chunk.choices[0].delta.content, end="")
print()
