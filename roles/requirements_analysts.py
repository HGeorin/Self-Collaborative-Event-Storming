from .prompts.requirements_analysts import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class RequirementsAnalyst(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("requirements_analyst")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }
        self.user_stories = []  # 记录识别的用户故事要素

    def participate_round(self, round_num: int, context: str = None) -> str:
        """处理需求分析师在不同轮次的交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Requirements analyst does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        """第一轮：需求可行性分析"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {RA_ROLE}

        {RA_TASK_DESC}

        请从需求分析角度评估以下业务目标：
        {business_report}

        检查要点：
        1. 需求是否具备明确的验收标准
        2. 是否存在模糊的需求边界
        3. 是否可拆分为独立的用户故事

        输出格式：
        [需求澄清问题] 或 "Agree to start Event Storming"
        """
        response = self.generate_response(prompt)
        self.add_to_history("requirements_analyst", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        """第二轮：识别需求相关领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {RA_ROLE}

        当前关键事件: {critical_event}

        {RA_TASK_ROUND2.replace('xxxx', critical_event)}

        需求分析指南:
        {RA_GUIDELINES_ROUND2}

        特别注意：
        - 事件应反映用户价值（如"客户满意度已记录"）
        - 避免技术实现细节（如"数据库日志已写入"）

        格式要求:
        {RA_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self._extract_user_stories(response)  # 提取用户故事要素
        self.add_to_history("requirements_analyst", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        """第四轮：定义需求级命令"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {RA_ROLE}

        当前事件流: {event_flow}

        {RA_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}

        需求分析指南:
        {RA_GUIDELINES_ROUND4}

        特别注意：
        - 命令应直接关联用户目标（如"用户提交订单"）
        - 实体命名采用业务术语（如"客服专员"而非"User角色"）

        格式要求:
        {RA_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        self.add_to_history("requirements_analyst", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        """第六轮：制定需求策略"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {RA_ROLE}

        当前领域模型:
        {domain_model}

        {RA_TASK_ROUND6}

        需求分析指南:
        {RA_GUIDELINES_ROUND6}

        特别注意：
        - 策略应可验证（如"订单金额>1万需二次确认"）
        - 标注需要业务方确认的模糊策略

        格式要求:
        {RA_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        self.add_to_history("requirements_analyst", response)
        return response

    def _extract_user_stories(self, response: str) -> None:
        """从领域事件中提取用户故事要素"""
        if "Domain Events:" in response:
            for line in response.split('\n'):
                if "Domain Event(" in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        self.user_stories.append(
                            f"As a [role], I want {parts[0].strip()} so that {parts[1].strip()}"
                        )