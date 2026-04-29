"""Splash / welcome screen shown briefly before the main window opens."""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette


class SplashScreen(QDialog):
    """Centered splash window shown while the app loads."""

    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(440, 280)
        self._center()
        self._build_ui()

    def _center(self):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width()  - self.width())  // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main card
        card = QLabel()
        card.setFixedSize(440, 280)
        card.setStyleSheet(
            "QLabel {"
            "  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "    stop:0 #0D1F35, stop:1 #1A4A7A);"
            "  border-radius: 18px;"
            "}"
        )
        layout.addWidget(card)

        # Inner layout on top of card
        inner = QVBoxLayout(card)
        inner.setContentsMargins(40, 36, 40, 32)
        inner.setSpacing(0)
        inner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Caduceus symbol
        symbol = QLabel("⚕")
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setStyleSheet(
            "font-size: 42px; color: #38BDF8;"
            "background: transparent; margin-bottom: 6px;"
        )
        inner.addWidget(symbol)

        # App name
        name_lbl = QLabel("DentNest")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setFont(QFont("Ubuntu", 28, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color: white; background: transparent;")
        inner.addWidget(name_lbl)

        # Tagline
        tag_lbl = QLabel("Dental Practice Management")
        tag_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_lbl.setStyleSheet(
            "color: #94A3B8; font-size: 13px; background: transparent; margin-top: 4px;"
        )
        inner.addWidget(tag_lbl)

        inner.addStretch()

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(4)
        self._progress.setStyleSheet(
            "QProgressBar { background: #1E3A5F; border-radius: 2px; border: none; }"
            "QProgressBar::chunk { background: #38BDF8; border-radius: 2px; }"
        )
        inner.addWidget(self._progress)

        # Status label
        self._status = QLabel("Loading…")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(
            "color: #64748B; font-size: 11px; background: transparent; margin-top: 6px;"
        )
        inner.addWidget(self._status)

        # Animate progress in steps
        self._step = 0
        self._steps = [
            (20,  "Initialising database…"),
            (50,  "Loading patient records…"),
            (80,  "Preparing interface…"),
            (100, "Ready!"),
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(340)

    def _tick(self):
        if self._step < len(self._steps):
            val, msg = self._steps[self._step]
            self._progress.setValue(val)
            self._status.setText(msg)
            self._step += 1
        else:
            self._timer.stop()
            QTimer.singleShot(250, self._done)

    def _done(self):
        self.finished.emit()
        self.accept()
