from .prompts.architects import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class Architect(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__(role="architect")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }

    def participate_round(self, round_num: int, context: str = None) -> str:
        """处理不同轮次的交互逻辑"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Architect does not participate in round {round_num}")

        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        """第一轮：评审业务目标报告"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {ARCH_ROLE}

        {ARCH_TASK_DESC}

        Business Report Received:
        {business_report}

        Output your questions OR "Agree to start Event Storming".
        """
        response = self.generate_response(prompt)
        self.add_to_history("architect", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        """第二轮：基于关键事件生成相关领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {ARCH_ROLE}

        Current Task:
        {ARCH_TASK_ROUND2.replace('xxxx', critical_event)}

        Guidelines:
        {ARCH_GUIDELINES_ROUND2}

        Required Format:
        {ARCH_FORMAT_ROUND2}

        Provide your analysis strictly following the format.
        """
        response = self.generate_response(prompt)
        self.add_to_history("architect", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        """第四轮：识别命令和执行实体"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {ARCH_ROLE}

        Current Task:
        {ARCH_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}

        Guidelines:
        {ARCH_GUIDELINES_ROUND4}

        Required Format:
        {ARCH_FORMAT_ROUND4}

        Provide your analysis strictly following the format.
        """
        response = self.generate_response(prompt)
        self.add_to_history("architect", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        """第六轮：识别潜在策略"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {ARCH_ROLE}

        Current Task:
        {ARCH_TASK_ROUND6}

        Current Domain Model:
        {domain_model}

        Guidelines:
        {ARCH_GUIDELINES_ROUND6}

        Required Format:
        {ARCH_FORMAT_ROUND6}

        Provide your analysis strictly following the format.
        """
        response = self.generate_response(prompt)
        self.add_to_history("architect", response)
        return response