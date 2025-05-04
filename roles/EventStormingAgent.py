from openai import OpenAI
import logging
from config.config_loader import config
from typing import Dict, List, Optional


class EventStormingAgent:
    def __init__(self, role: str):
        self.role = role
        # 初始化对话历史，包含系统消息
        self.conversation_history = []
        self.logger = logging.getLogger("EventStormingRunner")
        # 记录当前对话ID（如果API支持）
        self.current_chat_id: Optional[str] = None
        # 初始化LLM客户端
        llm_config = config.get_llm_config()
        self.client = OpenAI(api_key=llm_config['api_key'], base_url=llm_config['api_base'])
        self.model = llm_config['model']

    def _initialize_conversation(self, system_message: str) -> None:
        """初始化对话历史，添加系统消息"""
        if not any(msg.get("role") == "system" for msg in self.conversation_history):
            self.conversation_history.append({
                "role": "system",
                "content": system_message
            })
            self.logger.debug(f"[Agent: {self.role}] Initialized with system message")

    def add_to_history(self, speaker: str, message: str) -> None:
        """添加对话历史，自动转换角色为API兼容格式"""
        api_role = "assistant" if speaker == self.role else "user"
        self.conversation_history.append({
            "role": api_role,
            "content": message
        })
        self.logger.debug(f"Added to history - {speaker}: {message[:100]}...")

    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """生成响应，支持多轮对话"""
        self.logger.info(f"[Agent: {self.role}] Generating response")

        # 如果有系统消息，初始化对话
        if system_message:
            self._initialize_conversation(system_message)

        # 添加用户输入到历史
        self.add_to_history("user", prompt)

        try:
            # 只发送最近的对话历史（如果API有token限制）
            messages = self._get_recent_messages()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )

            response_content = response.choices[0].message.content

            # 添加助手响应到历史
            self.add_to_history(self.role, response_content)

            self.logger.info(f"[Agent: {self.role}] Received response (length: {len(response_content)} chars)")

            # 记录API使用情况
            if hasattr(response, 'usage'):
                usage = response.usage
                self.logger.info(
                    f"API Usage - prompt_tokens: {usage.prompt_tokens}, "
                    f"completion_tokens: {usage.completion_tokens}, "
                    f"total_tokens: {usage.total_tokens}"
                )

            return response_content

        except Exception as e:
            self.logger.error(f"[Agent: {self.role}] API请求失败: {str(e)}", exc_info=True)
            raise

    def _get_recent_messages(self, max_messages: int = 10) -> List[Dict]:
        """获取最近的对话历史，防止token超限"""
        # 总是包含系统消息
        system_msg = next((msg for msg in self.conversation_history if msg["role"] == "system"), None)

        # 获取最近的用户/助手消息
        recent_messages = [msg for msg in self.conversation_history if msg["role"] != "system"][-max_messages:]

        if system_msg:
            return [system_msg] + recent_messages
        return recent_messages

    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history = []
        self.current_chat_id = None
        self.logger.info(f"[Agent: {self.role}] Conversation history cleared")

    def discuss(self, context: str) -> str:
        self.logger.info(f"[Agent: {self.role}] Starting discussion with context")
        try:
            raise NotImplementedError
        except Exception as e:
            self.logger.error(f"[Agent: {self.role}] Discussion failed: {str(e)}", exc_info=True)
            raise