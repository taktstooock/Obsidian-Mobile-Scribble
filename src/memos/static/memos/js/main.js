// Service Workerの登録
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/memos/js/sw.js');
}

class MemoApp {
    constructor() {
        this.editor = document.getElementById('memo-content');
        this.saveButton = document.getElementById('save-button');
        this.memoList = document.getElementById('memo-list-container');
        this.setupSync();
        this.setupSaveButton();
    }

    setupSync() {
        // 定期的な同期
        setInterval(() => this.syncMemos(), 600000);
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
            await this.syncMemos(); // 保存成功後に同期を実行
        } catch (error) {
            // オフライン時はローカルストレージに保存
            localStorage.setItem('pendingMemo', content);
        }
    }

    async syncMemos() {
        try {
            const response = await fetch('/app/memos/');
            const data = await response.json();
            console.log('Memo list:', data);
            // オブジェクトから配列に変換してマッピング
            this.memoList.innerHTML = Object.entries(data.memos).map(([id, content]) => 
                `<li>${content}</li>`
            ).join('');
        } catch (error) {
            console.log('Failed to sync memos:', error);
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    setupSaveButton() {
        this.saveButton.addEventListener('click', () => {
            this.saveMemo();
        });
    }
}

// アプリの初期化
document.addEventListener('DOMContentLoaded', () => {
    new MemoApp();
});
