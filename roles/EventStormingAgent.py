import openai
class EventStormingAgent:
    def __init__(self, role: str, model: str = "gpt-4"):
        # 初始化角色类型和LLM配置
        self.role = role
        self.model = model
        self.conversation_history = []  # 存储对话上下文

    def initialize_llm(self, api_key: str):
        # 设置LLM API密钥（实际项目建议用安全存储）
        openai.api_key = api_key

    def add_to_history(self, speaker: str, message: str):
        # 记录对话历史（格式兼容OpenAI API）
        self.conversation_history.append({"role": speaker, "content": message})

    def generate_response(self, prompt: str) -> str:
        # 标准化的LLM调用（可扩展重试机制/速率限制等）
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}] + self.conversation_history
        )
        return response.choices[0].message.content

    def discuss(self, context: str) -> str:
        # 抽象方法（子类必须实现具体讨论逻辑）
        raise NotImplementedError