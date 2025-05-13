from typing import Dict
from .prompts.architects import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class Architect(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__(role="architect")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers: Dict[int, callable] = {
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
        system_message = f"""
        {TEAM_DESC}
        {ARCH_ROLE}
        """
        prompt = f"""
        {ARCH_TASK_DESC}
        this is the business report:
        {business_report}
        """
        response = self.generate_response(prompt, system_message)
        return response

    def _handle_round2(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {ARCH_TASK_ROUND2}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {ARCH_GUIDELINES_ROUND2}
        Required Format:
        {ARCH_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round4(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {ARCH_TASK_ROUND4}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {ARCH_GUIDELINES_ROUND4}
        Required Format:
        {ARCH_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round6(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {ARCH_TASK_ROUND6}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {ARCH_GUIDELINES_ROUND6}
        Required Format:
        {ARCH_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        return response