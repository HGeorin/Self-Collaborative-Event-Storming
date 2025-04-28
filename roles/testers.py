from .prompts.testers import *
from .prompts.basic import *
from .EventStormingAgent import EventStormingAgent


class Tester(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("tester")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            4: self._handle_round4,
            6: self._handle_round6
        }
        self.test_cases = []  # 记录生成的测试用例要素

    def participate_round(self, round_num: int, context: str = None) -> str:
        """处理测试人员在不同轮次的交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Tester does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        """第一轮：测试可行性分析"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {TESTER_ROLE}

        {TESTER_TASK_DESC}

        请从测试角度评估以下业务目标：
        {business_report}

        检查要点：
        1. 目标是否具备可衡量的成功标准
        2. 是否存在模糊的验收边界
        3. 是否可验证非功能需求（如性能要求）

        输出格式：
        [测试相关问题] 或 "Agree to start Event Storming"
        """
        response = self.generate_response(prompt)
        self.add_to_history("tester", response)
        return response

    def _handle_round2(self, critical_event: str) -> str:
        """第二轮：识别测试相关领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {TESTER_ROLE}

        当前关键事件: {critical_event}

        {TESTER_TASK_ROUND2.replace('xxxx', critical_event)}

        测试视角指南:
        {TESTER_GUIDELINES_ROUND2}

        特别注意：
        - 补充异常流事件（如"支付已失败"）
        - 标记边界条件（如"库存为零时的购买"）

        格式要求:
        {TESTER_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self._extract_test_scenarios(response)
        self.add_to_history("tester", response)
        return response

    def _handle_round4(self, event_flow: str) -> str:
        """第四轮：定义测试命令"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {TESTER_ROLE}

        当前事件流: {event_flow}

        {TESTER_TASK_ROUND4.replace('1.A, 2.B, ...', event_flow)}

        测试视角指南:
        {TESTER_GUIDELINES_ROUND4}

        特别注意：
        - 识别非法命令（如"未登录用户提交订单"）
        - 标注需要Mock的外部系统

        格式要求:
        {TESTER_FORMAT_ROUND4}
        """
        response = self.generate_response(prompt)
        self.add_to_history("tester", response)
        return response

    def _handle_round6(self, domain_model: str) -> str:
        """第六轮：制定测试策略"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {TESTER_ROLE}

        当前领域模型:
        {domain_model}

        {TESTER_TASK_ROUND6}

        测试视角指南:
        {TESTER_GUIDELINES_ROUND6}

        特别注意：
        - 验证策略的可测试性（如"需记录审计日志"）
        - 标注需要压力测试的瓶颈点

        格式要求:
        {TESTER_FORMAT_ROUND6}
        """
        response = self.generate_response(prompt)
        self.add_to_history("tester", response)
        return response

    def _extract_test_scenarios(self, response: str) -> None:
        """从领域事件中提取测试场景"""
        if "Domain Events:" in response:
            for line in response.split('\n'):
                if "Domain Event(" in line:
                    event = line.split('(')[1].split(')')[0]
                    self.test_cases.append(f"Verify {event} under normal flow")
                elif "hotpot(" in line:
                    issue = line.split('(')[1].split(')')[0]
                    self.test_cases.append(f"Validate edge case: {issue}")