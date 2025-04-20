from typing import Dict, List, Tuple
import json

from roles.architects import Architect
from roles.business_personal import BusinessPersonnel
from roles.developers import Developer
from roles.domain_experts import DomainExpert

from roles.requirements_analysts import RequirementsAnalyst
from roles.testers import Tester


class Session:
    def __init__(self, business_scenario: str, model: str = "gpt-4", max_round: int = 7, validation: bool = True):
        self.business_scenario = business_scenario
        self.model = model
        self.max_round = max_round
        self.validation = validation
        self.agents = self._initialize_agents()
        self.history = []

    def _initialize_agents(self) -> Dict[str, object]:
        """初始化所有角色Agent"""
        shared_args = {
            "system_description": self.business_scenario,
            "model": self.model
        }
        return {
            "architect": Architect(** shared_args),
            "business_personal": BusinessPersonnel(** shared_args),
            "developer": Developer(** shared_args),
            "domain_expert": DomainExpert(** shared_args),
            "requirements_analyst": RequirementsAnalyst(** shared_args),
            "tester": Tester(** shared_args)
        }

    def _get_round_participants(self, round_num: int) -> List[Tuple[str, str]]:
        """定义每轮参与角色及其执行顺序和输入来源"""
        round_config = {
            1: [("business_personal", None)],  # (角色, 输入来源)
            2: [("domain_expert", None), ("business_personal", "domain_expert"), ("architect", "domain_expert")],
            3: [("domain_expert",
                 ["business_personal", "requirements_analyst", "architect", "developer", "tester"])],
            4: [("domain_expert", None), ("business_personal", "domain_expert"), ("architect", "domain_expert")],
            5: [("domain_expert",
                 ["business_personal", "requirements_analyst", "architect", "developer", "tester"])],
            6: [("domain_expert", None), ("business_personal", "domain_expert"), ("architect", "domain_expert")],
            7: [(
                "domain_expert", ["business_personal", "requirements_analyst", "architect", "developer", "tester"])]
        }
        return round_config.get(round_num, [])

    def _gather_inputs(self, sources: List[str]) -> Dict[str, str]:
        """从指定角色收集上一轮输出"""
        return {role: self.history[-1][role] for role in sources if role in self.history[-1]}

    def _validate_round_output(self, round_num: int, outputs: Dict[str, str]) -> bool:
        """执行轮次输出验证（示例）"""
        if not self.validation:
            return True

        if round_num == 1:
            return all("Agree" in output for output in outputs.values())
        elif round_num == 3:
            return any("Hotpots" in output for output in outputs.values())
        return True

    def run_event_storming(self) -> Tuple[Dict[str, List], List[Dict]]:
        """执行完整的事件风暴流程"""
        for round_num in range(1, self.max_round + 1):
            print(f"\n=== Round {round_num} ===")
            round_outputs = {}

            for role, input_source in self._get_round_participants(round_num):
                agent = self.agents[role]

                # 准备输入上下文
                context = self._gather_inputs(input_source) if isinstance(input_source, list) else (
                    self.history[-1][input_source] if input_source else None
                )

                # 执行角色交互
                try:
                    response = agent.participate_round(round_num, context)
                    round_outputs[role] = response
                    print(f"[{role[:10].ljust(10)}]: {response[:80]}...")
                except Exception as e:
                    print(f"{role} 执行失败: {str(e)}")
                    round_outputs[role] = f"ERROR: {str(e)}"

            # 验证并保存结果
            if not self._validate_round_output(round_num, round_outputs):
                raise RuntimeError(f"Round {round_num} 验证失败")
            self.history.append(round_outputs)

        return self._compile_artifacts(), self.history

    def _compile_artifacts(self) -> Dict[str, List]:
        """编译最终建模产物"""
        last_round = self.history[-1]
        expert_output = last_round["domain_expert"]

        return {
            "domain_events": self._extract_structured_data(expert_output, "Domain Events"),
            "commands": self._extract_structured_data(expert_output, "Commands"),
            "policies": self._extract_structured_data(expert_output, "Policies"),
            "hotspots": self._extract_structured_data(expert_output, "Hotpots"),
            "test_cases": self.agents["tester"].test_cases,
            "user_stories": self.agents["requirements_analyst"].user_stories
        }

    def _extract_structured_data(self, text: str, section: str) -> List[Dict]:
        """从文本输出中提取结构化数据"""
        if section not in text:
            return []

        items = []
        section_text = text.split(section + ":")[1].split("\n\n")[0]
        for line in section_text.split('\n'):
            if line.strip() and not line.strip().startswith("..."):
                parts = line.split(':')
                if len(parts) > 1:
                    items.append({
                        "element": parts[0].strip(),
                        "rationale": parts[1].strip()
                    })
        return items