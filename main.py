import base64
import json
import argparse
import logging
import zlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import plantuml
import requests

from roles.nl_processor import NLProcessor
from session_es import Session

from roles.visualization_generator import VisualizationGenerator


class EventStormingRunner:
    def __init__(self):
        self.args = self._parse_args()
        self._validate_paths()
        self._setup_logging()  # 初始化日志系统

        self.nl_processor = NLProcessor()
        self.visualizer = VisualizationGenerator()

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
        parser.add_argument('--input_file', type=str, default='data/input.txt',
                            help='输入文件路径（支持txt文档或JSONL格式）')
        parser.add_argument('--output_path', type=str, default='output/artifacts.json',
                            help='建模产物输出路径')
        parser.add_argument('--max_round', type=int, default=7,
                            help='最大协作轮次（匹配Session默认值）')
        parser.add_argument('--disable_validation', action='store_true',
                            help='禁用模型验证阶段')
        parser.add_argument('--generate_visualization', action='store_true',
                            help='生成PlantUML可视化')
        parser.add_argument('--output_dir', type=str, default='output',
                            help='输出目录路径')
        return parser.parse_args()

    def _validate_paths(self) -> None:
        if not Path(self.args.input_file).exists():
            raise FileNotFoundError(f"输入文件不存在: {self.args.input_file}")
        Path(self.args.output_path).parent.mkdir(parents=True, exist_ok=True)

    def _load_tasks(self, input_path: Path):
        """加载任务数据"""
        with open(input_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    def _save_results(self, artifacts: Dict, output_dir: Path):
        """保存结果到文件"""
        output_path = output_dir / "artifacts.jsonl"
        result = {
            "artifacts": artifacts,
            "validation_status": not self.args.disable_validation
        }

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

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

    def generate_uml_from_plantuml(
            self,
            plantuml_code: str,
            output_dir: str = './graph',
            output_filename: str = 'uml_image.png'
    ) -> str:
        """
        完全修正的PlantUML生成方法（解决编码问题）

        参数:
            plantuml_code: 合法的PlantUML代码
            output_dir: 输出目录路径
            output_filename: 输出文件名

        返回:
            生成的图片完整路径
        """
        # 1. 准备输出目录
        output_path = Path(output_dir) / output_filename
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 2. 初始化PlantUML（强制使用修正后的URL生成方式）
        pu = plantuml.PlantUML(url='http://www.plantuml.com/plantuml/img/')

        # 3. 手动处理编码（关键修正）
        try:
            # 修正点1：添加必需的~1前缀
            compressed = zlib.compress(plantuml_code.encode('utf-8'))
            encoded = base64.b64encode(compressed).decode('ascii')
            encoded = encoded.replace('+', '-').replace('/', '_')

            # 修正点2：构建合规URL
            diagram_url = f"{pu.url}png/~1{encoded}"

            # 4. 下载图片
            import requests
            response = requests.get(diagram_url, timeout=10)
            response.raise_for_status()

            # 5. 保存文件
            with open(output_path, 'wb') as f:
                f.write(response.content)

            return str(output_path.resolve())

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"图表下载失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"生成错误: {str(e)}")

    def run(self) -> None:
        self.logger.info("===== 事件风暴会话开始 =====")
        self.logger.info(f"参数配置: {vars(self.args)}")

        input_path = Path(self.args.input_file)
        if input_path.suffix.lower() != '.txt':
            raise ValueError(f"不支持的输入文件格式: {input_path.suffix}")

        output_dir = Path(self.args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"开始处理任务")

            # 构造业务场景字符串
            # business_scenario = (
            #         f"Domain: {task['domain']}\n"
            #         f"Business Goal: {task['business_goal']}\n"
            #         f"Scenarios:\n- " + "\n- ".join(task['scenarios'])
            # )
            business_scenario = self.nl_processor.process_text_file(input_path)  # 直接获取字符串内容

            self.logger.debug(f"业务场景:\n{business_scenario}")

            # 初始化Session
            session = Session(
                business_scenario=business_scenario,
                max_round=self.args.max_round,
                validation=not self.args.disable_validation
            )

            # 运行事件风暴
            final_result, _ = session.run_event_storming()

            self.logger.info(f"任务生成建模产物: {final_result}")

            # 3. 生成可视化
            plantuml_code = self.visualizer.generate_plantuml(final_result)
            output_file = self.generate_plantuml_diagram(plantuml_code)

            print(f"✅ 图表已生成: {output_file}")

            # 保存结果
            self._save_results(final_result, output_dir)

        except Exception as e:
            self.logger.error(f"任务处理失败: {str(e)}", exc_info=True)

        self.logger.info("===== 事件风暴会话结束 =====")


if __name__ == '__main__':
    # EventStormingRunner().run()
    debug_code = """@startuml

actor Student
actor Tutor
component SchedulingSystem <<system>>
component PaymentSystem <<system>>
component NotificationSystem <<system>>
component RecommendationSystem <<system>>

component "RequestTutoringSession" as C1 <<command>>
component "ConfirmSessionTime" as C2 <<command>>
component "AuthorizePayment" as C3 <<command>>
component "BlockTutorAvailability" as C4 <<command>>
component "SendConfirmation" as C5 <<command>>
component "ScheduleReminder" as C6 <<command>>
component "CapturePayment" as C7 <<command>>
component "SubmitFeedback" as C8 <<command>>
component "ReleasePayment" as C9 <<command>>
component "ProposeFollowUp" as C10 <<command>>

component "TutorAvailabilityConfirmed" as E1 <<event>>
component "TutoringSessionScheduled" as E2 <<event>>
component "PaymentAuthorizationInitiated" as E3 <<event>>
component "TutorAvailabilityBlocked" as E4 <<event>>
component "SessionConfirmationSent" as E5 <<event>>
component "SessionReminderSent" as E6 <<event>>
component "PaymentCaptured" as E7 <<event>>
component "FeedbackSubmitted" as E8 <<event>>
component "TutorPaymentReleased" as E9 <<event>>
component "FollowUpSessionScheduled" as E10 <<event>>

Student --> C1
Tutor --> C2
PaymentSystem --> C3
SchedulingSystem --> C4
NotificationSystem --> C5
NotificationSystem --> C6
PaymentSystem --> C7
Student --> C8
PaymentSystem --> C9
RecommendationSystem --> C10

C1 --> E1
C2 --> E2
C3 --> E3
C4 --> E4
C5 --> E5
C6 --> E6
C7 --> E7
C8 --> E8
C9 --> E9
C10 --> E10

@enduml"""
    EventStormingRunner().generate_uml_from_plantuml(debug_code)