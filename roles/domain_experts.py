from .prompts.domain_experts import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent
from typing import Dict


class DomainExpert(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("domain_expert")
        # 初始化系统消息
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self._initialize_conversation(self.system_desc)

        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            3: self._handle_round3,
            5: self._handle_round5,
            7: self._handle_round7
        }
        self.decision_log = []

    def participate_round(self, round_num: int, context: Dict[str, str] = None) -> str:
        """处理领域专家在不同轮次的权威交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Domain expert does not participate in round {round_num}")

        # 添加轮次标记到对话历史
        self.add_to_history("system", f"Entering round {round_num} discussion")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        system_message = f"""
                {TEAM_DESC}
                {DE_ROLE}
                """
        prompt = f"""
                {DE_TASK_DESC}
                this is the business report:
                {business_report}
                """
        response = self.generate_response(prompt, system_message)
        return response

    def _handle_round2(self, bp_response: str = None) -> str:
        """第二轮：确定核心领域事件"""
        prompt = f"""
        ~Business Personal says:
        {bp_response}
        
        ~Here is your task:
        {DE_TASK_ROUND2}
        
        ~And this is the guidelines:
        {DE_GUIDELINES_ROUND2}

        ~You should output with this format:
        {DE_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round3(self, team_inputs: str) -> str:
        """第三轮：整合领域事件流"""
        prompt = f"""
        ~Team says:
        {team_inputs}

        ~Here is your task:
        {DE_TASK_ROUND3}

        ~And this is the guidelines:
        {DE_GUIDELINES_ROUND3}

        ~You should output with this format:
        {DE_FORMAT_ROUND3}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round5(self, team_inputs: str) -> str:
        """第五轮：整合命令和实体"""
        prompt = f"""
        ~Team says:
        {team_inputs}

        ~Here is your task:
        {DE_TASK_ROUND5}

        ~And this is the guidelines:
        {DE_GUIDELINES_ROUND5}

        ~You should output with this format:
        {DE_FORMAT_ROUND5}
        """
        response = self.generate_response(prompt)
        return response

    def _handle_round7(self, team_inputs: str) -> str:
        """第七轮：确定最终策略"""
        prompt = f"""
        ~Team says:
        {team_inputs}

        ~Here is your task:
        {DE_TASK_ROUND5}

        ~And this is the guidelines:
        {DE_GUIDELINES_ROUND5}

        ~You should output with this format:
        {DE_FORMAT_ROUND5}
        """
        response = self.generate_response(prompt)
        return response

    def _log_decisions(self, inputs: Dict[str, str], output: str) -> None:
        """记录仲裁决策过程"""
        decision = {
            "input": inputs,
            "output": output,
            "rationale": "自动生成决策，详见热点说明"
        }
        self.decision_log.append(decision)