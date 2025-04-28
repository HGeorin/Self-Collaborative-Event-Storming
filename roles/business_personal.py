from .prompts.business_personal import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class BusinessPersonnel(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("business_personal")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }

    def participate_round(self, round_num: int, context: str = None) -> str:
        """处理不同轮次的业务视角交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Business personnel does not participate in round {round_num}")

        return self.round_handlers[round_num](context)

    def _handle_round1(self, _: str = None) -> str:
        """第一轮：提出业务目标"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}

        {BP_TASK_DESC}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        """第二轮：补充业务相关领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}

        当前关键事件: {critical_event}

        {BP_TASK_ROUND2.replace('xxxx', critical_event)}

        业务视角指南:
        {BP_GUIDELINES_ROUND2}

        特别注意：
        - 从实际业务操作角度补充事件（如"客户提交退货申请"）
        - 避免技术术语（如"数据库记录更新"）

        格式要求:
        {BP_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        """第四轮：识别业务触发命令"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}

        当前事件流: {event_flow}

        {BP_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}

        业务视角指南:
        {BP_GUIDELINES_ROUND4}

        特别注意：
        - 命令应反映实际业务动作（如"客服批准退款"）
        - 执行者明确业务角色（如"财务专员"）

        格式要求:
        {BP_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        """第六轮：制定业务策略"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {BP_ROLE}

        当前领域模型:
        {domain_model}

        {BP_TASK_ROUND6}

        业务视角指南:
        {BP_GUIDELINES_ROUND6}

        特别注意：
        - 策略应体现业务规则（如"退货金额超过500元需主管审批"）
        - 避免技术实现细节

        格式要求:
        {BP_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        self.add_to_history("business_personal", response)
        return response