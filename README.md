# Obsidian-Mobile-Scribble

## システム仕様
Generated with GPT-4o

### 1. システム概要
   - **システム名**: Obsidian mobile scribble
   - **概要**: 本システムは、Obsidianのようなメモ管理とテンプレート機能を備えたモバイル向けのWebアプリです。Djangoを用いたフルスタック開発を行い、ユーザーが簡単にアクセスできるように、インストール可能なPWA（プログレッシブウェブアプリケーション）として提供されます。
   - **技術スタック**: Django 5.1, JavaScript, HTML, CSS

### 2. 主要機能
   - **メモの作成・保存**: タイトルやタグは付与せず、シンプルなテキストメモを作成・保存する機能を提供。
   - **オリジナルテンプレートエンジンの実装**: Obsidian Templaterで利用するようなテンプレート機能を独自に実装。特定の埋め込み構文を解析し、指定したプレースホルダに動的な情報（例: 日付やリンク）を自動挿入します。
   - **PWA対応**: Service Workerを利用してキャッシュやオフライン機能を実現し、ユーザーのデバイスにインストール可能なWebアプリとして提供。
   
### 3. システム構成
   本システムは以下の3つの主要な構成要素で成り立っています。

   - **バックエンド (Django)**  
     Djangoでメモ保存とテンプレート解析のバックエンドロジックを提供します。Djangoの標準機能を活用しつつ、テンプレートエンジンは自作して動的なテンプレート処理を行います。

   - **フロントエンド (HTML/JavaScript/CSS)**  
     JavaScriptとHTMLテンプレートで、メモの表示や編集インターフェースを構築。PWAのインストール促進や、Service Workerでのオフライン対応を行います。

   - **Service Worker**  
     メモアプリのオフラインアクセスをサポートするため、Service Workerを利用してリソースをキャッシュし、アプリの一部機能をオフラインでも利用可能にします。
### 4. 機能詳細
#### メモ管理
   - メモの作成・編集・削除が可能。
   - テキスト入力フィールドのみで、タイトルやタグは持たないシンプルな構成。
   - メモはデータベースに保存され、作成日時と更新日時が自動的に記録される。
   - ユーザーが閲覧するたびにfetchして、最新のメモを表示する。
    - 定期的にfetchもする。
   - vaultレポジトリに更新があるたびにpullして、markdownからメモをインポートする。
   - POSTがあったらmarkdownに反映し、pushする。
##### conflict
   - ローカルのメモとリモートのメモが競合した場合、リモートのメモを優先する。
#### オリジナルテンプレートエンジン
   - Djangoのテンプレートエンジンではなく、自作のテンプレートエンジンでプレースホルダ（例：`{{ Date }}`）を動的に置換。
   - テンプレートエンジンには以下の埋め込み関数を実装予定：
     - `{{ Date }}`: 現在の日付を指定のフォーマットで挿入。
        - 使用例: `{{Date:YYYY[年]MM[月]DD[日(]ddd[)]}}` → `2022年01月01日(土)`
#### PWA対応
   - **Service Worker**を利用し、アプリのリソース（CSS, JavaScript, 画像など）をキャッシュすることで、オフラインでもメモの閲覧が可能に。
    - **オフライン対応**: オフライン時にはキャッシュされたリソースを利用し、メモの閲覧や編集が可能。
      - オフライン時に作成されたメモは、オンラインになった際に自動的にサーバーに同期される。
   - **アプリのインストール**: PWA対応により、ユーザーは「ホーム画面に追加」オプションからアプリをインストール可能。  
#### ユーザー認証
   - obsidianのvaultのあるリポジトリの認証情報をユーザーモデルに持たせる。
   - ユーザー認証にはDjangoの標準機能を利用し、ユーザーごとにメモを管理。
### 5. システム設計
#### モデル設計
   - **Memoモデル**
     ```python
     from django.db import models

     class Memo(models.Model):
         content = models.TextField()
         author = models.ForeignKey(User, on_delete=models.CASCADE)
         created_at = models.DateTimeField(auto_now_add=True)
         updated_at = models.DateTimeField(auto_now=True)
     ```
- **Userモデル**
  ```python
  from django.contrib.auth.models import AbstractUser

  class User(AbstractUser):
	  vault_path = models.CharField(max_length=255)
    repo_url = models.CharField(max_length=255)
	  access_token = models.CharField(max_length=255)
  ```
   #### テンプレートエンジン設計
   - **テンプレート解析関数**
     テンプレートの解析に必要なプレースホルダを正規表現で検索し、対応するデータに置換します。例えば、メモの内容内に`{{ Date }}`があれば現在の日付で置換します。
     ```python
     import re
     from datetime import datetime

     def render_template(content):
         content = re.sub(r'\{\{Date:YYYY\[年\]MM\[月\]DD\[日\]\}\}', datetime.now().strftime('%Y年%m月%d日'), content)
         # 他のプレースホルダも同様に置換
         return content
     ```
   #### Service Worker設定
   - **service-worker.js**ファイルで、リソースのキャッシュと、オフライン時のフォールバック処理を実装します。
     ```javascript
     self.addEventListener('install', (event) => {
         event.waitUntil(
             caches.open('obsidian-mobile-scribble-v1').then((cache) => {
                 return cache.addAll([
                     '/',
                     '/static/css/main.css',
                     '/static/js/main.js',
                     '/offline.html',
                 ]);
             })
         );
     });

     self.addEventListener('fetch', (event) => {
         event.respondWith(
             caches.match(event.request).then((response) => {
                 return response || fetch(event.request);
             }).catch(() => caches.match('/offline.html'))
         );
     });
     ```
### 6. UIとUX設計
   - モバイルファーストでシンプルなUIデザインを採用。メモ一覧表示や編集画面は最小限のナビゲーションで操作できるようにします。
   - メモの自動保存やユーザーインターフェースの最適化により、快適なメモ作成環境を提供します。