// Service Workerの登録
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/memos/js/sw.js');
}

class MemoApp {
    constructor() {
        this.editor = document.getElementById('memo-content');
        this.setupAutoSave();
        this.setupSync();
    }

    setupAutoSave() {
        let timeout;
        this.editor.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this.saveMemo(), 2000);
        });
    }

    setupSync() {
        // 定期的な同期
        setInterval(() => this.syncMemos(), 60000);
        // 初回読み込み
        this.syncMemos();
    }

    async saveMemo() {
        const content = this.editor.value;
        try {
            const response = await fetch('/app/memos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ content }),
            });
            if (!response.ok) throw new Error('Failed to save memo');
        } catch (error) {
            // オフライン時はローカルストレージに保存
            localStorage.setItem('pendingMemo', content);
        }
    }

    async syncMemos() {
        try {
            const response = await fetch('/app/memos/');
            const data = await response.json();
            // メモの表示処理
            console.log(data);
        } catch (error) {
            console.log('Failed to sync memos:', error);
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// アプリの初期化
document.addEventListener('DOMContentLoaded', () => {
    new MemoApp();
});
