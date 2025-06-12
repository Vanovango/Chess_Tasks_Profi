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
        self.selected_cell = None
        self.number_positions = {}  # {(x, y): number} для отслеживания цифр на поле
        self.available_numbers = set()  # Множество доступных цифр (удаленных)
        self.next_number = 1  # Следующая цифра для добавления
        self.walls = []  # Список стен в формате [(x1, y1, x2, y2, orientation), ...]
        self.wall_click_count = 0  # Счетчик нажатий для определения ориентации стены
        self.setMouseTracking(True)
        self.setMinimumSize(400, 400)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {UI_COLORS['grid']};
                border-radius: 5px;
            }}
        """)

    def get_wall_orientation(self):
        """Получаем ориентацию стены на основе счетчика нажатий"""
        orientations = ['left', 'top', 'right', 'bottom']
        return orientations[self.wall_click_count % 4]

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

        # Рисуем стены
        painter.setPen(QPen(primary_color, 3))
        for wall in self.walls:
            x1, y1, orientation = wall
            if orientation == 'left':
                painter.drawLine(
                    margin + x1 * cell_size, margin + y1 * cell_size,
                    margin + x1 * cell_size, margin + (y1 + 1) * cell_size
                )
            elif orientation == 'top':
                painter.drawLine(
                    margin + x1 * cell_size, margin + y1 * cell_size,
                    margin + (x1 + 1) * cell_size, margin + y1 * cell_size
                )
            elif orientation == 'right':
                painter.drawLine(
                    margin + (x1 + 1) * cell_size, margin + y1 * cell_size,
                    margin + (x1 + 1) * cell_size, margin + (y1 + 1) * cell_size
                )
            elif orientation == 'bottom':
                painter.drawLine(
                    margin + x1 * cell_size, margin + (y1 + 1) * cell_size,
                    margin + (x1 + 1) * cell_size, margin + (y1 + 1) * cell_size
                )

        # Draw figures
        for (x, y), figure_id in self.figures.items():
            if figure_id in FIGURE_TYPES:
                figure = FIGURE_TYPES[figure_id]
                if figure_id == 1:  # Empty circle
                    painter.setPen(QPen(secondary_color, 2))
                    painter.setBrush(QBrush(QColor(UI_COLORS['primary'])))
                    painter.drawEllipse(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//4,
                        cell_size//2, cell_size//2
                    )
                elif figure_id == 2:  # Filled circle
                    painter.setPen(QPen(secondary_color, 2))
                    painter.setBrush(QBrush(QColor(UI_COLORS['background'])))
                    painter.drawEllipse(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//4,
                        cell_size//2, cell_size//2
                    )
                elif figure_id == 8:  # Закрашенная клетка
                    painter.setPen(QPen(primary_color, 2))
                    painter.setBrush(QBrush(QColor(UI_COLORS['primary'])))
                    painter.drawRect(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//4,
                        cell_size//2, cell_size//2
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
                    number = self.number_positions.get((x, y), 1)
                    painter.drawText(
                        QRect(margin + x * cell_size, margin + y * cell_size, cell_size, cell_size),
                        Qt.AlignCenter, str(number)
                    )
                elif figure_id == 7:  # Cross
                    painter.setPen(QPen(primary_color, 2))
                    # Горизонтальная линия
                    painter.drawLine(
                        margin + x * cell_size + cell_size//4,
                        margin + y * cell_size + cell_size//2,
                        margin + (x + 1) * cell_size - cell_size//4,
                        margin + y * cell_size + cell_size//2
                    )
                    # Вертикальная линия
                    painter.drawLine(
                        margin + x * cell_size + cell_size//2,
                        margin + y * cell_size + cell_size//4,
                        margin + x * cell_size + cell_size//2,
                        margin + (y + 1) * cell_size - cell_size//4
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
        cell_size = min(
            (self.width() - 40) // self.parent.size_spin.value(),
            (self.height() - 40) // self.parent.size_spin.value()
        )
        margin = (self.width() - cell_size * self.parent.size_spin.value()) // 2
        
        x = (event.x() - margin) // cell_size
        y = (event.y() - margin) // cell_size
        
        if 0 <= x < self.parent.size_spin.value() and 0 <= y < self.parent.size_spin.value():
            if event.button() == Qt.LeftButton:
                self.selected_cell = (x, y)
                
                if self.parent.selected_figure:
                    if self.parent.selected_figure == 3:  # Стена
                        orientation = self.get_wall_orientation()
                        # Удаляем все существующие стены в этой клетке
                        self.walls = [w for w in self.walls if not (w[0] == x and w[1] == y)]
                        
                        # Добавляем новую стену в зависимости от ориентации
                        if orientation == 'left' and x > 0:  # Стена слева
                            wall = (x, y, orientation)
                            self.walls.append(wall)
                        elif orientation == 'top' and y > 0:  # Стена сверху
                            wall = (x, y, orientation)
                            self.walls.append(wall)
                        elif orientation == 'right' and x < self.parent.size_spin.value() - 1:  # Стена справа
                            wall = (x, y, orientation)
                            self.walls.append(wall)
                        elif orientation == 'bottom' and y < self.parent.size_spin.value() - 1:  # Стена снизу
                            wall = (x, y, orientation)
                            self.walls.append(wall)
                        
                        self.wall_click_count += 1
                    elif self.parent.selected_figure == 6:  # Number
                        # Удаляем предыдущую цифру если есть
                        if (x, y) in self.figures and self.figures[(x, y)] == 6:
                            old_number = self.number_positions[(x, y)]
                            self.available_numbers.add(old_number)
                            del self.number_positions[(x, y)]
                            del self.figures[(x, y)]
                        
                        # Добавляем новую цифру
                        if self.available_numbers:
                            # Берем минимальную доступную цифру
                            number = min(self.available_numbers)
                            self.available_numbers.remove(number)
                        else:
                            # Если нет доступных цифр, берем следующую
                            number = self.next_number
                            self.next_number += 1
                        
                        self.figures[(x, y)] = 6
                        self.number_positions[(x, y)] = number
                    elif self.parent.selected_figure == 7:  # Cross
                        # Просто добавляем/заменяем крест
                        self.figures[(x, y)] = 7
                    elif self.parent.selected_figure == 8:  # Закрашенная клетка
                        # Добавляем/заменяем закрашенную клетку
                        self.figures[(x, y)] = 8
                    else:  # Other figures
                        self.figures[(x, y)] = self.parent.selected_figure
            elif event.button() == Qt.RightButton:
                # Удаляем фигуру или стену по правой кнопке
                if self.parent.selected_figure == 3:  # Стена
                    # Проверяем все возможные ориентации для удаления
                    for orientation in ['left', 'top', 'right', 'bottom']:
                        wall = (x, y, orientation)
                        if wall in self.walls:
                            self.walls.remove(wall)
                elif (x, y) in self.figures:
                    if self.figures[(x, y)] == 6:  # Если удаляем цифру
                        number = self.number_positions[(x, y)]
                        self.available_numbers.add(number)  # Добавляем цифру в доступные
                        del self.number_positions[(x, y)]
                    del self.figures[(x, y)]
            
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

    def __init__(self, parent=None, name=None, task_id=None, task_type=None, task_theme=None, complexity=None, walls=None, figures=None):
        super().__init__(parent)
        self.parent = parent
        self.name = name
        self.task_id = task_id
        self.task_type = task_type
        self.task_theme = task_theme
        self.complexity = complexity
        self.walls = walls
        self.figures = figures
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
        
        # Grid size
        size_label = QLabel('Размер сетки:')
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 12)
        self.size_spin.setSingleStep(2)
        self.size_spin.setValue(6)
        self.size_spin.valueChanged.connect(lambda: self.canvas.update())
        
        # Figures panel
        figures_label = QLabel('Доступные фигуры:')
        self.figures_panel = QHBoxLayout()
        self.figures_panel.setSpacing(10)
        
        # Add widgets to left panel
        left_panel.addWidget(type_label)
        left_panel.addWidget(self.type_combo)
        left_panel.addWidget(theme_label)
        left_panel.addWidget(self.theme_combo)
        left_panel.addWidget(name_label)
        left_panel.addWidget(self.name_edit)
        left_panel.addWidget(size_label)
        left_panel.addWidget(self.size_spin)
        left_panel.addWidget(figures_label)
        
        # Создаем контейнер для панели фигур
        figures_container = QWidget()
        figures_container.setLayout(self.figures_panel)
        left_panel.addWidget(figures_container)
        
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

        # После создания self.canvas:
        if self.walls is not None:
            self.canvas.walls = list(self.walls)
        if self.figures is not None:
            # figures может быть как dict, так и list (если из базы)
            if isinstance(self.figures, dict):
                self.canvas.figures = {tuple(map(int, k.split(","))): v for k, v in self.figures.items()}
            elif isinstance(self.figures, list):
                # если список кортежей
                self.canvas.figures = {tuple(f[:2]): f[2] for f in self.figures}
        self.canvas.update()

    def onTaskTypeChanged(self, task_type: str):
        """Update available themes and figures based on task type"""
        self.theme_combo.clear()
        if task_type in TASK_TYPES:
            self.theme_combo.addItems(TASK_TYPES[task_type])
            # Автоматически выбираем первую тему
            if self.theme_combo.count() > 0:
                self.theme_combo.setCurrentIndex(0)
                self.update_figure_buttons(task_type, self.theme_combo.currentText())

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
                self.add_figure_button(3, FIGURE_TYPES[3])  # Только стена
            elif theme == "Путь ладьи 1-2-3 с перегородками":
                self.add_figure_button(6, FIGURE_TYPES[6])  # Цифра
                self.add_figure_button(7, FIGURE_TYPES[7])  # Крест
            elif theme == "Несколько замкнутых циклов":
                self.add_figure_button(8, FIGURE_TYPES[8])  # Закрашенная клетка

        # Автоматически выбираем первую кнопку
        if self.figure_group.buttons():
            first_button = self.figure_group.buttons()[0]
            first_button.setChecked(True)
            self.selected_figure = first_button.figure_id

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

        # Определяем сложность по числу клеток
        size = self.size_spin.value()
        if size == 6:
            complexity = 'Легко'
        elif size == 8:
            complexity = 'Средне'
        elif size == 10:
            complexity = 'Сложно'
        elif size == 12:
            complexity = 'Невозможно'
        else:
            complexity = 'Легко'

        try:
            # Преобразуем кортежи в строки для JSON
            figures_json = {f"{x},{y}": fig_id for (x, y), fig_id in self.canvas.figures.items()}
            walls_json = [f"{x},{y},{orientation}" for x, y, orientation in self.canvas.walls]
            
            with db_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO tasks (
                        task_type, task_theme, name, complexity,
                        grid_size, walls, figures
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.type_combo.currentText(),
                    self.theme_combo.currentText(),
                    self.name_edit.text().strip(),
                    complexity,
                    self.size_spin.value(),
                    json.dumps(walls_json),
                    json.dumps(figures_json)
                ))
                
                QMessageBox.information(self, "Успех", "Задача успешно сохранена")
                self.taskCreated.emit()
                self.accept()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить задачу: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла непредвиденная ошибка: {str(e)}")

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.canvas.figures or self.canvas.walls:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Вы уверены, что хотите закрыть окно? Все несохраненные изменения будут потеряны.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()
