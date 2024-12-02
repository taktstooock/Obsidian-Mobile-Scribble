import re
from datetime import datetime, timedelta
import locale

class TemplateEngine:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

    def process(self, content, target_date=None):
        if target_date is None:
            target_date = datetime.now()
        elif isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d')

        # 日付プレースホルダの処理
        date_pattern = r'\{\{Date:([^}]+)\}\}'
        content = re.sub(date_pattern, lambda m: self._process_date(m, target_date), content)

        # テンプレートスクリプトの処理
        script_pattern = r'<%\*([\s\S]*?)%>'
        content = re.sub(script_pattern, lambda m: self._process_links(target_date), content)

        return content

    def _process_date(self, match, date):
        format_str = match.group(1)
        # 曜日の日本語変換用マッピング
        weekday_jp = ['月', '火', '水', '木', '金', '土', '日']
        
        if 'ddd' in format_str:
            # 曜日を日本語に変換
            weekday = weekday_jp[date.weekday()]
            format_str = format_str.replace('ddd', weekday)

        # YYYYなどの形式を一時的なプレースホルダに変換
        temp_format = format_str.replace('YYYY', '{YYYY}')\
                               .replace('MM', '{MM}')\
                               .replace('DD', '{DD}')
        
        # プレースホルダを実際の値に置換
        formatted = temp_format.format(
            YYYY=date.strftime('%Y'),
            MM=date.strftime('%m'),
            DD=date.strftime('%d')
        )
        
        # 最後に残りの装飾を処理
        formatted = formatted.replace('[年]', '年')\
                           .replace('[月]', '月')\
                           .replace('[日(]', '日(')\
                           .replace('[)]', ')')
        
        return formatted

    def _process_links(self, date):
        # 1週間前の日付
        last_week = date - timedelta(days=7)
        # 前日の日付
        yesterday = date - timedelta(days=1)
        # 翌日の日付
        tomorrow = date + timedelta(days=1)

        links = []
        links.append(f"☝ [[{last_week.strftime('%Y-%m-%d')}]]")
        links.append(f"⇦ [[{yesterday.strftime('%Y-%m-%d')}]]")
        links.append(f"➡ [[{tomorrow.strftime('%Y-%m-%d')}]]")

        return '\n'.join(links)

    def process_template(self, template_path, target_date, output_path):
        # テンプレートファイルを読み込む
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # テンプレートを処理
        processed_content = self.process(template_content, target_date)
        
        # 処理結果を保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

if __name__ == '__main__':
    engine = TemplateEngine()
    engine.process_template('temp_daily.md', datetime.now(), 'output.md')