"""PyQt6で実装されたGUIアプリケーション"""

import json
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from main import process_and_rename_files


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


def save_config(config):
    """設定を保存する"""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Name Shrinker")
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 説明ラベル
        info_label = QLabel("対象フォルダを選択してください：")
        layout.addWidget(info_label)

        # フォルダパス表示ラベル
        self.path_label = QLabel("（未設定）")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet(
            "padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout.addWidget(self.path_label)

        # フォルダ選択ボタン
        select_button = QPushButton("フォルダを選択")
        select_button.clicked.connect(self.select_folder)
        layout.addWidget(select_button)

        # 処理実行ボタン
        self.process_button = QPushButton("処理を実行")
        self.process_button.clicked.connect(self.process_files)
        self.process_button.setEnabled(False)
        layout.addWidget(self.process_button)

        # 設定を読み込んで表示
        self.config = load_config()
        self.update_path_display()

    def select_folder(self):
        """フォルダ選択ダイアログを表示"""
        # 既存のパスがあればそれを初期値として使用
        initial_dir = self.config.get("target_folder", "")
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")

        folder_path = QFileDialog.getExistingDirectory(
            self, "対象フォルダを選択", initial_dir
        )

        if folder_path:
            self.config["target_folder"] = folder_path
            if save_config(self.config):
                self.update_path_display()
            else:
                QMessageBox.warning(self, "エラー", "設定の保存に失敗しました。")

    def update_path_display(self):
        """パス表示を更新"""
        target_folder = self.config.get("target_folder", "")
        if target_folder and os.path.exists(target_folder):
            self.path_label.setText(target_folder)
            self.process_button.setEnabled(True)
        else:
            self.path_label.setText("（未設定）")
            self.process_button.setEnabled(False)

    def process_files(self):
        """ファイル処理を実行"""
        target_folder = self.config.get("target_folder", "")
        if not target_folder or not os.path.exists(target_folder):
            QMessageBox.warning(
                self, "エラー", "対象フォルダが設定されていないか、存在しません。"
            )
            return

        # 処理実行前に確認
        reply = QMessageBox.question(
            self,
            "確認",
            f"以下のフォルダ内のファイル名を処理しますか？\n\n{target_folder}\n\n"
            "ファイル名が変更されます。重要なファイルがある場合は事前にバックアップを取ってください。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 処理実行
                process_and_rename_files(target_folder)
                QMessageBox.information(
                    self, "完了", "ファイル名の処理が完了しました。"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "エラー", f"処理中にエラーが発生しました：\n{str(e)}"
                )


def main():
    """GUIアプリケーションのエントリーポイント"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
