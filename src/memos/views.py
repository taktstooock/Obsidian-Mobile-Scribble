from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Memo
from .sync import Sync, VaultDatabaseSync
import json
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(TemplateView, LoginRequiredMixin):
    template_name = 'memos/index.html'

class MemoView(View):
    def get(self, request):        
        # メモを取得
        memos = Memo.objects.filter(author=request.user)
        # 最新の20件を取得
        memos = memos.order_by('-created_at')[:20]
        memos = {memo.id: memo.content for memo in memos}
        return JsonResponse({'memos': memos})
    
    def post(self, request):
        data = json.loads(request.body.decode())
        content = data['content']

        # メモを保存
        memo = Memo.objects.create(
            content=content,
            author=request.user
        )

        vaultdatabasesync = VaultDatabaseSync(request.user)
        vaultdatabasesync.db2vault()
        
        return JsonResponse({'id': memo.id})
    
class SyncView(View):
    def post(self, request):
        sync = Sync(request.user)
        sync.sync()
        return JsonResponse({'status': 'success'})