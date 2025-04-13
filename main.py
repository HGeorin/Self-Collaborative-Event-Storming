import json
import argparse

from session_es import Session
from utils import generate_uml_diagram

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
args = parser.parse_args()


if __name__ == '__main__':

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
