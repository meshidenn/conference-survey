# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

学会でpublishされたpaperについて、概要とその年の傾向を簡単に把握するためのアプリ。accepted paperのリストからタグを生成・階層化し、要約をマインドマップで表示する。

## 開発手法

- **DDD（ドメイン駆動設計）**: ドメインモデルを中心に設計
- **TDD（テスト駆動開発）**: テストリスト作成→テスト実装→プロダクトコード→リファクタリングのサイクル
- **Clean Architecture**: 依存関係は外側から内側へ

## 技術スタック

- **Backend**: Python + FastAPI
- **Agent**: Google ADK
- **パッケージ管理**: uv（pipは使用しない）

## コマンド

```bash
# バックエンド（app/api/ディレクトリで実行）
cd app/api

# 依存関係のインストール
uv sync

# パッケージ追加
uv add <package>
uv add --dev <package>  # 開発用

# テスト実行
uv run pytest
uv run pytest tests/path/to/test_file.py::test_function  # 単一テスト
uv run pytest -v  # 詳細出力

# サーバー起動
uv run uvicorn src.entrypoint.main:app --reload

# Lint/Format
uv run ruff check .
uv run ruff format .
```

## アーキテクチャ（Clean Architecture）

```
app/
├── api/                        # バックエンド（Python）
│   ├── pyproject.toml
│   ├── src/
│   │   ├── entrypoint/         # アプリ起動
│   │   │   └── main.py
│   │   ├── core/               # 設定・ログ
│   │   ├── models/             # ドメインモデル
│   │   ├── schemas/            # Pydantic I/Oスキーマ
│   │   ├── services/           # ユースケース層
│   │   ├── repositories/       # データアクセス層
│   │   ├── routes/             # エンドポイント
│   │   └── exceptions/         # 例外ハンドラ
│   └── tests/
│       ├── conftest.py
│       └── ...
│
└── web/                        # フロントエンド
    └── ...
```

## コーディング規約

- PEP8準拠、型ヒント必須（PEP 585組み込みジェネリクス使用、typingは不使用）
- Docstring: Googleスタイル、日本語で記載
- 命名: 変数・関数は`snake_case`、クラスは`PascalCase`
- API: JSONは`camelCase`、内部は`snake_case`（Pydantic aliasで変換）
- DB: テーブル・カラム名は`snake_case`
- ライセンス: 非コピーレフト推奨（Apache, MIT, BSD, AFL, ISC, PFS）

## TDDの進め方

1. テストリストを作成
2. リストから1つ選び、失敗するテストを書く
3. テストを通すプロダクトコードを書く（気づきはテストリストに追加）
4. リファクタリング
5. テストリストが空になるまで繰り返す
