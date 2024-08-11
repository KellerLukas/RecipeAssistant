import json
from src.api.api_client_base import APIClientBase


API_KEY_UUID = "2m25xpqieooxvazcfhbprtphbq"

DEFAULT_MODEL_ARGS = {
    "model": "gpt-4o-mini",
    "response_format": {"type": "json_object"},
}


class LLMBaseClient(APIClientBase):
    def __init__(self, prompt_template: str, model_args: dict):
        super().__init__(op_key_uuid=API_KEY_UUID)
        self.prompt = self._get_prompt(prompt_template)
        self.client = OpenAI(api_key=self._api_key)

    def _get_prompt(self, prompt_template: str) -> str:
        raise NotImplementedError

    def get_classification(self, question: str) -> json:
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
a