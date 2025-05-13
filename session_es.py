from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from roles.architects import Architect
from roles.business_personal import BusinessPersonnel
from roles.developers import Developer
from roles.domain_experts import DomainExpert

from roles.requirements_analysts import RequirementsAnalyst
from roles.testers import Tester

from roles.prompts import debug


class Session:
    def __init__(self, business_scenario: str, max_round: int = 7, validation: bool = True):
        self.business_scenario = business_scenario
        self.max_round = max_round
        self.validation = validation
        self.agents = self._initialize_agents()
        self.history = []

    def _initialize_agents(self) -> Dict[str, object]:
        """初始化所有角色Agent"""
        shared_args = {
            "system_description": self.business_scenario,
        }
        return {
            "architect": Architect(**shared_args),
            "business_personal": BusinessPersonnel(**shared_args),
            "developer": Developer(**shared_args),
            "domain_expert": DomainExpert(**shared_args),
            "requirements_analyst": RequirementsAnalyst(**shared_args),
            "tester": Tester(**shared_args)
        }

    def _get_round_participants(self, round_num: int) -> List[Tuple[str, str]]:
        """定义每轮参与角色及其执行顺序和输入来源"""
        round_config = {
            1: [("business_personal", None)],  # (角色, 输入来源)
            2: [
                ("domain_expert", None),
                ("business_personal", "domain_expert"),
                ("architect", "domain_expert")
            ],
            3: [("domain_expert", ["business_personal", "requirements_analyst", "architect", "developer", "tester"])],
            4: [
                ("domain_expert", None),
                ("business_personal", "domain_expert"),
                ("architect", "domain_expert")
            ],
            5: [("domain_expert", ["business_personal", "requirements_analyst", "architect", "developer", "tester"])],
            6: [
                ("domain_expert", None),
                ("business_personal", "domain_expert"),
                ("architect", "domain_expert")
            ],
            7: [("domain_expert", ["business_personal", "requirements_analyst", "architect", "developer", "tester"])]
        }
        return round_config.get(round_num, [])

    def _gather_inputs(self, sources: List[str]) -> Dict[str, str]:
        """从历史记录中收集输入数据"""
        if not self.history:
            return {}
        return {role: self.history[-1].get(role, "") for role in sources}

    def _validate_round_output(self, round_num: int, outputs: Dict[str, str]) -> bool:
        """验证轮次输出有效性"""
        if not self.validation:
            return True

        if round_num == 1:
            return all("Agree" in output for output in outputs.values())
        elif round_num == 3:
            return any("Hotpots" in output for output in outputs.values())
        return True

    def _round_1(self) -> str:
        """
        处理第一轮交互
        返回business_personal收到报告后的回复
        """
        bp_agent = self.agents["business_personal"]

        # 1. 生成业务介绍
        introduce = bp_agent._handle_round1_1()

        # 2. 使用线程池并行请求其他角色
        with ThreadPoolExecutor() as executor:
            futures = {
                role: executor.submit(self.agents[role]._handle_round1, introduce)
                for role in self.agents
                if role != "business_personal"
            }

            # 获取所有响应
            responses = {
                role: future.result()
                for role, future in futures.items()
            }

        # 3. 整合结果
        consolidated = self._consolidate_responses(responses)
        bp_agent._handle_round1_2(consolidated)
        return consolidated

    def _round_2(self, bp_response: str = None) -> str:
        de_agent = self.agents["domain_expert"]
        de_response = de_agent._handle_round2(bp_response)

        with ThreadPoolExecutor() as executor:
            futures = {
                role: executor.submit(self.agents[role]._handle_round2, de_response)
                for role in self.agents
                if role != "domain_expert"
            }

            # 获取所有响应
            responses = {
                role: future.result()
                for role, future in futures.items()
            }

        consolidated = self._consolidate_responses(responses)
        # round 3
        return de_agent._handle_round3(consolidated)

    def _round_4(self, de_response: str = None) -> str:
        de_agent = self.agents["domain_expert"]

        with ThreadPoolExecutor() as executor:
            futures = {
                role: executor.submit(self.agents[role]._handle_round4, de_response)
                for role in self.agents
                if role != "domain_expert"
            }

            # 获取所有响应
            responses = {
                role: future.result()
                for role, future in futures.items()
            }

        consolidated = self._consolidate_responses(responses)
        # round 5
        return de_agent._handle_round5(consolidated)

    def _round_6(self, de_response: str = None) -> str:
        de_agent = self.agents["domain_expert"]

        with ThreadPoolExecutor() as executor:
            futures = {
                role: executor.submit(self.agents[role]._handle_round6, de_response)
                for role in self.agents
                if role != "domain_expert"
            }

            # 获取所有响应
            responses = {
                role: future.result()
                for role, future in futures.items()
            }

        consolidated = self._consolidate_responses(responses)
        # round 7
        return de_agent._handle_round7(consolidated)

    def run_event_storming(self):
        """同步执行事件风暴流程"""
        try:
            #self._debug()
            round1_output = self._round_1()
            self.history.append(round1_output)

            round2_output = self._round_2(round1_output)
            self.history.append(round2_output)

            round4_output = self._round_4(round2_output)
            self.history.append(round4_output)

            final_result = self._round_6(round4_output)
            self.history.append(final_result)

            return final_result, self.history
        except Exception as e:
            print(f"Event Storming failed: {e}")
            raise

    # def _compile_artifacts(self) -> Dict[str, List]:
    #     """编译最终产物"""
    #     if not self.history:
    #         return {
    #             "domain_events": [],
    #             "commands": [],
    #             "policies": [],
    #             "hotspots": [],
    #             "test_cases": [],
    #             "user_stories": []
    #         }
    #
    #     last_round = self.history[-1]
    #     expert_output = last_round.get("domain_expert", "")
    #
    #     return {
    #         "domain_events": self._extract_structured_data(expert_output, "Domain Events"),
    #         "commands": self._extract_structured_data(expert_output, "Commands"),
    #         "policies": self._extract_structured_data(expert_output, "Policies"),
    #         "hotspots": self._extract_structured_data(expert_output, "Hotpots"),
    #         "test_cases": self.agents["tester"].test_cases,
    #         "user_stories": self.agents["requirements_analyst"].user_stories
    #     }

    def _extract_structured_data(self, text: str, section: str) -> List[Dict]:
        """从文本中提取结构化数据"""
        if not text or section not in text:
            return []

        items = []
        section_text = text.split(section + ":")[1].split("\n\n")[0]
        for line in section_text.split('\n'):
            line = line.strip()
            if line and not line.startswith("..."):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    items.append({
                        "element": parts[0].strip(),
                        "rationale": parts[1].strip()
                    })
        return items

    def _consolidate_responses(self, responses: Dict[str, str]) -> str:
        """
        返回纯字符串格式的响应合并结果
        格式示例：
            [ARCHITECT] Agree to start...
            [DEVELOPER] Question: What's the timeout threshold?
            [TESTER] Need clarify test scope
        """
        return "\n".join(
            f"[{role.upper()}] {response.strip()}"
            for role, response in responses.items()
        )

    def _debug(self):
        """
        debug用
        """
        bp_agent = self.agents["business_personal"]
        response = bp_agent._handle_round1_2(debug.ROUND1_5ROLES)

        print("debug completed.")
