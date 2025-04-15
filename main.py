import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QColorDialog, QComboBox, QSlider
)
from PyQt5.QtGui import QPainter, QPen, QColor, QPalette, QFont, QIcon
from PyQt5.QtCore import Qt, QPoint

CONFIG_FILE = "crosshair_config.json"


class Crosshair(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.resize(200, 200)
        self.show()
        self.update_position()

    def update_position(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.center().x() - self.width() // 2
        y = screen.center().y() - self.height() // 2
        self.move(x, y)

    def set_config(self, config):
        self.config = config
        self.update()

    def paintEvent(self, event):
        self.update_position()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()

        size = self.config.get("size", 10)
        gap = self.config.get("gap", 4)
        thickness = self.config.get("thickness", 2)
        opacity = self.config.get("opacity", 100)
        style = self.config.get("style", "Clássico")
        color = QColor(self.config.get("color", "#00FF00"))
        color.setAlphaF(opacity / 100)

        pen_main = QPen(color, thickness)
        pen_shadow = QPen(QColor(0, 0, 0, 160), thickness + 1)

        def draw_line(x1, y1, x2, y2):
            painter.setPen(pen_shadow)
            painter.drawLine(x1, y1, x2, y2)
            painter.setPen(pen_main)
            painter.drawLine(x1, y1, x2, y2)

        if style == "Clássico":
            draw_line(center.x(), center.y() - gap - size, center.x(), center.y() - gap)
            draw_line(center.x(), center.y() + gap, center.x(), center.y() + gap + size)
            draw_line(center.x() - gap - size, center.y(), center.x() - gap, center.y())
            draw_line(center.x() + gap, center.y(), center.x() + gap + size, center.y())

        elif style == "Círculo":
            painter.setPen(pen_shadow)
            painter.drawEllipse(center, size + 1, size + 1)
            painter.setPen(pen_main)
            painter.drawEllipse(center, size, size)

        elif style == "Ponto":
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(center, size, size)

        elif style == "Retícula":
            draw_line(center.x(), center.y() - gap - size, center.x(), center.y() - gap)
            draw_line(center.x(), center.y() + gap, center.x(), center.y() + gap + size)
            draw_line(center.x() - gap - size, center.y(), center.x() - gap, center.y())
            draw_line(center.x() + gap, center.y(), center.x() + gap + size, center.y())


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sobre o Projeto")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QIcon("icon.ico"))
        self.set_dark_theme()

        layout = QVBoxLayout()
        font_title = QFont("Segoe UI", 12, QFont.Bold)
        font_text = QFont("Segoe UI", 10)

        label_title = QLabel("Mira Overlay - Projeto Open Source")
        label_title.setFont(font_title)
        label_title.setStyleSheet("color: rgb(170, 85, 255);")
        label_title.setAlignment(Qt.AlignCenter)

        label_text = QLabel(
            "Desenvolvido por yrvt\n\n"
            "Repositório GitHub:\n"
            "https://github.com/RevoltadoxDK\n\n"
            "Disponível como .EXE e código-fonte livre"
        )
        label_text.setFont(font_text)
        label_text.setStyleSheet("color: white;")
        label_text.setAlignment(Qt.AlignCenter)
        label_text.setWordWrap(True)

        layout.addWidget(label_title)
        layout.addWidget(label_text)
        self.setLayout(layout)

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(25, 25, 25))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)


class SettingsWindow(QWidget):
    def __init__(self, crosshair_widget):
        super().__init__()
        self.crosshair_widget = crosshair_widget
        self.setWindowTitle("Mira Personalizada • Feito por yrvt")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(420, 400)
        self.set_dark_theme()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        font = QFont("Segoe UI", 10, QFont.Bold)
        self.setFont(font)

        self.size_input = self._create_slider(layout, "Tamanho", 1, 100, "size")
        self.gap_input = self._create_slider(layout, "Espaçamento (Gap)", 0, 50, "gap")
        self.thickness_input = self._create_slider(layout, "Espessura", 1, 10, "thickness")
        self.opacity_input = self._create_slider(layout, "Opacidade", 10, 100, "opacity")

        color_button = QPushButton("Escolher Cor")
        color_button.clicked.connect(self.choose_color)
        layout.addWidget(color_button)

        style_layout = QHBoxLayout()
        style_label = QLabel("Formato:")
        self.set_label_style(style_label)
        style_layout.addWidget(style_label)

        self.style_box = QComboBox()
        self.style_box.addItems(["Clássico", "Círculo", "Ponto", "Retícula"])
        self.style_box.setCurrentText(self.crosshair_widget.config.get("style", "Clássico"))
        self.style_box.currentTextChanged.connect(self.apply_settings)
        style_layout.addWidget(self.style_box)
        layout.addLayout(style_layout)

        about_button = QPushButton("Sobre")
        about_button.clicked.connect(self.open_about)
        layout.addWidget(about_button)

        self.setLayout(layout)

    def _create_slider(self, layout, label_text, min_val, max_val, config_key):
        label = QLabel(label_text)
        self.set_label_style(label)
        layout.addWidget(label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(self.crosshair_widget.config.get(config_key, min_val))
        slider.valueChanged.connect(self.apply_settings)
        layout.addWidget(slider)

        setattr(self, f"{config_key}_slider", slider)
        return slider

    def set_label_style(self, label):
        label.setStyleSheet("color: rgb(170, 85, 255);")

    def choose_color(self):
        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.ShowAlphaChannel, False)
        dialog.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #555;
            }
            QLabel {
                color: white;
            }
        """)
        dialog.setPalette(self.palette())
        if dialog.exec_():
            selected_color = dialog.selectedColor()
            if selected_color.isValid():
                self.crosshair_widget.config["color"] = selected_color.name()
                self.apply_settings()

    def apply_settings(self):
        config = self.crosshair_widget.config
        config["size"] = self.size_slider.value()
        config["gap"] = self.gap_slider.value()
        config["thickness"] = self.thickness_slider.value()
        config["opacity"] = self.opacity_slider.value()
        config["style"] = self.style_box.currentText()
        self.crosshair_widget.set_config(config)
        self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.crosshair_widget.config, f, indent=4)

    def open_about(self):
        self.about_window = AboutWindow()
        self.about_window.show()

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(170, 85, 255))
        dark_palette.setColor(QPalette.Base, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.Text, QColor(200, 200, 255))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(170, 85, 255))
        dark_palette.setColor(QPalette.Highlight, QColor(100, 60, 200))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(dark_palette)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "size": 10,
        "gap": 4,
        "thickness": 2,
        "opacity": 100,
        "color": "#00FF00",
        "style": "Clássico"
    }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = load_config()
    crosshair = Crosshair(config)
    settings = SettingsWindow(crosshair)

    crosshair.show()
    settings.show()

    sys.exit(app.exec_())
