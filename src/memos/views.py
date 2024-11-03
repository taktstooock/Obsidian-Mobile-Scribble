from django.views import View
from django.http import JsonResponse
from .models import Memo
from .obsidian_templater import TemplateEngine
from .git import GitSync
import os

class MemoView(View):
    def get(self, request):
        # Git同期を実行
        repo_path = request.user.vault_path
        git_sync = GitSync(repo_path)
        git_sync.pull()
        
        # メモを取得
        memos = Memo.objects.filter(author=request.user)
        return JsonResponse({'memos': list(memos.values())})
    
    def post(self, request):
        content = request.POST.get('content')
        engine = TemplateEngine()
        processed_content = engine.process(content)
        
        # メモを保存
        memo = Memo.objects.create(
            content=processed_content,
            author=request.user
        )
        
        # Gitにpush
        repo_path = request.user.vault_path
        git_sync = GitSync(repo_path)
        
        # メモをmarkdownファイルとして保存
        filename = f"{memo.created_at.strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(repo_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        git_sync.push()
        
        return JsonResponse({'id': memo.id})