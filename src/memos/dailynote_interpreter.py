import os
import re
from datetime import datetime

def parse_dailynotes(directory):
    journal_entries = []

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                journal_section = re.search(r'# journal(.*?)(?=\n#|\Z)', content, re.DOTALL)
                if journal_section:
                    date = datetime.strptime(filename.split('.')[0], '%Y-%m-%d')
                    entries = re.findall(r'- (\d{2}:\d{2}:\d{2}) (.+)', journal_section.group(1))
                    for entry in entries:
                        time_str, text = entry
                        time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                        time_obj = datetime.combine(date, time_obj)
                        journal_entries.append((time_obj, text))

    return journal_entries

if __name__ == '__main__':
    journal_entries = parse_dailynotes('daily')
    for time, text in journal_entries:
        print(f'{time}: {text}')