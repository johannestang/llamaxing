# Adapted from: https://github.com/openai/openai-python/blob/main/examples/picture.py
from openai import OpenAI

# Point the client at our local instance of llamaxing.
# A dummy API key must be provided for it to work.
client = OpenAI(base_url="http://localhost:8000/v1", api_key="1234")

prompt = "An astronaut lounging in a tropical resort in space, pixel art"
model = "dall-e-3"


def main() -> None:
    # Generate an image based on the prompt
    response = client.images.generate(prompt=prompt, model=model)

    # Prints response containing a URL link to image
    print(response)


if __name__ == "__main__":
    main()
