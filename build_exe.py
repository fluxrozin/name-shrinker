"""PyInstallerでexeファイルをビルドするスクリプト"""

import PyInstaller.__main__

# ビルド設定（GUIモード）
PyInstaller.__main__.run(
    [
        "main.py",
        "--onefile",  # 単一のexeファイルにまとめる
        "--windowed",  # GUIモード（コンソールウィンドウを表示しない）
        "--name=name-shrinker",  # exeファイル名
        "--clean",  # ビルド前に一時ファイルをクリーンアップ
        "--noconfirm",  # 上書き確認なし
        "--hidden-import=PyQt6",  # PyQt6を明示的に含める
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
    ]
)

print("\nビルドが完了しました。distフォルダにexeファイルが生成されています。")
