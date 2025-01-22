// Service Workerの登録
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/memos/js/sw.js');
}

class MemoApp {
    constructor() {
        this.editor = document.getElementById('memo-content');
        this.saveButton = document.getElementById('save-button');
        this.syncButton = document.getElementById('vault-sync-button');
        this.memoList = document.getElementById('memo-list-container');
        this.setupSync();
        this.setupButtons();
    }

    setupSync() {
        // 定期的な同期
        setInterval(() => this.fetchMemos(), 600000);
        // 初回読み込み
        this.fetchMemos();
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
            await this.fetchMemos(); // 保存成功後に同期を実行
        } catch (error) {
            // オフライン時はローカルストレージに保存
            localStorage.setItem('pendingMemo', content);
        }
    }

    async fetchMemos() {
        try {
            const response = await fetch('/app/memos/');
            const data = await response.json();
            console.log('Memo list:', data);
            // オブジェクトから配列に変換してマッピング
            this.memoList.innerHTML = Object.entries(data.memos).map(([id, content]) => 
                `<li>${this.parseText(content)}</li>`
            ).join('');
        } catch (error) {
            console.log('Failed to sync memos:', error);
        }
    }

    async syncMemos() {
        this.syncButton.disabled = true;
        this.syncButton.textContent = '同期中...';
        try {
            const response = await fetch('/app/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });
            if (!response.ok) throw new Error('Failed to sync memos');
            await this.fetchMemos();
            this.syncButton.textContent = '同期成功';
        } catch (error) {
            console.log('Failed to sync memos:', error);
            this.syncButton.textContent = '同期失敗';
        } finally {
            setTimeout(() => {
                this.syncButton.disabled = false;
                this.syncButton.textContent = '同期';
            }, 2000);
        }
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    setupButtons() {
        this.saveButton.addEventListener('click', () => {
            this.saveMemo();
        });
        this.syncButton.addEventListener('click', () => {
            this.syncMemos();
        });
    }

    parseText(text) {
        text = text.replaceAll('\n', '<br>') // 改行を<br>に変換
            .replace(/\[(.*?)\]\((https?:\/\/\S+)\)/g, '<a href="$2">$1</a>') // リンクを変換
            .replace(/(\*\*|__)(.*?)\1/g, '<strong>$2</strong>') // 強調を太字に変換
            .replace(/(\*|_)(.*?)\1/g, '<em>$2</em>') // 斜体を変換
            ;
        return text;
    }
}

// アプリの初期化
document.addEventListener('DOMContentLoaded', () => {
    new MemoApp();
});
