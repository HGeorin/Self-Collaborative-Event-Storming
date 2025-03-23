# Self-collaboration Code Generation via ChatGPT

基于 Yihong Dong 等人 [**Self-collaboration Code Generation via ChatGPT**](https://arxiv.org/abs/2304.07590)

开发的面向事件风暴建模的自我协作框架

## Run code
```bash
# generate
bash run.sh
# evaluate
bash evaluate.sh
```

## Citation
```
@article{dong2023self,
  title={Self-collaboration code generation via chatgpt},
  author={Dong, Yihong and Jiang, Xue and Jin, Zhi and Li, Ge},
  journal={arXiv preprint arXiv:2304.07590},
  year={2023}
}
```

## TODO

- 一个完整的项目需要使用的工具，以及对应生成的图片:
  - plantUML √
    - 用于生成各种UML图
  - 知识图谱 √
  - miro
    - 用于生成事件风暴图，命令与事件关系图
    - 使用难度高，需要时间学习如何使用，难点在于如何使用大语言模型自动化生成图片，优势是更灵活，可生成图片，可兼容python
    - 目前考虑的方向是让Developer编写一个临时python代码，让它实现调用miro api并生成一个完整的事件风暴图
    - 需要用户自行填写apiKey用于生成图片，若需求很大，可能需要用户自行购买
- 如何输入：
  - 目前的main.py调用Openai-HumanEval库，计划：用户需在本地data文件夹自己编写输入jsonl文件，并且先去除验证部分。
- 具体逻辑待修改：
  - 目前主要涉及的文件:./main.py  ./session.py  ./roles/*  ./core/interface.py， 以及提示词
  - analyst逻辑不变，仍然是输入要求，输出需求分析
  - coder:主要看要求(待定) 比如需要使用miro生成事件风暴图，就让它生成代码，若需要生成uml图，就让它生成plantUML语言，需要多个图，则分步进行
  - tester:主要用于检测生成的代码或者plantUML是否正确，毕竟不能直接用于生成图片
- 使用文档：
  - 由于原论文提供的代码基本没有使用文档或者说明文档，为了之后的开发方便，会按照工作进度持续跟进说明文档的编写
- 可改进的地方:
  - 不一定必须使用gpt3.5，如果coder需要生成代码，claude 3.5 或者 deepseek-R2 是更好的选择，由用户决定


