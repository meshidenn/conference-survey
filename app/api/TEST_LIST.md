# テストリスト

## Phase 1: ドメインモデル ✅

### 値オブジェクト
- [x] SurveyId: UUIDとして生成される
- [x] PaperId: 文字列として生成される
- [x] TagId: UUIDとして生成される
- [x] ConferenceType: ACL, NAACL, EMNLP, EACLのenum
- [x] Conference: 学会種別と年度を持つ
- [x] Conference: 年度は1900-2100の範囲

### Paper
- [x] Paper: id, title, authors, abstractを持つ
- [x] Paper: tagsは空リストで初期化
- [x] Paper: characteristicsはNoneで初期化
- [x] Paper: タグを追加できる
- [x] Paper: 特徴を設定できる

### TagNode
- [x] TagNode: id, name, parent_id, child_idsを持つ
- [x] TagNode: paper_idsは空リストで初期化
- [x] TagNode: summaryはNoneで初期化
- [x] TagNode: 子ノードを追加できる
- [x] TagNode: 論文を関連付けできる
- [x] TagNode: paper_countはpaper_idsの数を返す
- [x] TagNode: ルートノードの判定ができる

### TagHierarchy
- [x] TagHierarchy: ノードを追加できる
- [x] TagHierarchy: ルートノードを取得できる
- [x] TagHierarchy: 葉ノードを取得できる
- [x] TagHierarchy: ボトムアップ順でノードを取得できる

### Survey (集約ルート)
- [x] Survey: id, conference, statusを持つ
- [x] Survey: 初期statusはpending
- [x] Survey: papersは空リストで初期化
- [x] Survey: tag_hierarchyは空で初期化
- [x] Survey: 論文を追加できる
- [x] Survey: statusを更新できる
- [x] Survey: 処理中にできる
- [x] Survey: 完了にできる
- [x] Survey: 失敗にできる

## Phase 2: 論文取得 ✅
- [x] PaperFetcherインターフェース定義
- [x] FetcherFactory: ConferenceTypeから適切なFetcherを返す
- [x] AclAnthologyFetcher: 論文リストを取得できる（モック）
- [x] CreateSurveyUseCase: サーベイを作成できる

## Phase 3: タグ生成・階層化 ✅
- [x] LLMクライアントインターフェース定義
- [x] TagGeneratorAgent: abstractからタグを生成できる
- [x] HierarchyAgent: 類似タグを統合できる
- [x] HierarchyAgent: タグを階層化できる

## Phase 4: 要約・特徴抽出 ✅
- [x] SummaryAgent: 要約を生成できる
- [x] CharacteristicAgent: 論文の特徴を抽出できる
- [x] ProcessSurveyUseCase: 全処理を統括できる

## Phase 5: API完成 ✅
- [x] POST /surveys: サーベイ作成エンドポイント
- [x] GET /surveys/{id}: サーベイ詳細エンドポイント
- [x] GET /surveys: サーベイ一覧エンドポイント
- [x] POST /surveys/{id}/process: 処理実行エンドポイント（非同期）
- [x] GET /surveys/{id}/mindmap: マインドマップ用データエンドポイント
