from typing import Dict
from .prompts.developers import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class Developer(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("developer")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers: Dict[int, callable] = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }
        self.tech_constraints = []  # 记录识别出的技术约束

    def participate_round(self, round_num: int, context: str = None) -> str:
        """处理开发者在不同轮次的交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Developer does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        """第一轮：评审业务目标的技术可行性"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DEV_ROLE}

        {DEV_TASK_DESC}

        请从技术实现角度评估以下业务目标：
        {business_report}

        需要检查：
        1. 是否存在明显技术障碍（如实时性要求超出当前架构能力）
        2. 是否需要特殊技术栈支持
        3. 预估实现复杂度（高/中/低）

        输出格式：
        [技术问题]（若无则输出"Agree to start Event Storming."）
        """
        response = self.generate_response(prompt)
        self.add_to_history("developer", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        """第二轮：补充技术相关领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DEV_ROLE}

        当前关键事件: {critical_event}

        {DEV_TASK_ROUND2.replace('xxxx', critical_event)}

        技术视角指南:
        {DEV_GUIDELINES_ROUND2}

        特别注意：
        - 补充技术驱动事件（如"数据库备份完成"）
        - 标记技术热点（如"高并发支付验证"）

        格式要求:
        {DEV_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self._extract_tech_constraints(response)  # 提取技术约束
        self.add_to_history("developer", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        """第四轮：识别技术命令和执行实体"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DEV_ROLE}

        当前事件流: {event_flow}

        {DEV_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}

        技术视角指南:
        {DEV_GUIDELINES_ROUND4}

        特别注意：
        - 明确技术组件调用（如"支付网关API触发"）
        - 区分同步/异步命令

        格式要求:
        {DEV_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        self.add_to_history("developer", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        """第六轮：识别技术策略"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DEV_ROLE}

        当前领域模型:
        {domain_model}

        {DEV_TASK_ROUND6}

        技术视角指南:
        {DEV_GUIDELINES_ROUND6}

        特别注意：
        - 技术兜底策略（如"重试3次失败后进入人工处理"）
        - 系统级约束（如"响应时间<500ms"）

        格式要求:
        {DEV_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        self.add_to_history("developer", response)
        return response

    def _extract_tech_constraints(self, response: str) -> None:
        """从响应中提取技术约束"""
        if "Hotpots" in response:
            for line in response.split('\n'):
                if "hotpot" in line.lower():
                    self.tech_constraints.append(
                        line.split(':')[1].strip()  # 提取热点描述
                    )