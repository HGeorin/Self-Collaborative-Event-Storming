from typing import Dict
from .prompts.business_personal import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class BusinessPersonnel(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("business_personal")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)

    def participate_round(self, round_num: int, context: str = None) -> str:
        if round_num not in self.round_handlers:
            raise ValueError(f"Business personnel does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1_1(self, _: str = None) -> str:
        system_message = f"""
        {TEAM_DESC}
        {BP_ROLE}
        """
        prompt = f"""
        {BP_TASK_DESC_1}
        """
        response = self.generate_response(prompt, system_message)
        return response

    def _handle_round1_2(self, reports: str = None) -> str:
        prompt = f"""
        {BP_TASK_DESC_2}
        Here are reports from other members:
        {reports}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round2(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {BP_TASK_ROUND2}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {BP_GUIDELINES_ROUND2}
        Required Format:
        {BP_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round4(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {BP_TASK_ROUND4}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {BP_GUIDELINES_ROUND4}
        Required Format:
        {BP_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round6(self, de_response: str) -> str:
        prompt = f"""
        Current Task:
        {BP_TASK_ROUND6}
        Here is what domain expert says:
        {de_response}
        Guidelines:
        {BP_GUIDELINES_ROUND6}
        Required Format:
        {BP_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        return response