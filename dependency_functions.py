from pydantic_models import CompletionRequest


def get_prompt_messages(data: CompletionRequest):
    print(data.messages)
    return data.messages