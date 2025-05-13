from .EventStormingAgent import EventStormingAgent


class VisualizationGenerator(EventStormingAgent):
    def __init__(self):
        super().__init__("visualization_generator")
        self.system_message = """
        You are a PlantUML specialist that converts event storming results into precise PlantUML code.

        RULES:
        1. ONLY output PlantUML code wrapped between @startuml/@enduml
        2. NEVER add explanations or natural language
        3. Ensure syntax is 100% valid PlantUML
        """

    def generate_plantuml(self, final_result: str) -> str:
        """
        根据最终结果生成PlantUML代码
        :param final_result: 事件风暴最终文本结果
        :return: 纯PlantUML代码字符串
        """
        prompt = f"""
        Convert this event storming result to PlantUML:

        {final_result}
        """

        # 获取LLM响应并严格提取PlantUML代码块
        response = self.generate_response(prompt, self.system_message)
        return self._extract_plantuml_code(response)

    def _extract_plantuml_code(self, text: str) -> str:
        """从响应中精确提取PlantUML代码块"""
        start_tag = "@startuml"
        end_tag = "@enduml"

        start_idx = text.find(start_tag)
        end_idx = text.find(end_tag)

        if start_idx == -1 or end_idx == -1:
            raise ValueError("Invalid PlantUML response: missing start/end tags")

        return text[start_idx: end_idx + len(end_tag)].strip()