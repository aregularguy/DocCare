"""Due Payments page — dedicated view of all outstanding patient balances."""
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QScrollArea,
    QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from ...services.treatment_service import TreatmentService
from .payment_list import RecordPaymentDialog

ROWS_PER_PAGE = 25


class DuePaymentsWidget(QWidget):
    """Full-featured due payments tracking page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.treatment_service = TreatmentService()
        self._all_rows: list[dict] = []
        self._filtered_rows: list[dict] = []
        self._current_page = 0
        self.init_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(32, 28, 32, 32)
        self._layout.setSpacing(20)
        scroll.setWidget(container)

        # ── Hero banner ──
        banner = QFrame()
        banner.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            " stop:0 #7A2E0F, stop:0.6 #B8450D, stop:1 #D4680A);"
            " border-radius: 14px; }"
        )
        banner.setFixedHeight(110)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 0, 28, 0)

        banner_text = QVBoxLayout()
        b_title = QLabel("Due Payments")
        b_title.setStyleSheet(
            "color:white; font-size:24px; font-weight:700; background:transparent;"
        )
        b_subtitle = QLabel("Track outstanding patient balances")
        b_subtitle.setStyleSheet(
            "color:#E8C4A8; font-size:13px; background:transparent;"
        )
        banner_text.addStretch()
        banner_text.addWidget(b_title)
        banner_text.addWidget(b_subtitle)
        banner_text.addStretch()
        banner_layout.addLayout(banner_text)
        banner_layout.addStretch()

        self.total_badge = QLabel("0 due")
        self.total_badge.setStyleSheet(
            "color:white; font-size:13px; font-weight:600;"
            " background:rgba(255,255,255,0.18); border-radius:14px;"
            " padding:6px 18px;"
        )
        banner_layout.addWidget(self.total_badge)

        self._layout.addWidget(banner)

        # ── Summary cards ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_outstanding = self._make_summary_card(
            "Total Outstanding", "Rs.0", "#C98A2E", "Rs"
        )
        self.card_patients = self._make_summary_card(
            "Patients with Dues", "0", "#1F8A9E", "P"
        )
        self.card_treatments = self._make_summary_card(
            "Treatments with Dues", "0", "#D0534F", "T"
        )
        cards_row.addWidget(self.card_outstanding)
        cards_row.addWidget(self.card_patients)
        cards_row.addWidget(self.card_treatments)
        self._layout.addLayout(cards_row)

        # ── Search row ──
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by patient name or treatment…")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_row.addWidget(self.search_input, 1)

        self._layout.addLayout(filter_row)

        # ── Due payments table ──
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_frame.setStyleSheet(
            "QFrame#card { background:#FFFFFF; border:1px solid #DDE5E8;"
            " border-radius:12px; padding:0px; }"
        )
        tbl_layout = QVBoxLayout(table_frame)
        tbl_layout.setContentsMargins(0, 0, 0, 0)
        tbl_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Patient", "Treatment", "Total Cost", "Paid", "Due Amount", ""]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setFrameShape(QFrame.Shape.NoFrame)
        # Disable table's own scrollbar — the outer QScrollArea handles scrolling
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Style the header
        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "  background:#F8F8FA; color:#6B7280; font-weight:600;"
            "  font-size:11px; border:none; padding:10px 12px;"
            "  border-bottom:2px solid #DDE5E8;"
            "}"
        )

        tbl_layout.addWidget(self.table)
        self._layout.addWidget(table_frame)

        # ── Pagination bar ──
        self.pagination_frame = QFrame()
        self.pagination_frame.setStyleSheet(
            "QFrame { background:transparent; }"
        )
        pag_layout = QHBoxLayout(self.pagination_frame)
        pag_layout.setContentsMargins(0, 4, 0, 0)
        pag_layout.setSpacing(12)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setFixedSize(100, 36)
        self.prev_btn.setStyleSheet(
            "QPushButton {"
            "  background:#EEF3F4; color:#1E2B32; border:1px solid #DDE5E8;"
            "  border-radius:8px; font-weight:600; font-size:12px;"
            "}"
            "QPushButton:hover { background:#DDE5E8; }"
            "QPushButton:disabled { color:#A9B6BC; background:#F4F7F8; border-color:#EEF3F4; }"
        )
        self.prev_btn.clicked.connect(self._prev_page)
        pag_layout.addWidget(self.prev_btn)

        pag_layout.addStretch()

        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet(
            "color:#5B6B73; font-size:12px; font-weight:500;"
        )
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pag_layout.addWidget(self.page_label)

        pag_layout.addStretch()

        self.next_btn = QPushButton("Next")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setFixedSize(100, 36)
        self.next_btn.setStyleSheet(
            "QPushButton {"
            "  background:#1F8A9E; color:white; border:none;"
            "  border-radius:8px; font-weight:600; font-size:12px;"
            "}"
            "QPushButton:hover { background:#16707F; }"
            "QPushButton:disabled { background:#B9DCE4; }"
        )
        self.next_btn.clicked.connect(self._next_page)
        pag_layout.addWidget(self.next_btn)

        self._layout.addWidget(self.pagination_frame)

        # ── Empty state ──
        self.empty_lbl = QLabel("No outstanding payments. All treatments are fully paid!")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "color:#5B6B73; font-size:15px; padding:40px;"
        )
        self.empty_lbl.hide()
        self._layout.addWidget(self.empty_lbl)

        self.refresh_data()

    # ── Summary card factory ──────────────────────────────────────────────────

    def _make_summary_card(
        self, label: str, value: str, accent: str, icon: str
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("metric_card")
        card.setStyleSheet(
            f"QFrame#metric_card {{ background:#FFFFFF; border:1px solid #DDE5E8;"
            f" border-left: 4px solid {accent}; border-radius:10px; }}"
        )
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        card.setFixedHeight(110)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(4)

        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size:11px; font-weight:bold; color:#fff;"
            f" background:{accent}; border-radius:10px; padding:2px 7px;"
        )
        icon_lbl.setMaximumWidth(50)
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        cl.addLayout(top_row)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("metric_value")
        val_lbl.setFont(QFont("Noto Sans", 18, QFont.Weight.Bold))
        val_lbl.setStyleSheet(
            f"color:{accent}; background:transparent;"
        )
        val_lbl.setWordWrap(False)
        val_lbl.setMinimumWidth(80)
        cl.addWidget(val_lbl)

        lbl_lbl = QLabel(label)
        lbl_lbl.setObjectName("metric_label")
        lbl_lbl.setStyleSheet(
            "font-size:11px; color:#5B6B73; background:transparent;"
        )
        cl.addWidget(lbl_lbl)

        card._value_label = val_lbl
        return card

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh_data(self):
        self._load_data()
        self._update_summary()
        self._current_page = 0
        self._apply_filter()

    def _load_data(self):
        self._all_rows = []
        try:
            pending = self.treatment_service.get_pending_with_patient_names()
            for item in pending:
                t = item['treatment']
                self._all_rows.append({
                    'patient_name': item['patient_name'],
                    'patient_mobile': item['patient_mobile'],
                    'treatment_name': t.treatment_type_name or '—',
                    'total_cost': t.total_cost,
                    'amount_paid': t.amount_paid,
                    'due_amount': t.pending_amount,
                    'treatment_id': t.id,
                    'patient_id': item['patient_id'],
                })
        except Exception:
            pass

        # Sort by due amount descending (highest dues first)
        self._all_rows.sort(key=lambda r: r['due_amount'], reverse=True)

    def _update_summary(self):
        total_outstanding = sum(r['due_amount'] for r in self._all_rows)
        unique_patients = len({r['patient_id'] for r in self._all_rows})
        num_treatments = len(self._all_rows)

        self.card_outstanding._value_label.setText(f"Rs.{total_outstanding:,.0f}")
        self.card_patients._value_label.setText(str(unique_patients))
        self.card_treatments._value_label.setText(str(num_treatments))
        self.total_badge.setText(
            f"{num_treatments} due" if num_treatments else "All clear"
        )

    # ── Filtering ─────────────────────────────────────────────────────────────

    def _on_search_changed(self):
        self._current_page = 0
        self._apply_filter()

    def _apply_filter(self):
        search_text = self.search_input.text().strip().lower()

        self._filtered_rows = []
        for row in self._all_rows:
            if search_text:
                haystack = (
                    row['patient_name'].lower()
                    + row['treatment_name'].lower()
                )
                if search_text not in haystack:
                    continue
            self._filtered_rows.append(row)

        self._render_page()

    # ── Pagination ────────────────────────────────────────────────────────────

    def _total_pages(self) -> int:
        return max(1, math.ceil(len(self._filtered_rows) / ROWS_PER_PAGE))

    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def _next_page(self):
        if self._current_page < self._total_pages() - 1:
            self._current_page += 1
            self._render_page()

    def _render_page(self):
        total = len(self._filtered_rows)
        total_pages = self._total_pages()

        if self._current_page >= total_pages:
            self._current_page = max(0, total_pages - 1)

        start = self._current_page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        page_rows = self._filtered_rows[start:end]

        self._populate_table(page_rows)

        # Update pagination controls
        self.prev_btn.setEnabled(self._current_page > 0)
        self.next_btn.setEnabled(self._current_page < total_pages - 1)
        self.page_label.setText(
            f"Page {self._current_page + 1} of {total_pages}  ({total} total)"
        )

        # Hide pagination if only 1 page
        self.pagination_frame.setVisible(total_pages > 1)

    def _populate_table(self, rows: list[dict]):
        self.table.setRowCount(0)

        if not rows:
            self.table.hide()
            self.empty_lbl.show()
            self.pagination_frame.hide()
            return

        self.table.show()
        self.empty_lbl.hide()

        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)

            # Patient name (bold, dark blue)
            name_item = QTableWidgetItem(row_data['patient_name'])
            name_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            name_item.setForeground(QBrush(QColor("#1F4E5A")))
            self.table.setItem(row_idx, 0, name_item)

            # Treatment
            treat_item = QTableWidgetItem(row_data['treatment_name'])
            treat_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row_idx, 1, treat_item)

            # Total cost (right-aligned)
            cost_item = QTableWidgetItem(f"Rs.{row_data['total_cost']:,.0f}")
            cost_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            cost_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row_idx, 2, cost_item)

            # Paid (right-aligned, green)
            paid_item = QTableWidgetItem(f"Rs.{row_data['amount_paid']:,.0f}")
            paid_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            paid_item.setFont(QFont("Segoe UI", 11))
            paid_item.setForeground(QBrush(QColor("#2E9E6B")))
            self.table.setItem(row_idx, 3, paid_item)

            # Due amount (right-aligned, bold, orange)
            due_item = QTableWidgetItem(f"Rs.{row_data['due_amount']:,.0f}")
            due_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            due_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            due_item.setForeground(QBrush(QColor("#C98A2E")))
            self.table.setItem(row_idx, 4, due_item)

            # Pay Now button
            pay_btn = QPushButton("Pay Now")
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setFixedHeight(32)
            pay_btn.setStyleSheet(
                "QPushButton {"
                "  background:#1F8A9E; color:white; border:none;"
                "  border-radius:8px; font-weight:600; font-size:12px;"
                "  padding:0 16px;"
                "}"
                "QPushButton:hover { background:#16707F; }"
                "QPushButton:pressed { background:#125B67; }"
            )
            pay_btn.clicked.connect(
                lambda _, pid=row_data['patient_id'], tid=row_data['treatment_id']: self._on_pay_now(pid, tid)
            )
            self.table.setCellWidget(row_idx, 5, pay_btn)

        # Resize table height to fit its content — no internal scrolling
        row_count = self.table.rowCount()
        header_h = self.table.horizontalHeader().height()
        rows_h = row_count * self.table.verticalHeader().defaultSectionSize()
        self.table.setFixedHeight(header_h + rows_h + 4)

    # ── Pay Now action ────────────────────────────────────────────────────────

    def _on_pay_now(self, patient_id: int, treatment_id: int):
        dialog = RecordPaymentDialog(
            parent=self,
            prefill_patient_id=patient_id,
            prefill_treatment_id=treatment_id,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
