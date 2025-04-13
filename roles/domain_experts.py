from prompts.domain_experts import *
from prompts.basic import *
import EventStormingAgent
from typing import Dict, List


class DomainExpert(EventStormingAgent):
    def __init__(self, system_description: str):
        super().__init__("domain_expert")
        self.system_desc = SYSTEM_DESC.replace("xxxxx", system_description)
        self.round_handlers = {
            1: self._handle_round1,
            2: self._handle_round2,
            3: self._handle_round3,
            5: self._handle_round5,
            7: self._handle_round7
        }
        self.decision_log = []  # 记录所有仲裁决策

    def participate_round(self, round_num: int, context: Dict[str, str] = None) -> str:
        """处理领域专家在不同轮次的权威交互"""
        if round_num not in self.round_handlers:
            raise ValueError(f"Domain expert does not participate in round {round_num}")
        return self.round_handlers[round_num](context)

    def _handle_round1(self, business_report: str) -> str:
        """第一轮：评审业务目标"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DE_ROLE}

        {DE_TASK_DESC}

        请以领域专家身份评估以下业务目标：
        {business_report}

        检查要点：
        1. 是否符合行业惯例
        2. 是否存在业务逻辑矛盾
        3. 术语使用是否准确

        输出格式：
        [问题列表] 或 "Agree to proceed with event storming"
        """
        response = self.generate_response(prompt)
        self.add_to_history("domain_expert", response)
        return response

    def _handle_round2(self, _: str = None) -> str:
        """第二轮：确定核心领域事件"""
        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DE_ROLE}

        {DE_TASK_ROUND2}

        {DE_GUIDELINES_ROUND2}

        请基于以下标准选择最重要的领域事件：
        1. 对业务流程有决定性影响
        2. 会触发多个后续事件
        3. 具有明确的业务价值

        格式要求：
        {DE_FORMAT_ROUND2}
        """
        response = self.generate_response(prompt)
        self.add_to_history("domain_expert", response)
        return response

    def _handle_round3(self, team_inputs: Dict[str, str]) -> str:
        """第三轮：整合领域事件流"""
        events_by_role = "\n".join([f"{role}: {events}" for role, events in team_inputs.items()])

        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DE_ROLE}

        各角色提交的领域事件：
        {events_by_role}

        {DE_TASK_ROUND3}

        {DE_GUIDELINES_ROUND3}

        处理步骤：
        1. 合并相同语义的事件（如"订单创建"和"订单已生成"）
        2. 移除违反业务规则的事件（如"未付款直接发货"）
        3. 对争议事件标注热点并说明原因

        格式要求：
        {DE_FORMAT_ROUND3}
        """
        response = self.generate_response(prompt)
        self._log_decisions(team_inputs, response)  # 记录仲裁过程
        self.add_to_history("domain_expert", response)
        return response

    def _handle_round5(self, team_inputs: Dict[str, str]) -> str:
        """第五轮：整合命令和实体"""
        commands_by_role = "\n".join([f"{role}: {data}" for role, data in team_inputs.items()])

        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DE_ROLE}

        各角色提交的命令和实体：
        {commands_by_role}

        {DE_TASK_ROUND5}

        {DE_GUIDELINES_ROUND5}

        仲裁原则：
        1. 优先保留业务人员定义的Actor命名
        2. 技术命令需与业务事件逻辑匹配
        3. 标记存在执行冲突的命令

        格式要求：
        {DE_FORMAT_ROUND5}
        """
        response = self.generate_response(prompt)
        self.add_to_history("domain_expert", response)
        return response

    def _handle_round7(self, team_inputs: Dict[str, str]) -> str:
        """第七轮：确定最终策略"""
        policies_by_role = "\n".join([f"{role}: {policies}" for role, policies in team_inputs.items()])

        prompt = f"""
        {TEAM_DESC}
        {self.system_desc}
        {DE_ROLE}

        各角色提交的策略：
        {policies_by_role}

        {DE_TASK_ROUND7}

        {DE_GUIDELINES_ROUND7}

        最终校验：
        1. 策略必须对应具体领域事件
        2. 业务规则应覆盖所有异常分支
        3. 技术策略不得违反业务合规要求

        格式要求：
        {DE_FORMAT_ROUND7}
        """
        response = self.generate_response(prompt)
        self.add_to_history("domain_expert", response)
        return response

    def _log_decisions(self, inputs: Dict[str, str], output: str) -> None:
        """记录仲裁决策过程"""
        decision = {
            "input": inputs,
            "output": output,
            "rationale": "自动生成决策，详见热点说明"
        }
        self.decision_log.append(decision)