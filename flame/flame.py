import sys

import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt5.QtWidgets import QApplication, QWidget


class FlameWidget(QWidget):
    """
    A widget that displays a flame animation.
    """

    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height

        self.pixmap = QPixmap(width, height)
        self.setFixedSize(width, height)

        self.palette = self.create_palette()
        self.data = np.zeros((height, width), dtype=np.uint8)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def refresh(self):
        # seed the initial row with random values
        self.data[self.height - 1, :] = np.random.randint(0, 255, self.width, dtype=np.uint8)

        # perform the operation
        # x[i, j] = (x[i - 1, j] + x[i - 2, j] + x[i + 1, j] + x[i + 2, j] + x[i, j + 1] * 5) / 9
        x1 = np.roll(self.data, shift=1, axis=1)
        x2 = np.roll(self.data, shift=2, axis=1)
        x3 = np.roll(self.data, shift=-1, axis=1)
        x4 = np.roll(self.data, shift=-2, axis=1)
        x5 = np.roll(self.data, shift=-1, axis=0)

        self.data = ((x1 + x2 + x3 + x4 + x5 * 5) // 9).astype(int)

        # convert data to image using flame palette
        image = QImage(self.palette[self.data], self.data.shape[1], self.data.shape[0], QImage.Format_RGB32)
        self.pixmap.convertFromImage(image)

        self.update()

    @staticmethod
    def create_palette():
        palette = np.zeros((256,), dtype=np.uint32)
        for i in range(64):
            palette[i] = QColor(i * 4, 0, 0, 255).rgba()
            palette[i + 64] = QColor(255, i * 4, 0, 255).rgba()
            palette[i + 128] = QColor(255, 255, i * 4, 255).rgba()
            palette[i + 192] = QColor(255, 255, 255, 255).rgba()
        return palette


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = FlameWidget(640, 240)
    widget.show()

    sys.exit(app.exec_())
