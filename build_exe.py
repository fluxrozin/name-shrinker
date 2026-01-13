"""PyInstallerでexeファイルをビルドするスクリプト"""

import PyInstaller.__main__  # type: ignore[import-untyped]

# ビルド設定
PyInstaller.__main__.run(
    [
        "main.py",
        "--onefile",  # 単一のexeファイルにまとめる
        "--console",  # コンソールウィンドウを表示
        "--name=name-shrinker",  # exeファイル名
        "--clean",  # ビルド前に一時ファイルをクリーンアップ
        "--noconfirm",  # 上書き確認なし
    ]
)

print("\nビルドが完了しました。distフォルダにexeファイルが生成されています。")
