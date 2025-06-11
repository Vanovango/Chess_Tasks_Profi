from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QKeyEvent
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QSpinBox, QPushButton, QWidget,
    QButtonGroup, QMessageBox, QFrame
)
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from config import (
    DEFAULT_GRID_SIZE, COMPLEXITY_SETTINGS, TASK_TYPES, UI_COLORS, DB_PATH,
    GRID_SIZE_SETTINGS, FIGURE_TYPES, VALIDATION_SETTINGS, db_connection
)

class FigureButton(QPushButton):
    def __init__(self, figure_id: int, figure_info: dict):
        super().__init__()
        self.figure_id = figure_id
        self.figure_info = figure_info
        self.setCheckable(True)
        self.setFixedSize(40, 40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                font-size: 20px;
                font-weight: bold;
                color: {UI_COLORS['primary']};
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
                color: white;
            }}
            QPushButton:checked {{
                background-color: {UI_COLORS['secondary']};
                color: white;
            }}
        """)
        self.setText(figure_info['symbol'])
        self.setToolTip(figure_info['description'])

class TaskCanvas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.figures = {}
        self.walls = []
        self.selected_cell = None
        self.digit_counter = 1
        self.setMouseTracking(True)
        self.setMinimumSize(400, 400)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {UI_COLORS['grid']};
                border-radius: 5px;
            }}
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate cell size
        cell_size = min(
            (self.width() - 40) // self.parent.size_spin.value(),
            (self.height() - 40) // self.parent.size_spin.value()
        )
        margin = (self.width() - cell_size * self.parent.size_spin.value()) // 2

        # Создаем цвета
        grid_color = QColor(UI_COLORS['grid'])
        primary_color = QColor(UI_COLORS['primary'])
        secondary_color = QColor(UI_COLORS['secondary'])
        accent_color = QColor(UI_COLORS['accent'])
        
        # Рисуем сетку
        painter.setPen(QPen(grid_color, 1))

        # Draw grid
        for i in range(self.parent.size_spin.value() + 1):
            # Vertical lines
            painter.drawLine(
                margin + i * cell_size, margin,
                margin + i * cell_size, margin + self.parent.size_spin.value() * cell_size
            )
            # Horizontal lines
            painter.drawLine(
                margin, margin + i * cell_size,
                margin + self.parent.size_spin.value() * cell_size, margin + i * cell_size
            )

        # Draw walls
        painter.setPen(QPen(primary_color, 3))
        for wall in self.walls:
            x1, y1, x2, y2 = wall
            painter.drawLine(
                margin + x1 * cell_size, margin + y1 * cell_size,
                margin + x2 * cell_size, margin + y2 * cell_size
            )

        # Draw figures
        for (x, y), figure_id in self.figures.items():
            if figure_id in FIGURE_TYPES:
                figure = FIGURE_TYPES[figure_id]
                if figure_id == 1:  # Empty circle
                    painter.setPen(QPen(secondary_color, 2))
                    painter.setBrush(QBrush(UI_COLORS['background']))
                    painter.drawEllipse(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//4,
                        cell_size//2, cell_size//2
                    )
                elif figure_id == 2:  # Filled circle
                    painter.setPen(QPen(secondary_color, 2))
                    painter.setBrush(QBrush(UI_COLORS['primary']))
                    painter.drawEllipse(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//4,
                        cell_size//2, cell_size//2
                    )
                elif figure_id == 3:  # Wall
                    painter.setPen(QPen(primary_color, 3))
                    painter.drawLine(
                        margin + x * cell_size, margin + y * cell_size,
                        margin + (x + 1) * cell_size, margin + (y + 1) * cell_size
                    )
                elif figure_id == 4:  # Start point
                    painter.setFont(QFont('Arial', cell_size//3, QFont.Bold))
                    painter.setPen(QPen(secondary_color, 2))
                    painter.drawText(
                        QRect(margin + x * cell_size, margin + y * cell_size, cell_size, cell_size),
                        Qt.AlignCenter, "1"
                    )
                elif figure_id == 5:  # End point
                    painter.setFont(QFont('Arial', cell_size//3, QFont.Bold))
                    painter.setPen(QPen(secondary_color, 2))
                    painter.drawText(
                        QRect(margin + x * cell_size, margin + y * cell_size, cell_size, cell_size),
                        Qt.AlignCenter, "2"
                    )
                elif figure_id == 6:  # Number
                    painter.setFont(QFont('Arial', cell_size//3, QFont.Bold))
                    painter.setPen(QPen(secondary_color, 2))
                    painter.drawText(
                        QRect(margin + x * cell_size, margin + y * cell_size, cell_size, cell_size),
                        Qt.AlignCenter, str(self.digit_counter)
                    )

        # Draw selected cell highlight
        if self.selected_cell:
            x, y = self.selected_cell
            painter.setPen(QPen(accent_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(
                margin + x * cell_size + 1,
                margin + y * cell_size + 1,
                cell_size - 2, cell_size - 2
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cell_size = min(
                (self.width() - 40) // self.parent.size_spin.value(),
                (self.height() - 40) // self.parent.size_spin.value()
            )
            margin = (self.width() - cell_size * self.parent.size_spin.value()) // 2
            
            x = (event.x() - margin) // cell_size
            y = (event.y() - margin) // cell_size
            
            if 0 <= x < self.parent.size_spin.value() and 0 <= y < self.parent.size_spin.value():
                self.selected_cell = (x, y)
                
                if self.parent.selected_figure:
                    if self.parent.selected_figure in [4, 5, 6]:  # Start, End, Number
                        # Remove existing figure of same type
                        for pos, fig_id in list(self.figures.items()):
                            if fig_id == self.parent.selected_figure:
                                del self.figures[pos]
                        
                        # Add new figure
                        self.figures[(x, y)] = self.parent.selected_figure
                        if self.parent.selected_figure == 6:  # Number
                            self.digit_counter += 1
                    else:  # Other figures
                        self.figures[(x, y)] = self.parent.selected_figure
                
                self.update()

    def mouseMoveEvent(self, event):
        cell_size = min(
            (self.width() - 40) // self.parent.size_spin.value(),
            (self.height() - 40) // self.parent.size_spin.value()
        )
        margin = (self.width() - cell_size * self.parent.size_spin.value()) // 2
        
        x = (event.x() - margin) // cell_size
        y = (event.y() - margin) // cell_size
        
        if 0 <= x < self.parent.size_spin.value() and 0 <= y < self.parent.size_spin.value():
            self.selected_cell = (x, y)
        else:
            self.selected_cell = None
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_cell = None
            self.update()

class CreateTaskForm(QDialog):
    taskCreated = QtCore.pyqtSignal()

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.parent = parent
        self.name = name
        self.figures_on_board = {}
        self.selected_figure = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Создание задачи' + (f': {self.name}' if self.name else ''))
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {UI_COLORS['background']};
            }}
            QLabel {{
                color: {UI_COLORS['primary']};
                font-size: 14px;
                font-weight: bold;
            }}
            QComboBox, QLineEdit, QTextEdit, QSpinBox {{
                background-color: {UI_COLORS['background']};
                border: 2px solid {UI_COLORS['primary']};
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
                color: {UI_COLORS['primary']};
            }}
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-height: 40px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:checked {{
                background-color: {UI_COLORS['secondary']};
            }}
        """)
        
        # Main layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # Left panel for controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Task type selection
        type_label = QLabel('Тип задачи:')
        self.type_combo = QComboBox()
        self.type_combo.addItems(TASK_TYPES.keys())
        self.type_combo.currentTextChanged.connect(self.onTaskTypeChanged)
        
        # Task theme selection
        theme_label = QLabel('Тема задачи:')
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.onTaskThemeChanged)
        
        # Task name
        name_label = QLabel('Название задачи:')
        self.name_edit = QLineEdit()
        
        # Task description
        desc_label = QLabel('Описание задачи:')
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        
        # Grid size
        size_label = QLabel('Размер сетки:')
        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 8)
        self.size_spin.setValue(DEFAULT_GRID_SIZE)
        self.size_spin.valueChanged.connect(lambda: self.canvas.update())
        
        # Figures panel
        figures_label = QLabel('Доступные фигуры:')
        self.figures_panel = QVBoxLayout()
        self.figures_panel.setSpacing(10)
        
        # Add widgets to left panel
        left_panel.addWidget(type_label)
        left_panel.addWidget(self.type_combo)
        left_panel.addWidget(theme_label)
        left_panel.addWidget(self.theme_combo)
        left_panel.addWidget(name_label)
        left_panel.addWidget(self.name_edit)
        left_panel.addWidget(desc_label)
        left_panel.addWidget(self.desc_edit)
        left_panel.addWidget(size_label)
        left_panel.addWidget(self.size_spin)
        left_panel.addWidget(figures_label)
        left_panel.addLayout(self.figures_panel)
        left_panel.addStretch()
        
        # Save button
        self.save_btn = QPushButton('Сохранить')
        self.save_btn.clicked.connect(self.saveTask)
        left_panel.addWidget(self.save_btn)
        
        # Right panel for grid
        right_panel = QVBoxLayout()
        self.canvas = TaskCanvas(self)
        right_panel.addWidget(self.canvas)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)
        
        main_layout.addWidget(left_widget)
        main_layout.addLayout(right_panel)
        
        self.onTaskTypeChanged(self.type_combo.currentText())
        
        # Set window properties
        self.setMinimumSize(1000, 700)

    def onTaskTypeChanged(self, task_type: str):
        """Update available themes and figures based on task type"""
        self.theme_combo.clear()
        if task_type in TASK_TYPES:
            self.theme_combo.addItems(TASK_TYPES[task_type])
        self.update_figure_buttons(task_type)

    def onTaskThemeChanged(self, theme: str):
        """Update available figures based on task theme"""
        self.update_figure_buttons(self.type_combo.currentText(), theme)

    def update_figure_buttons(self, task_type: str, theme: str = None):
        """Update available figure buttons based on task type and theme"""
        # Clear existing buttons
        while self.figures_panel.count():
            item = self.figures_panel.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create button group for figures
        self.figure_group = QtWidgets.QButtonGroup(self)
        self.figure_group.setExclusive(True)
        self.figure_group.buttonClicked.connect(self.onFigureSelected)

        # Add figure buttons based on task type and theme
        if task_type == "Замкнутые":
            if theme == "Цикл с пустыми и закрашенными точками":
                self.add_figure_button(1, FIGURE_TYPES[1])
                self.add_figure_button(2, FIGURE_TYPES[2])
            elif theme == "Цикл с закрашенными точками":
                self.add_figure_button(1, FIGURE_TYPES[1])
            elif theme == "Замкнутый путь с перегородками":
                self.add_figure_button(3, FIGURE_TYPES[3])
            elif theme == "Путь ладьи 1-2-3 с перегородками":
                self.add_figure_button(4, FIGURE_TYPES[4])
                self.add_figure_button(5, FIGURE_TYPES[5])
                self.add_figure_button(3, FIGURE_TYPES[3])
            elif theme == "Несколько замкнутых циклов":
                self.add_figure_button(6, FIGURE_TYPES[6])

    def add_figure_button(self, figure_id: int, figure_info: dict):
        """Add a figure button to the panel"""
        btn = FigureButton(figure_id, figure_info)
        self.figure_group.addButton(btn)
        self.figures_panel.addWidget(btn)

    def onFigureSelected(self, button):
        """Handle figure button selection"""
        self.selected_figure = button.figure_id
        # Обновляем состояние кнопок
        for btn in self.figure_group.buttons():
            btn.setChecked(btn == button)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for figure selection"""
        if event.key() in range(Qt.Key_1, Qt.Key_7):  # Keys 1-6
            figure_id = event.key() - Qt.Key_1 + 1
            for btn in self.figure_group.buttons():
                if btn.figure_id == figure_id:
                    btn.setChecked(True)
                    self.selected_figure = figure_id
                    break
        super().keyPressEvent(event)

    def saveTask(self):
        """Save task to database"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название задачи")
            return

        try:
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO tasks (
                        task_type, task_theme, name, description,
                        grid_size, walls, figures
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.type_combo.currentText(),
                    self.theme_combo.currentText(),
                    self.name_edit.text().strip(),
                    self.desc_edit.toPlainText().strip(),
                    self.size_spin.value(),
                    json.dumps([]),  # walls
                    json.dumps(self.canvas.figures)  # figures
                ))
                self.taskCreated.emit()
                self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить задачу: {str(e)}")
