import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any
from session_es import Session


class EventStormingRunner:
    def __init__(self):
        self.args = self._parse_args()
        self._validate_paths()
        self._setup_logging()  # 初始化日志系统

    def _setup_logging(self):
        """设置日志系统，每次运行创建新的日志文件"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # 使用当前时间创建日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"event_storming_{timestamp}.log"

        # 配置日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )
        self.logger = logging.getLogger("EventStormingRunner")

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
                    self.logger.error(f"JSON解析错误: {str(e)}")
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
        self.logger.info("===== 事件风暴会话开始 =====")
        self.logger.info(f"参数配置: {vars(self.args)}")

        for task in self._load_tasks():
            task_id = task.get("task_id", "未知ID")
            try:
                self.logger.info(f"开始处理任务: {task_id}")

                # 构造业务场景字符串
                business_scenario = (
                        f"Domain: {task['domain']}\n"
                        f"Business Goal: {task['business_goal']}\n"
                        f"Scenarios:\n- " + "\n- ".join(task['scenarios'])
                )

                self.logger.debug(f"业务场景:\n{business_scenario}")

                # 初始化Session
                session = Session(
                    business_scenario=business_scenario,
                    max_round=self.args.max_round,
                    validation=not self.args.disable_validation
                )

                # 运行事件风暴
                artifacts, _ = session.run_event_storming()

                self.logger.info(f"任务 {task_id} 生成建模产物: {list(artifacts.keys())}")

                # 保存结果
                output = self._format_output(task, artifacts)
                with open(self.args.output_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(output, ensure_ascii=False) + '\n')

                self.logger.info(f"任务 {task_id} 处理完成并保存结果")

            except Exception as e:
                self.logger.error(f"任务 {task_id} 处理失败: {str(e)}", exc_info=True)
                continue

        self.logger.info("===== 事件风暴会话结束 =====")


if __name__ == '__main__':
    EventStormingRunner().run()