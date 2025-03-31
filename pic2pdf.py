import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap
from fpdf import FPDF


class DropArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("拖放图片到这里")
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f0f0f0;
            }
        """
        )
        self.setAcceptDrops(True)
        self.image_paths = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                """
                QLabel {
                    border: 2px dashed #555;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #e0e0e0;
                }
            """
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f0f0f0;
            }
        """
        )

    def dropEvent(self, event):
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 20px;
                background-color: #f0f0f0;
            }
        """
        )

        new_images_added = 0
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                if file_path not in self.image_paths:
                    self.image_paths.append(file_path)
                    new_images_added += 1

        if new_images_added > 0:
            self.setText(
                f"已添加 {new_images_added} 张图片\n当前共 {len(self.image_paths)} 张图片\n继续拖放可添加更多"
            )
        else:
            self.setText(
                f"没有新增有效图片\n当前共 {len(self.image_paths)} 张图片\n继续拖放可添加更多"
            )

    def clear_images(self):
        self.image_paths = []
        self.setText("拖放图片到这里")


class PDFGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转PDF工具")
        self.setFixedSize(500, 250)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)

        self.filename_label = QLabel("PDF文件名 (无需扩展名):")
        layout.addWidget(self.filename_label)

        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("例如: 实验X00XYZ")
        layout.addWidget(self.filename_input)

        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("生成PDF")
        self.generate_btn.clicked.connect(self.generate_pdf)
        button_layout.addWidget(self.generate_btn)

        self.clear_btn = QPushButton("清空图片")
        self.clear_btn.clicked.connect(self.clear_images)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        self.status_label = QLabel("准备就绪")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def generate_pdf(self):
        if not self.drop_area.image_paths:
            self.status_label.setText("错误: 请先添加图片")
            self.status_label.setStyleSheet("color: red;")
            return

        filename = self.filename_input.text().strip()
        if not filename:
            self.status_label.setText("错误: 请输入文件名")
            self.status_label.setStyleSheet("color: red;")
            return

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存PDF文件",
            os.path.join(os.path.expanduser("~"), "Desktop", filename),
            "PDF文件 (*.pdf)",
        )

        if not save_path:
            return

        try:
            pdf = FPDF()

            for image_path in self.drop_area.image_paths:
                img = QPixmap(image_path)
                width, height = img.width(), img.height()

                pdf.add_page()
                pdf.image(image_path, x=10, y=10, w=190, h=(190 * height / width))

            pdf.output(save_path)

            self.status_label.setText(
                f"PDF已成功生成: {save_path}\n共包含 {len(self.drop_area.image_paths)} 张图片"
            )
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"错误: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def clear_images(self):
        self.drop_area.clear_images()
        self.status_label.setText("已清空所有图片")
        self.status_label.setStyleSheet("color: blue;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFGeneratorApp()
    window.show()
    sys.exit(app.exec_())
