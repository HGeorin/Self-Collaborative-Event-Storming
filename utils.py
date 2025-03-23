import json
import re
import ast

import networkx as nx
from matplotlib import pyplot as plt
from plantuml import PlantUML
import os
import time
import difflib
import copy


def code_truncate_regex(code):
    code_regex = r"```(.*?|)\n(?P<code>.*?)```"
    match = re.search(code_regex, code, re.DOTALL)
    code = match.group("code") if match else ""
    return code
    
def code_truncate(response):
    code = code_truncate_regex(response)
    if code == "":
        generation = response[response.find("def"):]
        tem = [s for s in generation.split('\n\n') if 'def ' in s or s[:1] == ' ']
        code = '\n\n'.join(tem).strip('```').strip()
    return code

def prompt_split_humaneval(prompt, mehotd_name):
    prompt = prompt.strip()
    prompt = prompt.replace("\r\n", "\n")
    before_func = prompt[:prompt.rfind("def ")]
    code = prompt[prompt.rfind("def "):]

    comment_start_1 = re.search("\"\"\"", code)
    comment_start_2 = re.search("\'\'\'", code)
    if comment_start_1:
        comment_start = comment_start_1.end()
    elif comment_start_2:
        comment_start = comment_start_2.end()


    example_start_1 = re.search("[eE]xample(:)?", code)
    example_start_2 = re.search("[fF]or [eE]xamble(:)?", code)
    example_start_3 = re.search(">>>", code)
    example_start_4 = re.search(mehotd_name+"\(.+\)", code[comment_start:])


    if example_start_1:
        comment = code[comment_start:example_start_1.start()]
        example = code[example_start_1.start():-4]
    elif example_start_2:
        comment = code[comment_start:example_start_2.start()]
        example = code[example_start_2.start():-4]
    elif example_start_3:
        comment = code[comment_start:example_start_3.start()]
        example = "Example:\n"+code[example_start_3.start():-4]
    elif example_start_4:
        comment = code[comment_start:example_start_4.start()+comment_start]
        example = "Example:\n"+code[example_start_4.start()+comment_start:-4]
    else:
        comment = code[comment_start:-4]
        example = ""
    comment = comment.strip().replace("\n", " ")
    comment = re.sub("\s+", " ", comment)

    example = re.sub("\n(\s)*","\n\t",example)
    test_case = "\t"+example.strip()
    signature = code[:code.index("\n")+1]

    return before_func, signature, comment, test_case

def build_test_method(test_list, test_imports, method_name):
    if test_imports:
        test_imports = "\n".join(test_imports)
        test_method = test_imports + "\n"
    else:
        test_method = ""
    test_method = "def check(" + method_name + "):\n"
    if len(test_list) == 0:
        return test_method + "\treturn True" + "\n"
    for test in test_list:
        test_method += '\t' + test + "\n"
    return test_method.strip("\n")

def find_method_name(code, lang="python"):
    try:
        parsed = ast.parse(code)
        function_defs = [node for node in parsed.body if isinstance(node, ast.FunctionDef)]
        if function_defs:
            if len(function_defs) == 1:
                method_name = function_defs[0].name
            else:
                method_name = function_defs[-1].name if function_defs[-1].name != "main" else function_defs[-2].name
        else:
            method_name = None
    except:
        method_name = None

    return method_name


def code_split(func):
    '''
    Split code into signature, comment and function body
    '''
    func = func.replace("\r\n", "\n")
    before_func = func[:func.rfind("def ")]
    code = func[func.rfind("def "):]

    is_comment = False
    comments = []
    
    statements = code.split("\n")
    for s_idx, s in enumerate(statements):
        s = s.strip()
        if s.startswith("def"):
            signature = statements[:s_idx+1]
            method_name = s.split("def ")[1].split("(")[0]
            func_body_idx = s_idx+1
            tmp_statement = statements[func_body_idx].strip()
            if not tmp_statement.startswith("'''"):
                break
        elif s.startswith("'''") and not is_comment:
            is_comment = True

        elif is_comment:
            if s.startswith("'''"):
                is_comment = False
                func_body_idx = s_idx+1
                break
            comments.append(s)
    func_body = statements[func_body_idx:]
    return method_name, "\n".join(signature), "\n".join(comments), "\n".join(func_body), before_func

def construct_system_message(requirement, role, team=''):
    if team == '':
        system_message = "The requirement from users is: \n{'requirement':\n"  +  "'"+ requirement.replace('\n\n','\n').strip(".") + "'\n}\n\n" + role
    else:
        system_message = team + '\n '+ \
                    "The requirement from users is: \n{'requirement':\n"  +  "'"+ requirement.replace('\n\n','\n').strip(".") + "'\n}\n\n" + \
                    role
                
    return system_message


def generate_uml_from_plantuml(plantuml_code: str, output_dir='./graph', output_filename='uml_image.png'):
    """
    通过 PlantUML 代码生成 UML 图并保存到指定目录
    :param plantuml_code: PlantUML 代码
    :param output_dir: 生成的图像存储目录
    :param output_filename: 生成图像的文件名
    :return: 生成的图像文件路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plantuml_file = os.path.join(output_dir, 'temp_plantuml.puml')
    with open(plantuml_file, 'w') as file:
        file.write(plantuml_code)

    plantuml = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    output_file_path = os.path.join(output_dir, output_filename)
    plantuml.processes_file(plantuml_file, output_file_path)

    os.remove(plantuml_file)

    return output_file_path

def generate_knowledge_graph(data: dict, output_dir='./graph', output_filename='knowledge_graph.png'):
    """
    根据输入的数据生成知识图谱，并保存到指定目录
    :param data: 包含实体和关系的字典，格式为 {实体: [关系1, 关系2, ...]}
    :param output_dir: 图像存储目录
    :param output_filename: 生成图像的文件名
    :return: 生成的图像文件路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    G = nx.DiGraph()

    for entity, relationships in data.items():
        for relation in relationships:
            G.add_edge(entity, relation)

    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G)  # 使用 spring 布局
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)

    output_file_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_file_path, format='PNG')
    plt.close()

    return output_file_path


def generate_uml_diagram(artifacts):
    """生成PlantUML流程图"""
    uml = [
        "@startuml",
        "left to right direction",
        "skinparam packageStyle rectangle"
    ]

    # 添加事件
    for event in artifacts['events']:
        uml.append(f"rectangle \"{event['name']}\" as {event['id']}")

    # 添加流程关系
    for flow in artifacts['process_flows']:
        uml.append(f"{flow['source']} --> {flow['target']} : {flow['trigger']}")

    uml.append("@enduml")
    return '\n'.join(uml)

def parse_user_scenarios(scenario_data: Dict) -> str:
    """将用户场景数据转换为自然语言描述"""
    scenarios = []
    for idx, s in enumerate(scenario_data['scenarios'], 1):
        scenarios.append(
            f"{idx}. 场景名称：{s['name']}\n"
            f"   参与角色：{', '.join(s['actors'])}\n"
            f"   业务规则：{'; '.join(s.get('business_rules', []))}"
        )
    return "\n".join(scenarios)
    