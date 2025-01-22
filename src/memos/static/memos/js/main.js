class MemoApp {
    constructor() {
        this.editor = document.getElementById('memo-content');
        this.saveButton = document.getElementById('save-button');
        this.syncButton = document.getElementById('vault-sync-button');
        this.memoList = document.getElementById('memo-list-container');
        this.setupSync();
        this.setupButtons();
        this.setupEditor();
    }

    setupSync() {
        // 定期的な同期
        setInterval(() => this.fetchMemos(), 600000);
        // 初回読み込み
        this.fetchMemos();
    }

    async saveMemo() {
        this.saveButton.disabled = true;
        const content = this.editor.value;
        try {
            const response = await fetch('memos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ content }),
            });
            if (!response.ok) throw new Error('Failed to save memo');
            this.editor.value = '';
            this.saveButton.disabled = false;
            await this.fetchMemos(); // 保存成功後に同期を実行
        } catch (error) {
            // オフライン時はローカルストレージに保存
            localStorage.setItem('pendingMemo', content);
            console.log('Failed to save memo:', error);
            this.saveButton.disabled = false;
        }
    }

    async fetchMemos() {
        try {
            const response = await fetch('memos/');
            const data = await response.json();
            console.log('Memo list:', data);
            // オブジェクトから配列に変換してマッピング
            const sortedMemos = Object.entries(data.memos).sort((a, b) => {
                return new Date(b[1][1]) - new Date(a[1][1]);
            });
            this.memoList.innerHTML = sortedMemos.map(([id, [content, time, is_synced]]) =>
                `<li id="${id}" class="synced-${is_synced}"><time class="created-at" datetime="${time}">${time}</time>${this.parseText(content)}</li>`
            ).join('');
        } catch (error) {
            console.log('Failed to sync memos:', error);
        }
    }

    async syncMemos() {
        this.syncButton.disabled = true;
        this.syncButton.innerHTML = '<div class="loader">Syncing...</div>';
        this.syncButton.classList.add('syncing');
        try {
            const response = await fetch('sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });
            if (!response.ok) throw new Error('Failed to sync memos');
            await this.fetchMemos();
            this.syncButton.textContent = 'Success!';
            this.syncButton.classList.remove('syncing');
            this.syncButton.classList.add('success');
        } catch (error) {
            console.log('Failed to sync memos:', error);
            this.syncButton.textContent = 'Failed!';
            this.syncButton.classList.remove('syncing');
            this.syncButton.classList.add('failed');
        } finally {
            setTimeout(() => {
                this.syncButton.disabled = false;
                this.syncButton.textContent = 'Sync';
                this.syncButton.classList.remove('success', 'failed', 'syncing');
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

    setupEditor() {
        this.editor.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.key === 'Enter') {
                this.saveMemo();
            }
        });
    }

    parseText(text) {
        text = text
            .replace(/</g, '&lt;').replace(/>/g, '&gt;') // タグをエスケープ
            .replaceAll('\n', '<br>') // 改行を<br>に変換
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
