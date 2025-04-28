import json
import argparse
from pathlib import Path
from typing import Generator, Dict, Any
from session_es import Session


class EventStormingRunner:

    def __init__(self):
        self.args = self._parse_args()
        self._validate_paths()

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='事件风暴协作建模框架')
        parser.add_argument('--input_file', type=str, default='data/input.jsonl',
                            help='输入文件路径（JSONL格式）')
        parser.add_argument('--output_path', type=str, default='output/artifacts.json',
                            help='建模产物输出路径')
        parser.add_argument('--max_round', type=int, default=7,
                            help='最大协作轮次（匹配Session默认值）')
        parser.add_argument('--disable_validation', action='store_true',
                            help='禁用模型验证阶段')
        return parser.parse_args()

    def _validate_paths(self) -> None:
        if not Path(self.args.input_file).exists():
            raise FileNotFoundError(f"输入文件不存在: {self.args.input_file}")
        Path(self.args.output_path).parent.mkdir(parents=True, exist_ok=True)

    def _load_tasks(self) -> Generator[Dict[str, Any], None, None]:
        with open(self.args.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    continue

    def _format_output(self, task: Dict, artifacts: Dict) -> Dict[str, Any]:
        return {
            "task_id": task.get("task_id"),
            "domain": task.get("domain"),
            "artifacts": {
                "domain_events": artifacts["domain_events"],
                "commands": artifacts["commands"],
                "policies": artifacts["policies"],
                "hotspots": artifacts["hotspots"],
                "test_cases": artifacts["test_cases"],
                "user_stories": artifacts["user_stories"]
            },
            "validation_status": not self.args.disable_validation
        }

    def run(self) -> None:
        for task in self._load_tasks():
            try:
                # 构造session_es需要的业务场景字符串
                business_scenario = (
                        f"Domain: {task['domain']}\n"
                        f"Business Goal: {task['business_goal']}\n"
                        f"Scenarios:\n- " + "\n- ".join(task['scenarios'])
                )

                # 初始化Session（完全匹配你的构造函数）
                session = Session(
                    business_scenario=business_scenario,
                    max_round=self.args.max_round,
                    validation=not self.args.disable_validation
                )

                # 运行事件风暴（匹配你的返回结构）
                artifacts, _ = session.run_event_storming()

                # 保存结果
                output = self._format_output(task, artifacts)
                with open(self.args.output_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(output, ensure_ascii=False) + '\n')

                print(f"任务 {task.get('task_id')} 处理完成")

            except Exception as e:
                print(f"任务处理失败: {str(e)}")
                continue


if __name__ == '__main__':
    EventStormingRunner().run()