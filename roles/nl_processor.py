from pathlib import Path
import logging

class NLProcessor():
    def __init__(self):
        """纯文本处理器，仅负责文件读取"""
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_text_file(self, txt_path: Path) -> str:
        """
        读取TXT文件内容并返回清理后的业务场景字符串
        """
        self.logger.info(f"开始处理文本文件: {txt_path}")

        # 1. 直接读取文本内容
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
        except Exception as e:
            self.logger.error(f"文件读取失败: {str(e)}")
            raise

        # 2. 简单清理文本（可选）
        cleaned_content = self._clean_text_content(raw_content)

        return cleaned_content

    def _clean_text_content(self, text: str) -> str:
        """
        基本文本清理（按需调整）
        """
        # 移除多余空行和首尾空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
