from openai import OpenAI
from config.config_loader import config
class EventStormingAgent:
    def __init__(self, role: str):
        self.role = role
        self.conversation_history = []

    def add_to_history(self, speaker: str, message: str):
        # 记录对话历史（格式兼容OpenAI API）
        self.conversation_history.append({"role": speaker, "content": message})

    def generate_response(self, prompt: str) -> str:
        # response = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=[{"role": "system", "content": prompt}] + self.conversation_history
        # )
        # return response.choices[0].message.content
        llm_config = config.get_llm_config()
        client = OpenAI(api_key=llm_config['api_key'], base_url=llm_config['api_base'])

        response = client.chat.completions.create(
            model=llm_config['model'],  # deepseek-R1
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        return response.choices[0].message.content

    def discuss(self, context: str) -> str:
        raise NotImplementedError
