import os
import yaml
from pathlib import Path
from typing import Dict


class ConfigLoader:
    def __init__(self):
        # 加载YAML配置
        config_path = Path(__file__).parent / "config_prod.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        # 优先使用环境变量中的API密钥
        self._config['llm']['api_key'] = os.getenv('OPENAI_API_KEY', self._config['llm']['api_key'])

    def get_llm_config(self) -> Dict[str, str]:
        """获取LLM配置字典"""
        return self._config['llm']


# 单例模式
config = ConfigLoader()