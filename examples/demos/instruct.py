# Adapted from: https://github.com/openai/openai-python/blob/main/examples/async_demo.py
import asyncio

from openai import AsyncOpenAI

# Point the client at our local instance of llamaxing.
# A dummy API key must be provided for it to work.
client = AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="1234")


async def main() -> None:
    stream = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Say this is a test",
        stream=True,
    )
    async for completion in stream:
        if len(completion.choices) > 0:
            print(completion.choices[0].text, end="")
    print()


asyncio.run(main())
