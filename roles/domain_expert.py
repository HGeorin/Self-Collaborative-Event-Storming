import json
import re
from typing import Dict, List
from utils import parse_user_scenarios


class DomainExpert:
    def __init__(self, team_prompt: str, role_prompt: str, scenario: Dict, model: str):
        """
        参数说明：
        - team_prompt: 团队协作规则提示词
        - role_prompt: 角色专属提示词（DOMAIN_EXPERT内容）
        - scenario: 业务场景数据，结构示例：
            {
                "domain": "电商订单系统",
                "business_goal": "实现从下单到履约的完整流程管理",
                "scenarios": [...]  # 用户场景列表
            }
        - model: 使用的LLM模型名称
        """
        self.team_prompt = team_prompt
        self.role_prompt = role_prompt
        self.scenario = scenario
        self.model = model
        self.history = []

    def elicit_knowledge(self) -> Dict:
        """核心方法：提取领域知识"""
        # 构建完整的提示词
        full_prompt = self._build_prompt()

        # 调用LLM（示例使用伪代码，需替换为实际API调用）
        response = self._call_llm(full_prompt)

        # 解析和验证响应
        return self._parse_response(response)

    def _build_prompt(self) -> List[Dict]:
        """构造多轮对话提示"""
        return [
            {"role": "system", "content": self.team_prompt},
            {"role": "user", "content": self._format_scenario()},
            {"role": "assistant", "content": "好的，我已收到业务场景描述，开始进行领域分析..."},
            {"role": "user", "content": self.role_prompt}
        ]

    def _format_scenario(self) -> str:
        """将业务场景数据转换为自然语言描述"""
        scenarios_text = "\n".join(
            [f"### {s['name']}\n{s['description']}"
             for s in self.scenario['scenarios']]
        )
        return (
            f"业务领域：{self.scenario['domain']}\n"
            f"业务目标：{self.scenario['business_goal']}\n"
            f"用户场景列表：\n{scenarios_text}"
        )

    def _call_llm(self, messages: List[Dict]) -> str:
        """调用LLM的示例实现（需替换为实际API调用）"""
        # 伪代码示例，实际应使用OpenAI API等
        print(f"调用模型：{self.model}")
        print("发送消息：", json.dumps(messages, indent=2, ensure_ascii=False))
        return '''
            ## 统一语言词典
            1. ​**订单** - 用户购买商品的契约，包含商品列表、金额、收货地址
            2. ​**库存保留** - 在支付前锁定商品的业务规则

            ## 业务流程
            ```mermaid
            graph TD
                A[用户提交订单] --> B{支付状态检查}
                B -->|已支付| C[生成发货单]
                B -->|未支付| D[取消订单]
            ```

            ## 待澄清点
            - 支付超时时间的具体数值
            - 部分库存不足时的处理策略
        '''

    def _parse_response(self, response: str) -> Dict:
        """解析LLM响应为结构化数据"""
        return {
            "ubiquitous_language": self._extract_terms(response),
            "process_diagram": self._extract_mermaid_code(response),
            "ambiguities": self._find_ambiguities(response)
        }

    def _extract_terms(self, text: str) -> List[Dict]:
        """提取统一语言词条"""
        terms = []
        term_re = re.compile(r"\d+\. \*\*(.+?)\*\* - (.+)")
        for match in term_re.findall(text):
            terms.append({"term": match[0], "definition": match[1]})
        return terms

    def _extract_mermaid_code(self, text: str) -> str:
        """提取Mermaid流程图代码"""
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.DOTALL)
        return mermaid_blocks[0] if mermaid_blocks else ""

    def _find_ambiguities(self, text: str) -> List[str]:
        """识别待澄清点"""
        return re.findall(r"- (.*?)\n", text.split("## 待澄清点")[1])