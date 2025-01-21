import os
import re
from datetime import datetime

class DailyNoteInterpreter:
    def __init__(self, daily_note_file_path):
        self.daily_note_file = open(daily_note_file_path, 'r', encoding='utf-8')

        if not self.daily_note_file:
            raise FileNotFoundError(f"File {daily_note_file_path} not found")
        if not daily_note_file_path.endswith('.md'):
            raise ValueError("File must be a markdown file")
        
        self.content = self.daily_note_file.read()
        self.date = datetime.strptime(os.path.basename(daily_note_file_path).split('.')[0], '%Y-%m-%d')

    def __del__(self):
        self.daily_note_file.close()
    
    def extract_entries(self):
        journal_entries = []
        journal_section = re.search(r'# journal(.*?)(?=\n#|\Z)', self.content, re.DOTALL)
        if journal_section:
            entries = re.findall(r'- (\d{2}:\d{2}:\d{2}) (.+)', journal_section.group(1))
            for entry in entries:
                time_str, text = entry
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                time_obj = datetime.combine(self.date, time_obj)
                journal_entries.append((time_obj, text))

        return journal_entries
    
    def update_entries(self, journal_entries):
        journal_section = re.search(r'# journal(.*?)(?=\n#|\Z)', self.content, re.DOTALL)
        if journal_section:
            updated_journal_section = journal_section.group(0)
            for time, text in journal_entries:
                if time.date() != self.date:
                    raise ValueError("Memo date does not match daily note date")
                time_str = time.strftime('%H:%M:%S')
                updated_journal_section += f'- {time_str} {text}\n'
            self.content = self.content.replace(journal_section.group(0), updated_journal_section)
            self.daily_note_file.seek(0)
            self.daily_note_file.truncate()
            self.daily_note_file.write(self.content)
            self.daily_note_file.flush()
        else:
            raise ValueError("Journal section not found in daily note file")

def parse_dailynotes(directory_path):
    journal_entries = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.md'):
            daily_note_file_path = os.path.join(directory_path, filename)
            interpreter = DailyNoteInterpreter(daily_note_file_path)
            journal_entries.extend(interpreter.extract_entries())

    return journal_entries

if __name__ == '__main__':
    journal_entries = parse_dailynotes('daily')
    for time, text in journal_entries:
        print(f'{time}: {text}')