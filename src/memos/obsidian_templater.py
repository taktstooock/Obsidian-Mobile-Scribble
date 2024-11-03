import re
from datetime import datetime

class TemplateEngine:
    def process(self, content):
        # 日付プレースホルダの処理
        date_pattern = r'\{\{Date:([^}]+)\}\}'
        content = re.sub(date_pattern, self._process_date, content)
        return content
    
    def _process_date(self, match):
        format_str = match.group(1)
        # YYYYなどの形式をPythonの日付フォーマットに変換
        format_str = format_str.replace('YYYY', '%Y')\
                              .replace('MM', '%m')\
                              .replace('DD', '%d')\
                              .replace('ddd', '%a')\
                              .replace('[', '')\
                              .replace(']', '')
        return datetime.now().strftime(format_str)