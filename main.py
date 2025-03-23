import os
import copy
import json
import argparse
import tqdm

from session_es import Session
from datasets import load_dataset, load_from_disk
from utils import prompt_split_humaneval, find_method_name, code_split, build_test_method, generate_uml_diagram

parser = argparse.ArgumentParser(description='EventStorming协作建模框架')
parser.add_argument('--input_file', type=str, default='data/input.jsonl',
                   help='输入文件路径（JSONL格式）')
parser.add_argument('--output_path', type=str, default='eventstorming_output.jsonl',
                   help='建模结果输出路径')
parser.add_argument('--model', type=str, default='gpt-4',
                   choices=['gpt-4', 'gpt-3.5-turbo'],
                   help='使用的LLM模型')
parser.add_argument('--max_round', type=int, default=3,
                   help='每阶段最大协作轮次')
parser.add_argument('--validation', action='store_true', default=False,
                   help='启用模型验证阶段')

# parser.add_argument('--lang', type=str, default='python')
# parser.add_argument('--output_path', type=str, default='output.jsonl')
#
# parser.add_argument('--signature', action='store_true')
# parser.add_argument('--max_round', type=int, default=2)
#
# parser.add_argument('--max_tokens', type=int, default=512)
# parser.add_argument('--majority', type=int, default=1)
# parser.add_argument('--temperature', type=float, default=0.0)
# parser.add_argument('--top_p', type=float, default=0.95)
#
# parser.add_argument('--fail_list', type=list, default=[])
# parser.add_argument('--append', action='store_true')
# parser.add_argument('--verbose', action='store_true')
# parser.add_argument("--timeout", type=float, default=10, help="how many seconds to wait during execution for each test case")
args = parser.parse_args()


if __name__ == '__main__':

    from roles.rule_event_storming_act import (
        TEAM_COLLAB,
        DOMAIN_EXPERT,
        EVENT_IDENTIFIER,
        AGGREGATE_DESIGNER,
        PROCESS_MODELER,
        MODEL_VALIDATOR
    )

    def load_custom_dataset(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                yield json.loads(line)


    with open(args.output_path, 'w') as f_out:
        # 处理每个建模任务
        for task in load_custom_dataset(args.input_file):
            try:
                # 输入解析改造
                domain_info = {
                    'domain': task['domain'],
                    'business_goal': task['business_goal'],
                    'user_scenarios': task['scenarios']
                }

                # 初始化建模会话
                session = Session(
                    team_prompt = TEAM_COLLAB,
                    domain_expert_prompt = DOMAIN_EXPERT,
                    event_identifier_prompt = EVENT_IDENTIFIER,
                    aggregate_designer_prompt = AGGREGATE_DESIGNER,
                    process_modeler_prompt = PROCESS_MODELER,
                    model_validator_prompt = MODEL_VALIDATOR,
                    business_scenario = domain_info,
                    model=args.model,
                    max_round=args.max_round,
                    validation=args.validation
                )

                # 运行协作建模流程
                model_artifacts, history = session.run_event_storming()

                # 构造输出结构
                output = {
                    "task_id": task["task_id"],
                    "domain": task["domain"],
                    "identified_events": model_artifacts['events'],
                    "aggregates": model_artifacts['aggregates'],
                    "process_flows": model_artifacts['process_flows'],
                    "validation_report": model_artifacts.get('validation', {}),
                    "model_visualization": generate_uml_diagram(model_artifacts)  # 新增可视化生成
                }

                f_out.write(json.dumps(output) + '\n')
                f_out.flush()

            except Exception as e:
                print(f"任务 {task['task_id']} 处理失败: {str(e)}")
                continue

    from roles.rule_descriptions_actc import TEAM, ANALYST, PYTHON_DEVELOPER, TESTER

    # OUTPUT_PATH = args.output_path

    # load dataset
    # if args.dataset == 'humaneval':
    #     if args.lang == 'python':
    #         dataset = load_dataset("openai_humaneval")
    #         dataset_key = ["test"]
    #
    # with open(OUTPUT_PATH, 'w+') as f:
    #     for key in dataset_key:
    #         pbar = tqdm.tqdm(dataset[key], total=len(dataset[key]))
    #         for idx, task in enumerate(pbar):
    #
    #             if args.dataset == 'humaneval':
    #                 method_name = task['entry_point']
    #                 before_func, signature, intent, public_test_case = prompt_split_humaneval(task['prompt'],method_name)
    #                 args.signature = True
    #                 if args.signature:
    #                     intent = task['prompt']
    #
    #                 test = task['test']
    #
    #             try:
    #                 session = Session(TEAM, ANALYST, PYTHON_DEVELOPER, TESTER,requirement=intent, model=args.model, majority=args.majority,
    #                                 max_tokens=args.max_tokens, temperature=args.temperature,
    #                                 top_p=args.top_p, max_round=args.max_round, before_func=before_func)
    #
    #                 code, session_history = session.run_session()
    #
    #             except RuntimeError as e:
    #                 print(str(e))
    #                 print("task-%d fail"%(task['task_id']))
    #                 fail_list.append(task['task_id'])
    #                 continue
    #
    #             if  code == "error":
    #                 continue
    #
    #             entry_point = find_method_name(code)
    #             solution = {
    #                 'task_id': task['task_id'],
    #                 'prompt': before_func+"\n",
    #                 'test': test,
    #                 'entry_point': entry_point,
    #                 'completion': code,
    #                 'session_history': session_history,
    #             }
    #             f.write(json.dumps(solution) + '\n')
    #             f.flush()
