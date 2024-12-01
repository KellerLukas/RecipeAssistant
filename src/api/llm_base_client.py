import json
from openai import OpenAI
from src.api.api_client_base import APIClientBase


API_KEY_UUID = "2m25xpqieooxvazcfhbprtphbq"

DEFAULT_MODEL_ARGS = {
    "model": "gpt-4o-mini",
    "response_format": {"type": "json_object"},
}


class LLMBaseClient(APIClientBase):
    def __init__(self, prompt_template: str, **kwargs):
        super().__init__(op_key_uuid=API_KEY_UUID)
        self.prompt = prompt_template.format(**kwargs)
        self.client = OpenAI(api_key=self._api_key)

    def _get_prompt(self, **kwargs) -> str:
        raise NotImplementedError

    def invoke(self, question: str) -> json:
        response = self.client.chat.completions.create(**DEFAULT_MODEL_ARGS,
            messages=[
                {"role": "system", "content": self.prompt},
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )
        content = response.choices[0].message.content
        return content.replace("</Response>", "")
