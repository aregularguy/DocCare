"""
Interactive Dental Chart (Odontogram) widget for DentNest.

Displays a standard FDI tooth chart:
  Upper jaw:  11-18 (upper-right) | 21-28 (upper-left)
  Lower jaw:  41-48 (lower-right) | 31-38 (lower-left)

Click any tooth to pick its condition from a context menu.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTextEdit, QDialog, QDialogButtonBox,
    QComboBox, QGridLayout, QSizePolicy, QToolTip, QMessageBox
)
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics,
    QPainterPath, QLinearGradient, QRadialGradient, QTransform
)
from ...models.tooth_condition import TOOTH_CONDITIONS, FDI_UPPER, FDI_LOWER
from ...services.dental_chart_service import DentalChartService


# ── Colours ──────────────────────────────────────────────────────────────────
_BG = "#F4F7F8"
_PANEL_BG = "#FFFFFF"
_HEADER = "#1F4E5A"
_ACCENT = "#1F8A9E"

_ENAMEL_HEALTHY = "#FBF8F1"   # natural enamel white
_ROOT_IVORY     = "#E6D5B3"   # cementum / dentine ivory
_IMPLANT_METAL  = "#AEB9C2"   # titanium grey

# Conditions whose colour also tints the root (not just the crown)
_ROOT_TINT = {"decay", "extraction", "root_canal"}


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(
        int(a.red()   * (1 - t) + b.red()   * t),
        int(a.green() * (1 - t) + b.green() * t),
        int(a.blue()  * (1 - t) + b.blue()  * t),
    )


def _cylinder_gradient(color: QColor, half_w: float) -> QLinearGradient:
    """Horizontal gradient that makes a flat shape read as a rounded cylinder."""
    g = QLinearGradient(-half_w, 0.0, half_w, 0.0)
    g.setColorAt(0.00, color.darker(160))
    g.setColorAt(0.15, color.darker(112))
    g.setColorAt(0.36, color.lighter(108))
    g.setColorAt(0.55, color)
    g.setColorAt(0.82, color.darker(120))
    g.setColorAt(1.00, color.darker(165))
    return g


# ── Single Tooth Widget ───────────────────────────────────────────────────────

class ToothWidget(QWidget):
    """
    Draws one anatomical tooth (crown + roots) with 3D shading.

    Geometry is built in a canonical space: x centred on the tooth axis,
    y = 0 at the biting edge and increasing toward the root apex. The paint
    transform flips upper teeth so their roots point up, and applies a small
    arch lift/tilt so the row follows a natural smile curve.
    """

    clicked_signal = pyqtSignal(int)

    _TH        = 132   # widget height
    _LABEL_H   = 16    # FDI number strip
    _PAD       = 4     # side padding (room for tilt + shadow)
    _ARCH_LIFT = 10.0  # posterior teeth sit this much higher
    _MAX_TILT  = 4.0   # degrees of root fan at the third molar

    def __init__(self, tooth_number: int, jaw: str = "upper", parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.jaw = jaw
        self.condition = "healthy"
        self.notes = ""
        self._index = tooth_number % 10
        self._screen_right = tooth_number // 10 in (2, 3)
        self._hovered = False

        self._crown_w, self._crown_h, self._root_len = self._dims()
        self.setFixedSize(self._crown_w + 2 * self._PAD + 4, self._TH)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_geometry()
        self._update_tooltip()

        # Fix tooltip background so text is readable
        self.setStyleSheet(
            "QToolTip { color: #1E2B32; background-color: #FFFDE7;"
            " border: 1.5px solid #FFB300; border-radius: 6px;"
            " padding: 5px 8px; font-size: 12px; }"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def set_condition(self, condition: str, notes: str = ""):
        condition = condition if condition in TOOTH_CONDITIONS else "healthy"
        rebuild = (condition == "implant") != (self.condition == "implant")
        self.condition = condition
        self.notes = notes
        if rebuild:
            self._build_geometry()
        self._update_tooltip()
        self.update()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_tooltip(self):
        cfg = TOOTH_CONDITIONS[self.condition]
        tip = f"<b>Tooth {self.tooth_number}</b><br>{cfg['label']}"
        if self.notes:
            tip += f"<br><i>📝 {self.notes}</i>"
        self.setToolTip(tip)

    def _kind(self) -> str:
        i = self._index
        if i in (1, 2):
            return "incisor"
        if i == 3:
            return "canine"
        if i in (4, 5):
            return "premolar"
        return "molar"

    def _dims(self) -> tuple[int, int, int]:
        """(crown width, crown height, root length) per tooth position."""
        upper = self.jaw == "upper"
        table = {
            1: (40, 38, 50) if upper else (30, 32, 44),
            2: (34, 34, 46) if upper else (32, 32, 46),
            3: (38, 36, 58) if upper else (36, 36, 54),
            4: (38, 32, 46) if upper else (36, 32, 48),
            5: (36, 32, 46) if upper else (36, 32, 48),
            6: (52, 30, 40) if upper else (54, 30, 42),
            7: (50, 30, 38) if upper else (50, 30, 40),
            8: (46, 28, 32) if upper else (46, 28, 34),
        }
        return table.get(self._index, (38, 32, 44))

    def _label_rect(self) -> QRect:
        if self.jaw == "upper":
            return QRect(0, self._TH - self._LABEL_H, self.width(), self._LABEL_H)
        return QRect(0, 0, self.width(), self._LABEL_H)

    def _transform(self) -> QTransform:
        """Canonical tooth space → widget pixels (flip, arch lift, tilt)."""
        t = (max(1, min(8, self._index)) - 1) / 7.0
        lift = self._ARCH_LIFT * t * t
        tilt = self._MAX_TILT * t * (-1.0 if self._screen_right else 1.0)
        tr = QTransform()
        if self.jaw == "upper":
            tr.translate(self.width() / 2.0, self._TH - self._LABEL_H - 4 - lift)
            tr.rotate(tilt)
            tr.scale(1.0, -1.0)
        else:
            tr.translate(self.width() / 2.0, self._LABEL_H + 4 + self._ARCH_LIFT - lift)
            tr.rotate(tilt)
        return tr

    # ── Anatomical geometry ───────────────────────────────────────────────────

    def _root(self, xl: float, xr: float, ax: float, y_top: float, ay: float) -> QPainterPath:
        """Tapered, slightly curved root from a neck span down to a pointed apex."""
        d = ay - y_top
        p = QPainterPath()
        p.moveTo(xl, y_top)
        p.lineTo(xr, y_top)
        p.cubicTo(xr, y_top + d * 0.40,
                  ax + (xr - ax) * 0.50, y_top + d * 0.85,
                  ax + 1.3, ay - 1.2)
        p.quadTo(ax, ay + 0.8, ax - 1.3, ay - 1.2)
        p.cubicTo(ax + (xl - ax) * 0.50, y_top + d * 0.85,
                  xl, y_top + d * 0.40,
                  xl, y_top)
        p.closeSubpath()
        self._apices.append(QPointF(ax, ay))
        return p

    def _build_geometry(self):
        W, Hc, Lr = float(self._crown_w), float(self._crown_h), float(self._root_len)
        w = W / 2.0
        kind = self._kind()
        upper = self.jaw == "upper"
        distal = 1.0 if self._screen_right else -1.0   # roots curve slightly distally
        implant = self.condition == "implant"

        self._apices: list[QPointF] = []
        self._grooves: list[QPainterPath] = []
        self._threads: list[tuple[QPointF, QPointF]] = []
        self._back_path: QPainterPath | None = None
        root_top = Hc - 4

        crown = QPainterPath()
        roots: list[QPainterPath] = []

        if kind == "incisor":
            neck = w * 0.62
            crown.moveTo(-w + 3, 0.6)
            crown.quadTo(0, -0.8, w - 3, 0.6)
            crown.quadTo(w, 1, w, 5)
            crown.cubicTo(w, Hc * 0.5, w * 0.86, Hc * 0.82, neck, Hc)
            crown.lineTo(-neck, Hc)
            crown.cubicTo(-w * 0.86, Hc * 0.82, -w, Hc * 0.5, -w, 5)
            crown.quadTo(-w, 1, -w + 3, 0.6)
            if not implant:
                roots.append(self._root(-neck, neck, distal * 2.5, root_top, Hc + Lr))
            for gx in (-w * 0.33, w * 0.33):
                g = QPainterPath()
                g.moveTo(gx, 4)
                g.quadTo(gx * 0.9, Hc * 0.35, gx * 0.8, Hc * 0.55)
                self._grooves.append(g)

        elif kind == "canine":
            neck = w * 0.60
            crown.moveTo(-1.5, 0.4)
            crown.quadTo(0, -0.6, 1.5, 0.4)
            crown.cubicTo(w * 0.35, Hc * 0.04, w * 0.75, Hc * 0.16, w * 0.95, Hc * 0.32)
            crown.cubicTo(w * 1.05, Hc * 0.55, w * 0.85, Hc * 0.85, neck, Hc)
            crown.lineTo(-neck, Hc)
            crown.cubicTo(-w * 0.85, Hc * 0.85, -w * 1.05, Hc * 0.55, -w * 0.95, Hc * 0.32)
            crown.cubicTo(-w * 0.75, Hc * 0.16, -w * 0.35, Hc * 0.04, -1.5, 0.4)
            if not implant:
                roots.append(self._root(-neck, neck, distal * 3.0, root_top, Hc + Lr))
            for gx in (-w * 0.42, w * 0.42):
                g = QPainterPath()
                g.moveTo(gx, Hc * 0.28)
                g.quadTo(gx * 0.85, Hc * 0.5, gx * 0.7, Hc * 0.68)
                self._grooves.append(g)

        elif kind == "premolar":
            neck = w * 0.60
            crown.moveTo(-1.5, 0.3)
            crown.quadTo(0, -0.5, 1.5, 0.3)
            crown.cubicTo(w * 0.45, Hc * 0.05, w * 0.85, Hc * 0.14, w * 0.97, Hc * 0.30)
            crown.cubicTo(w * 1.05, Hc * 0.55, w * 0.85, Hc * 0.85, neck, Hc)
            crown.lineTo(-neck, Hc)
            crown.cubicTo(-w * 0.85, Hc * 0.85, -w * 1.05, Hc * 0.55, -w * 0.97, Hc * 0.30)
            crown.cubicTo(-w * 0.85, Hc * 0.14, -w * 0.45, Hc * 0.05, -1.5, 0.3)
            if not implant:
                if upper and self._index == 4:
                    # Upper first premolar: bifurcated root
                    ay = Hc + Lr * 0.94
                    roots.append(self._root(-neck, neck * 0.05, -w * 0.30 + distal * 2, root_top, ay))
                    roots.append(self._root(-neck * 0.05, neck, w * 0.30 + distal * 2, root_top, ay))
                else:
                    roots.append(self._root(-neck, neck, distal * 2.5, root_top, Hc + Lr))
            for gx in (-w * 0.45, w * 0.45):
                g = QPainterPath()
                g.moveTo(gx, Hc * 0.24)
                g.quadTo(gx * 0.85, Hc * 0.45, gx * 0.72, Hc * 0.62)
                self._grooves.append(g)

        else:  # molar
            neck = w * 0.80
            c = Hc * 0.16
            crown.moveTo(-w, Hc * 0.32)
            crown.cubicTo(-w, Hc * 0.05, -w * 0.8, 0, -w * 0.52, 0)
            crown.cubicTo(-w * 0.25, 0, -w * 0.1, c * 0.6, 0, c)
            crown.cubicTo(w * 0.1, c * 0.6, w * 0.25, 0, w * 0.52, 0)
            crown.cubicTo(w * 0.8, 0, w, Hc * 0.05, w, Hc * 0.32)
            crown.cubicTo(w * 1.03, Hc * 0.62, w * 0.92, Hc * 0.9, neck, Hc)
            crown.lineTo(-neck, Hc)
            crown.cubicTo(-w * 0.92, Hc * 0.9, -w * 1.03, Hc * 0.62, -w, Hc * 0.32)
            if not implant:
                spread = 0.30 if self._index == 8 else 0.58
                # Root trunk so the furcation starts below the neck
                trunk = QPainterPath()
                trunk.moveTo(-neck, root_top)
                trunk.lineTo(neck, root_top)
                trunk.lineTo(neck * 0.92, Hc + Lr * 0.22)
                trunk.quadTo(0, Hc + Lr * 0.08, -neck * 0.92, Hc + Lr * 0.22)
                trunk.closeSubpath()
                roots.append(trunk)
                roots.append(self._root(-neck, -neck * 0.10, -w * spread + distal * 3,
                                        root_top, Hc + Lr))
                roots.append(self._root(neck * 0.10, neck, w * spread + distal * 3,
                                        root_top, Hc + Lr * 0.94))
                if upper:
                    # Palatal root, seen behind the two buccal roots
                    self._back_path = self._root(-neck * 0.42, neck * 0.42, distal * 1.5,
                                                 root_top, Hc + Lr * 1.04)
            g = QPainterPath()   # central groove between the cusps
            g.moveTo(0, c + 1)
            g.quadTo(0.6, Hc * 0.45, 0, Hc * 0.62)
            self._grooves.append(g)
            for gx in (-w * 0.62, w * 0.62):
                g = QPainterPath()
                g.moveTo(gx, Hc * 0.30)
                g.quadTo(gx * 0.9, Hc * 0.55, gx * 0.8, Hc * 0.72)
                self._grooves.append(g)

        if implant:
            neck_w = min(w * 0.55, 11.0)
            top, bot = root_top, Hc + Lr * 0.85
            bw = neck_w * 0.65
            body = QPainterPath()
            body.moveTo(-neck_w, top)
            body.lineTo(neck_w, top)
            body.lineTo(bw, bot - 4)
            body.quadTo(bw, bot, 0, bot)
            body.quadTo(-bw, bot, -bw, bot - 4)
            body.closeSubpath()
            roots.append(body)
            self._apices.append(QPointF(0, bot))
            y = top + 6.0
            while y < bot - 5:
                frac = (y - top) / (bot - top)
                hw = neck_w + (bw - neck_w) * frac
                self._threads.append((QPointF(-hw, y), QPointF(hw, y + 2.0)))
                y += 4.5

        crown.closeSubpath()
        tooth = QPainterPath(crown)
        for r in roots:
            tooth = tooth.united(r)
        self._tooth_path = tooth

        # Enamel boundary (CEJ): dips toward the root in the middle
        big = W * 2
        cej = QPainterPath()
        cej.moveTo(w, Hc - 3)
        cej.cubicTo(w * 0.35, Hc + 3, -w * 0.35, Hc + 3, -w, Hc - 3)
        self._cej_line = cej

        clip = QPainterPath()
        clip.moveTo(-big, -20)
        clip.lineTo(big, -20)
        clip.lineTo(big, Hc - 3)
        clip.lineTo(w, Hc - 3)
        clip.cubicTo(w * 0.35, Hc + 3, -w * 0.35, Hc + 3, -w, Hc - 3)
        clip.lineTo(-big, Hc - 3)
        clip.closeSubpath()
        self._crown_region = tooth.intersected(clip)
        self._root_region = tooth.subtracted(clip)

    # ── Events ────────────────────────────────────────────────────────────────

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked_signal.emit(self.tooth_number)

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cfg = TOOTH_CONDITIONS[self.condition]
        border_color = QColor(cfg["border"])
        W, Hc = float(self._crown_w), float(self._crown_h)
        w = W / 2.0
        length = Hc + self._root_len
        tooth = self._tooth_path
        T = self._transform()

        # ── 1. Soft drop shadow ──────────────────────────────────────────────
        shadow_off = 3.0 if self._hovered else 2.0
        painter.setTransform(T * QTransform.fromTranslate(1.5, shadow_off))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(40, 40, 70, 60 if self._hovered else 32))
        painter.drawPath(tooth)
        painter.setTransform(T)

        # ── Missing: ghost outline only ──────────────────────────────────────
        if self.condition == "missing":
            painter.setBrush(QColor(0, 0, 0, 10))
            painter.setPen(QPen(QColor("#A9B6BC"), 1.4, Qt.PenStyle.DashLine))
            painter.drawPath(tooth)
            painter.setPen(QPen(QColor("#9E9E9E"), 2.0))
            m = w * 0.55
            painter.drawLine(QPointF(-m, Hc * 0.15), QPointF(m, Hc * 0.95))
            painter.drawLine(QPointF(m, Hc * 0.15), QPointF(-m, Hc * 0.95))
            self._draw_label(painter, cfg)
            return

        enamel = QColor(_ENAMEL_HEALTHY) if self.condition == "healthy" else QColor(cfg["color"])
        root_col = QColor(_ROOT_IVORY)
        if self.condition in _ROOT_TINT:
            root_col = _mix(root_col, QColor(cfg["color"]), 0.30)
        outline_w = 2.0 if self._hovered else 1.3
        outline = QPen(border_color.darker(115) if self._hovered else border_color, outline_w)

        # ── 2. Palatal root (behind) ─────────────────────────────────────────
        if self._back_path is not None:
            painter.setPen(QPen(border_color.darker(110), 1.0))
            painter.setBrush(_cylinder_gradient(root_col.darker(118), w * 0.5))
            painter.drawPath(self._back_path)

        # ── 3. Root / implant body ───────────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        if self.condition == "implant":
            painter.setBrush(_cylinder_gradient(QColor(_IMPLANT_METAL), w * 0.6))
        else:
            painter.setBrush(_cylinder_gradient(root_col, w))
        painter.drawPath(self._root_region)

        painter.save()
        painter.setClipPath(self._root_region)
        if self.condition == "implant":
            painter.setPen(QPen(QColor(60, 70, 80, 150), 1.1))
            for a, b in self._threads:
                painter.drawLine(a, b)
            painter.setPen(QPen(QColor(255, 255, 255, 140), 0.8))
            for a, b in self._threads:
                painter.drawLine(a + QPointF(0, 1.4), b + QPointF(0, 1.4))
        else:
            # Ambient occlusion: roots darken toward the apex (inside the bone)
            ao = QLinearGradient(0.0, Hc, 0.0, length)
            ao.setColorAt(0.0, QColor(90, 60, 30, 0))
            ao.setColorAt(1.0, QColor(90, 60, 30, 85))
            painter.fillRect(QRect(int(-W), int(Hc - 4), int(W * 2), int(length)), ao)
            # Narrow sheen running down the root
            sheen = QLinearGradient(-w * 0.45, 0.0, -w * 0.05, 0.0)
            sheen.setColorAt(0.0, QColor(255, 255, 255, 0))
            sheen.setColorAt(0.5, QColor(255, 255, 255, 70))
            sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.fillRect(QRect(int(-W), int(Hc - 4), int(W * 2), int(length)), sheen)
        painter.restore()

        # ── 4. Crown (enamel) ────────────────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_cylinder_gradient(enamel, w))
        painter.drawPath(self._crown_region)

        painter.save()
        painter.setClipPath(self._crown_region)
        # Translucent biting edge → warmer neck
        depth = QLinearGradient(0.0, 0.0, 0.0, Hc)
        depth.setColorAt(0.00, QColor(120, 140, 170, 45))
        depth.setColorAt(0.30, QColor(120, 140, 170, 0))
        depth.setColorAt(0.75, QColor(160, 120, 60, 0))
        depth.setColorAt(1.00, QColor(160, 120, 60, 55))
        painter.fillRect(QRect(int(-W), -4, int(W * 2), int(Hc + 8)), depth)

        # Developmental grooves / cusp ridges
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(110, 85, 50, 60), 1.1))
        for g in self._grooves:
            painter.drawPath(g)
        painter.setPen(QPen(QColor(255, 255, 255, 90), 0.9))
        for g in self._grooves:
            painter.drawPath(g.translated(1.2, 0))

        if self.condition == "decay":
            spot = QRadialGradient(w * 0.18, Hc * 0.32, W * 0.16)
            spot.setColorAt(0.0, QColor(70, 35, 20, 220))
            spot.setColorAt(0.6, QColor(110, 50, 30, 150))
            spot.setColorAt(1.0, QColor(110, 50, 30, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(spot)
            painter.drawEllipse(QPointF(w * 0.18, Hc * 0.32), W * 0.16, W * 0.16)

        # Specular highlight (light from the upper-left)
        painter.setPen(Qt.PenStyle.NoPen)
        shine = QRadialGradient(-w * 0.35, Hc * 0.38, w * 0.55)
        shine.setColorAt(0.0, QColor(255, 255, 255, 170))
        shine.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(shine)
        painter.drawEllipse(QPointF(-w * 0.35, Hc * 0.38), w * 0.55, Hc * 0.45)
        painter.setBrush(QColor(255, 255, 255, 190))
        painter.drawEllipse(QPointF(-w * 0.42, Hc * 0.30), 1.8, Hc * 0.14)
        painter.restore()

        # ── 5. Enamel–root junction line ─────────────────────────────────────
        painter.save()
        painter.setClipPath(tooth)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(140, 105, 60, 110), 1.0))
        painter.drawPath(self._cej_line)

        # ── 6. Root canal: filled canals to each apex ────────────────────────
        if self.condition == "root_canal":
            painter.setPen(QPen(QColor("#C94A46"), 2.0, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap))
            pulp = QPointF(0, Hc * 0.55)
            for apex in self._apices:
                tip = pulp + (apex - pulp) * 0.93
                canal = QPainterPath(pulp)
                canal.quadTo(QPointF(tip.x() * 0.4, (pulp.y() + tip.y()) / 2), tip)
                painter.drawPath(canal)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#C94A46"))
            painter.drawEllipse(pulp, 3.5, 4.5)
        painter.restore()

        # ── 7. Outline + hover glow ──────────────────────────────────────────
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._hovered:
            painter.setPen(QPen(QColor(0, 122, 255, 80), 5.0))
            painter.drawPath(tooth)
        painter.setPen(outline)
        painter.drawPath(tooth)

        if self.condition == "extraction":
            painter.setPen(QPen(QColor("#C94A46"), 2.0))
            painter.drawLine(QPointF(-w * 0.7, Hc + 6), QPointF(w * 0.7, length * 0.8))
            painter.drawLine(QPointF(w * 0.7, Hc + 6), QPointF(-w * 0.7, length * 0.8))

        self._draw_label(painter, cfg)

    def _draw_label(self, painter: QPainter, cfg: dict):
        painter.resetTransform()
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        num_color = QColor(cfg["text"]) if self.condition != "healthy" else QColor("#2E3D44")
        painter.setPen(num_color)
        painter.drawText(
            self._label_rect(),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            str(self.tooth_number)
        )
        painter.end()


# ── Condition Picker Dialog ───────────────────────────────────────────────────

class ToothConditionDialog(QDialog):
    """A dialog to pick a condition and optional notes for one tooth."""

    def __init__(self, tooth_number: int, current_condition: str,
                 current_notes: str, parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.setWindowTitle(f"Tooth {tooth_number}")
        self.setMinimumWidth(360)
        self.setStyleSheet("""
            QDialog { background: #F4F7F8; }
            QLabel { font-size: 13px; color: #1E2B32; }
            QComboBox { border: 1.5px solid #CFDADE; border-radius: 8px;
                        padding: 6px 12px; font-size: 13px; background: white; }
            QTextEdit { border: 1.5px solid #CFDADE; border-radius: 8px;
                        padding: 6px; font-size: 13px; background: white; }
            QPushButton { border-radius: 8px; padding: 8px 20px; font-weight: 700; font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 20)

        t = QLabel(f"🦷 Set Condition — Tooth {tooth_number}")
        t.setStyleSheet("font-size: 15px; font-weight: 700; color: #1F4E5A;")
        layout.addWidget(t)

        layout.addWidget(QLabel("Condition:"))
        self.combo = QComboBox()
        for key, meta in TOOTH_CONDITIONS.items():
            self.combo.addItem(meta["label"], key)
            idx = self.combo.count() - 1
            self.combo.setItemData(idx, QColor(meta["color"]),
                                   Qt.ItemDataRole.BackgroundRole)
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == current_condition:
                self.combo.setCurrentIndex(i)
                break
        layout.addWidget(self.combo)

        layout.addWidget(QLabel("Notes (optional):"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("e.g. 'mesial decay', 'sensitivity reported'…")
        self.notes_edit.setFixedHeight(72)
        self.notes_edit.setText(current_notes)
        layout.addWidget(self.notes_edit)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        ok_btn = btn_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText("✅  Save")
        ok_btn.setStyleSheet("background:#1F8A9E; color:white; border:none;")
        cancel_btn = btn_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet("background:#DDE5E8; color:#1E2B32; border:none;")
        layout.addWidget(btn_box)

    def get_result(self) -> tuple[str, str]:
        return self.combo.currentData(), self.notes_edit.toPlainText().strip()


# ── Full Dental Chart Widget ──────────────────────────────────────────────────

class DentalChartWidget(QWidget):
    """
    Full odontogram widget to embed as a tab in PatientDetailsWidget.
    Shows the FDI two-digit numbering system chart (upper + lower jaw).
    """

    def __init__(self, patient_id: int, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.chart_service = DentalChartService()
        self._tooth_widgets: dict[int, ToothWidget] = {}
        self._build_ui()
        self._load_chart()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        inner.setStyleSheet(f"background:{_BG};")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(20)

        # Title strip
        title_bar = QHBoxLayout()
        title = QLabel("🦷  Dental Chart  (FDI Numbering)")
        title.setStyleSheet(f"font-size:17px; font-weight:800; color:{_HEADER};")
        title_bar.addWidget(title)
        title_bar.addStretch()

        reset_btn = QPushButton("🔄  Reset All")
        reset_btn.setStyleSheet(
            "QPushButton { background:#FBEBEA; color:#D0534F; border:1.5px solid #D0534F;"
            " border-radius:8px; padding:6px 14px; font-weight:700; font-size:12px; }"
            "QPushButton:hover { background:#D0534F; color:white; }"
        )
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_all)
        title_bar.addWidget(reset_btn)
        layout.addLayout(title_bar)

        # Legend
        layout.addWidget(self._build_legend())

        # Chart card
        chart_card = QFrame()
        chart_card.setStyleSheet(
            f"QFrame {{ background:{_PANEL_BG}; border-radius:16px;"
            f" border:1px solid #DDE5E8; }}"
        )
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(24, 24, 24, 24)
        chart_layout.setSpacing(8)

        upper_lbl = QLabel("UPPER JAW")
        upper_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_lbl.setStyleSheet(
            "font-size:10px; font-weight:700; color:#5B6B73; letter-spacing:2px; background:transparent;"
        )
        chart_layout.addWidget(upper_lbl)

        chart_layout.addWidget(self._build_jaw_row(
            list(reversed(range(11, 19))),
            list(range(21, 29)),
            jaw="upper"
        ))

        chart_layout.addWidget(self._midline())

        chart_layout.addWidget(self._build_jaw_row(
            list(reversed(range(41, 49))),
            list(range(31, 39)),
            jaw="lower"
        ))

        lower_lbl = QLabel("LOWER JAW")
        lower_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lower_lbl.setStyleSheet(
            "font-size:10px; font-weight:700; color:#5B6B73; letter-spacing:2px; background:transparent;"
        )
        chart_layout.addWidget(lower_lbl)

        layout.addWidget(chart_card)
        layout.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll)

    def _build_jaw_row(self, right_teeth: list, left_teeth: list, jaw: str) -> QWidget:
        row_w = QWidget()
        row_w.setStyleSheet("background:transparent;")
        row = QHBoxLayout(row_w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addStretch()

        for tn in right_teeth:
            tw = ToothWidget(tn, jaw=jaw)
            tw.clicked_signal.connect(self._on_tooth_clicked)
            self._tooth_widgets[tn] = tw
            row.addWidget(tw)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedWidth(2)
        div.setStyleSheet("background:#C5D2D7; border:none;")
        row.addWidget(div)

        for tn in left_teeth:
            tw = ToothWidget(tn, jaw=jaw)
            tw.clicked_signal.connect(self._on_tooth_clicked)
            self._tooth_widgets[tn] = tw
            row.addWidget(tw)

        row.addStretch()
        return row_w

    def _midline(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(20)
        w.setStyleSheet("background:transparent;")
        l = QHBoxLayout(w)
        l.setContentsMargins(40, 0, 40, 0)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 transparent, stop:0.2 #C5D2D7,"
            "stop:0.8 #C5D2D7, stop:1 transparent); border:none;"
        )
        l.addWidget(sep)
        return w

    def _build_legend(self) -> QWidget:
        legend_frame = QFrame()
        legend_frame.setStyleSheet(
            "QFrame { background:#E3F3F6; border-radius:10px; border:1px solid #B9DCE4; }"
        )
        fl = QHBoxLayout(legend_frame)
        fl.setContentsMargins(16, 10, 16, 10)
        fl.setSpacing(6)
        fl.addWidget(QLabel("Legend:"))
        for key, meta in TOOTH_CONDITIONS.items():
            pill = QLabel(meta["label"])
            pill.setStyleSheet(
                f"background:{meta['color']}; color:{meta['text']};"
                f" border:1.5px solid {meta['border']}; border-radius:8px;"
                f" padding:2px 8px; font-size:11px; font-weight:600;"
            )
            fl.addWidget(pill)
        fl.addStretch()
        return legend_frame

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load_chart(self):
        chart = self.chart_service.get_patient_chart(self.patient_id)
        for tooth_num, tc in chart.items():
            if tooth_num in self._tooth_widgets:
                self._tooth_widgets[tooth_num].set_condition(tc.condition, tc.notes)

    def refresh(self):
        self._load_chart()

    # ── Interaction ───────────────────────────────────────────────────────────

    def _on_tooth_clicked(self, tooth_number: int):
        tw = self._tooth_widgets.get(tooth_number)
        if not tw:
            return
        dlg = ToothConditionDialog(tooth_number, tw.condition, tw.notes, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            condition, notes = dlg.get_result()
            ok = self.chart_service.save_tooth(self.patient_id, tooth_number, condition, notes)
            if ok:
                tw.set_condition(condition, notes)
            else:
                QMessageBox.warning(self, "Error", f"Could not save tooth {tooth_number}.")

    def _reset_all(self):
        reply = QMessageBox.question(
            self, "Reset All",
            "This will clear ALL tooth conditions for this patient.\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.chart_service.db.execute(
                "DELETE FROM tooth_conditions WHERE patient_id=?",
                (self.patient_id,)
            )
        except Exception as ex:
            QMessageBox.warning(self, "Error", str(ex))
            return
        for tw in self._tooth_widgets.values():
            tw.set_condition("healthy", "")
