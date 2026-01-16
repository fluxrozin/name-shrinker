import json
import os
import re
import sys
from pathlib import Path


def replace_invalid_characters(name):
    # 指定された文字をアンダーバーに置換
    for ch in ["\n", "\r", "/", ".", ".."]:
        name = name.replace(ch, "_")
    return name


def process_and_rename_files(path):
    # フォルダ内の全ファイルを対象に処理
    for filename in os.listdir(path):
        # ファイルのフルパスを取得
        full_path = os.path.join(path, filename)

        # ディレクトリはスキップ
        if os.path.isdir(full_path):
            continue

        # exeファイル（自分自身）はスキップ
        if filename.lower().endswith(".exe"):
            continue

        # ファイル名と拡張子を分離
        name, ext = os.path.splitext(filename)

        # 拡張子を除いたファイル名に無効な文字が含まれている場合、それをアンダーバーに置換
        name = replace_invalid_characters(name)

        # 非UTF-8文字をアンダーバーに置換
        try:
            name.encode("utf-8")
        except UnicodeEncodeError:
            name = re.sub(r"[^\x00-\x7F]+", "_", name)

        # 新しいファイル名を再構築
        new_filename = name + ext
        new_full_path = os.path.join(path, new_filename)

        # ファイル名が143バイトを超える場合、リネーム対象として処理
        if len(new_filename.encode("utf-8")) > 143:
            # 先頭68バイトの文字列を取得
            head = name[:68].encode("utf-8")[:68].decode("utf-8", "ignore")
            # 後ろ68バイトの文字列を取得
            tail = name[-68:].encode("utf-8")[-68:].decode("utf-8", "ignore")

            # 新しいファイル名を生成
            new_filename = f"{head}...{tail}{ext}"
            new_full_path = os.path.join(path, new_filename)

        # ファイル名が変更された場合のみリネーム
        if full_path != new_full_path:
            if os.path.exists(full_path):
                os.rename(full_path, new_full_path)
                print(f"Renamed '{filename}' to '{new_filename}'")
            else:
                print(f"File not found: {full_path}")


def get_config_path():
    """設定ファイルのパスを取得"""
    appdata = os.getenv("APPDATA")
    if appdata is None:
        # APPDATAが設定されていない場合はカレントディレクトリを使用
        appdata = os.getcwd()
    config_dir = Path(appdata) / "name-shrinker"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config():
    """設定を読み込む"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def main():
    """CLIモードのメイン関数"""
    # 設定ファイルから対象フォルダを読み込む
    config = load_config()
    target_folder = config.get("target_folder")

    if target_folder and os.path.exists(target_folder):
        folder_path = target_folder
        print(f"設定ファイルから読み込んだ処理対象フォルダ: {folder_path}")
    else:
        # 設定がない場合は従来通りexeと同じフォルダを使用
        if getattr(sys, "frozen", False):
            # PyInstallerでexe化された場合
            folder_path = os.path.dirname(sys.executable)
        else:
            # 通常のPythonスクリプトとして実行された場合
            folder_path = os.path.dirname(os.path.abspath(__file__))
        print(f"処理対象フォルダ: {folder_path}")

    print("ファイル名の処理を開始します...\n")

    # ファイル名の処理とリネームを実行
    process_and_rename_files(folder_path)

    print("\n処理が完了しました。")
    input("Enterキーを押して終了してください...")


if __name__ == "__main__":
    # --cli オプションがある場合のみCLIモードで起動
    # それ以外はデフォルトでGUIモードで起動
    if "--cli" in sys.argv:
        main()
    else:
        try:
            from gui import main as gui_main

            gui_main()
        except ImportError:
            # GUIモジュールがインポートできない場合はCLIモードで実行
            main()
