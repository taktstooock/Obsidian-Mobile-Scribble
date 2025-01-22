from django.urls import path
from .views import IndexView, MemoView, SyncView

app_name = 'memos'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('memos/', MemoView.as_view(), name='memos'),
    path('sync/', SyncView.as_view(), name='sync'),
]
