from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Memo
from .sync import Sync
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime

class IndexView(TemplateView, LoginRequiredMixin):
    template_name = 'memos/index.html'

class MemoView(View):
    def get(self, request):        
        # メモを取得
        memos = Memo.objects.filter(author=request.user)
        # 最新の40件を取得
        memos = memos.order_by('created_at').reverse()[:40]
        memos = {memo.id: (
            memo.content,
            datetime.strftime(timezone.localtime(memo.created_at), "%Y/%m/%d %H:%M:%S"),
            bool(memo.vault_synced_at)
            ) for memo in memos}
        return JsonResponse({'memos': memos})
    
    def post(self, request):
        data = json.loads(request.body.decode())
        content = data['content']
        if not content:
            return JsonResponse({'error': 'content is empty'}, status=400)

        # メモを保存
        memo = Memo.objects.create(
            content=content,
            author=request.user
        )
        
        return JsonResponse({'id': memo.id})
    
class SyncView(View):
    def post(self, request):
        print('syncing')
        # sync = Sync(request.user)
        # sync.sync()
        import time
        time.sleep(10)
        return JsonResponse({'status': 'success'})