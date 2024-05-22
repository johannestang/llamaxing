import json

import tiktoken
from logging_utils import logger


# Adapted from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb # noqa: E501
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
    } or model.startswith("gpt-4"):
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}. "
            "See https://github.com/openai/openai-python/blob/main/chatml.md for "
            "information on how messages are converted to tokens."
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def merge_response_chunks(chunks, object_type="chat.completion.chunk"):
    if object_type not in ("chat.completion.chunk", "text_completion"):
        raise Exception("Invalid object type")

    merged_response = ""
    merge_successful = False
    token_count = 0
    valid_chunks = 0

    if not isinstance(chunks, list):
        raise Exception("Input should be a list")
    if len(chunks) == 0:
        raise Exception("Input list has length 0")

    chunks = "".join(chunks)
    chunks = chunks.split("\n\n")

    # Process chunks
    for chunk in chunks:
        if len(chunk) < 5:
            # Chunk is empty!
            break

        chunk_prefix = chunk[:5]
        if chunk_prefix != "data:":
            # Unexpected format!
            break

        # Are we done?
        chunk_data = chunk[6:]
        if chunk_data.strip() == "[DONE]":
            merge_successful = True
            break
        # If not, parse data:
        try:
            chunk_data = json.loads(chunk_data)
        except Exception:
            break

        # Is the chunk actually a completion chunk?
        if chunk_data["object"] == object_type:
            valid_chunks += 1
        else:
            # Otherwise, skip it
            continue

        if object_type == "chat.completion.chunk":
            # Is this the first chunk?
            if valid_chunks == 1:
                merged_response = chunk_data
                if "content" not in merged_response["choices"][0]["delta"]:
                    merged_response["choices"][0]["delta"]["content"] = ""
            elif valid_chunks > 1:
                delta = chunk_data["choices"][0]["delta"]
                if "content" in delta:
                    token_count += 1
                    merged_response["choices"][0]["delta"]["content"] += delta[
                        "content"
                    ]
                if "finish_reason" in chunk_data["choices"][0]:
                    merged_response["choices"][0]["finish_reason"] = chunk_data[
                        "choices"
                    ][0]["finish_reason"]
        elif object_type == "text_completion":
            # Is this the first chunk?
            if valid_chunks == 1:
                merged_response = chunk_data
                if "text" not in merged_response["choices"][0]:
                    merged_response["choices"][0]["text"] = ""
            elif valid_chunks > 1:
                delta = chunk_data["choices"][0]
                if "text" in delta:
                    token_count += 1
                    merged_response["choices"][0]["text"] += delta["text"]
                if "finish_reason" in chunk_data["choices"][0]:
                    merged_response["choices"][0]["finish_reason"] = chunk_data[
                        "choices"
                    ][0]["finish_reason"]

    if valid_chunks == 0:
        raise Exception("Merge failed - did not find any valid chunks!")

    if object_type == "chat.completion.chunk":
        # Rename delta key to match non-streaming response
        merged_response["choices"][0]["message"] = merged_response["choices"][0].pop(
            "delta"
        )

    # Add more info
    if merge_successful:
        merged_response["usage"] = {"completion_tokens": token_count}
    merged_response["streaming_response"] = True
    merged_response["stream_merge_successful"] = merge_successful

    return merged_response
