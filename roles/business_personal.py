from typing import Dict
from .prompts.business_personal import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class BusinessPersonnel(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("business_personal")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers: Dict[int, callable] = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }

    def participate_round(self, round_num: int, context: str = None) -> str:
        if round_num not in self.round_handlers:
            raise ValueError(f"Business personnel does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, _: str = None) -> str:
        system_message = f"""
        {TEAM_DESC}
        {BP_ROLE}
        """
        prompt = f"""
        {BP_TASK_DESC}
        """
        response = self.generate_response(prompt, system_message)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}
        当前关键事件: {critical_event}
        {BP_TASK_ROUND2.replace('xxxx', critical_event)}
        业务视角指南:
        {BP_GUIDELINES_ROUND2}
        格式要求:
        {BP_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}
        当前事件流: {event_flow}
        {BP_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}
        业务视角指南:
        {BP_GUIDELINES_ROUND4}
        格式要求:
        {BP_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}
        当前领域模型:
        {domain_model}
        {BP_TASK_ROUND6}
        业务视角指南:
        {BP_GUIDELINES_ROUND6}
        格式要求:
        {BP_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response