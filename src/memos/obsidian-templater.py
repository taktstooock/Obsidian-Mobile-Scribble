import re
from datetime import datetime

class TemplateEngine:
    def __init__(self):
        self.patterns = {
            'date': r'\{\{Date:([^}]+)\}\}'
        }
    
    def process(self, content):
        content = self._process_date(content)
        return content
    
    def _process_date(self, content):
        def replace_date(match):
            format_str = match.group(1)
            now = datetime.now()
            return now.strftime(format_str)
        
        return re.sub(self.patterns['date'], replace_date, content)