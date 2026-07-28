from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QColor
from PySide6.QtCore import Qt
from ui.theme_manager import ThemeManager

class CurvedLogo(QWidget):
    def __init__(self, text="CINEMAPY"):
        super().__init__()
        self.text = text
        self.setMinimumSize(220, 60)
        self.setMaximumHeight(80)
        self.curve_strength = -0.30
        self.y_offset_strength = -0.20
        self.logo_font = QFont("Arial Black", 22)
        self.logo_font.setWeight(QFont.Black)
        self.logo_font.setLetterSpacing(QFont.AbsoluteSpacing, 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        fm = QFontMetrics(self.logo_font)
        char_widths = []
        total_width = 0
        for char in self.text:
            w = fm.horizontalAdvance(char)
            char_widths.append(w)
            total_width += w
            
        start_x = (self.width() - total_width) / 2
        current_x = start_x
        center_index = (len(self.text) - 1) / 2.0
        painter.setFont(self.logo_font)
        primary_color_hex = ThemeManager.get_color("primary")
        painter.setPen(QColor(primary_color_hex))
        center_y = self.height() / 2.0
        
        for i, char in enumerate(self.text):
            dist_from_center = (i - center_index) / center_index if center_index > 0 else 0
            parabola = 1.0 - (dist_from_center * dist_from_center)
            scale_y = 1.4 + (parabola * self.curve_strength)
            y_shift = parabola * self.y_offset_strength * 20.0
            painter.save()
            painter.translate(current_x, center_y + y_shift)
            painter.scale(1.0, scale_y)
            text_y = fm.capHeight() / 2.0
            painter.drawText(0, text_y, char)
            painter.restore()
            current_x += char_widths[i]
