from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar, QMessageBox
)
import random
import json
import sqlite3
import heapq
from typing import Dict, List, Optional, Tuple, Set
from config import (
    COMPLEXITY_SETTINGS, TASK_TYPES, UI_COLORS, DB_PATH,
    VALIDATION_SETTINGS, FIGURE_TYPES, TASK_THEME_FIGURES, db_connection
)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # Обновление каждые 50мс
        
    def rotate(self):
        self.angle = (self.angle + 10) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Полупрозрачный фон
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))
        
        # Центр экрана
        center = self.rect().center()
        
        # Текст
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 14, QFont.Bold))
        text = "Задача генерируется, пожалуйста подождите..."
        text_rect = painter.fontMetrics().boundingRect(text)
        text_rect.moveCenter(center)
        text_rect.moveTop(center.y() + 30)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        # Крутящийся индикатор
        painter.translate(center)
        painter.rotate(self.angle)
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        for i in range(8):
            painter.rotate(45)
            painter.drawLine(20, 0, 40, 0)
            
    def showEvent(self, event):
        self.timer.start()
        super().showEvent(event)
        
    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

class TaskGenerator(QMainWindow):
    finished = QtCore.pyqtSignal()

    def __init__(self, task_type: str, task_theme: str, complexity: str, parent=None):
        super().__init__(parent)
        self.task_type = task_type
        self.task_theme = task_theme
        self.complexity = complexity
        
        # Get grid settings
        settings = COMPLEXITY_SETTINGS[complexity]
        self.CELL_SIZE = int(settings['cell_size'])
        self.MARGIN = int(settings['margin'])
        self.GRID_SIZE = int(settings['grid_size'])
        
        # Calculate window dimensions
        self.SCREEN_WIDTH = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN)
        self.SCREEN_HEIGHT = int(self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 200)
        
        # Initialize task data
        self.walls = []
        self.figures = {}
        self.solution = None
        self.wall_cache = {}  # Кэш для проверки стен
        
        # Создаем оверлей загрузки до setup_ui
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()
        
        # Setup UI
        self.setup_ui()
        
        # Генерируем первую задачу после инициализации UI
        QTimer.singleShot(0, self.generate_task)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.size())

    def setup_ui(self):
        """Setup the UI components"""
        self.setWindowTitle(f"Генератор задач - {self.task_type}")
        self.setFixedSize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Create central widget and main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Info block
        info_block = QtWidgets.QFrame()
        info_block.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_COLORS['background']};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {UI_COLORS['grid']};
            }}
        """)
        info_layout = QtWidgets.QVBoxLayout(info_block)
        info_layout.setSpacing(5)
        
        # Add task info
        task_info = QtWidgets.QLabel(
            f"Тип: {self.task_type}\n"
            f"Тема: {self.task_theme}\n"
            f"Сложность: {self.complexity}"
        )
        task_info.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['text']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        info_layout.addWidget(task_info)
        main_layout.addWidget(info_block)
        
        # Grid area
        grid_block = QtWidgets.QFrame()
        grid_block.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_COLORS['background']};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {UI_COLORS['grid']};
            }}
        """)
        grid_layout = QtWidgets.QVBoxLayout(grid_block)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create canvas
        self.canvas = TaskCanvas(self)
        self.canvas.setFixedSize(self.SCREEN_WIDTH - 40, self.SCREEN_WIDTH - 40)
        grid_layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        main_layout.addWidget(grid_block)
        
        # Button block
        button_block = QtWidgets.QFrame()
        button_block.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_COLORS['background']};
                border-radius: 10px;
                padding: 10px;
                border: 1px solid {UI_COLORS['grid']};
            }}
        """)
        button_layout = QtWidgets.QHBoxLayout(button_block)
        button_layout.setSpacing(10)
        
        # Add buttons
        regenerate_btn = QtWidgets.QPushButton("Сгенерировать заново")
        regenerate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['secondary']};
            }}
        """)
        regenerate_btn.clicked.connect(self.generate_task)
        button_layout.addWidget(regenerate_btn)
        
        save_btn = QtWidgets.QPushButton("Сохранить")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['secondary']};
            }}
        """)
        save_btn.clicked.connect(self.save_task)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QtWidgets.QPushButton("Отмена")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['secondary']};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addWidget(button_block)

    def generate_task(self):
        """Generate a new task"""
        try:
            self.loading_overlay.show()
            QtWidgets.QApplication.processEvents()  # Обновляем UI
            
            # Clear previous task
            self.walls = []
            self.figures = {}
            self.solution = None
            self.wall_cache.clear()
            
            # Generate task based on type and theme
            if self.task_type == "Замкнутые":
                self.generate_closed_task()
            else:
                self.generate_open_task()
            
            # Validate the generated task
            if not self.validate_task():
                QtWidgets.QMessageBox.warning(
                    self, "Предупреждение",
                    "Сгенерированная задача не прошла валидацию. Попробуйте еще раз."
                )
                return
            
            # Update canvas
            self.canvas.update()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Ошибка при генерации задачи: {str(e)}"
            )
        finally:
            self.loading_overlay.hide()

    def save_task(self):
        """Save the generated task to the database"""
        try:
            # Check if we have walls and figures
            if not self.walls or not self.figures:
                QtWidgets.QMessageBox.warning(
                    self, "Предупреждение",
                    "Нельзя сохранить задачу без стен или фигур"
                )
                return
                
            # Get task name from main window
            task_name = self.parent().lineEdit_task_name.text()
            if not task_name:
                # Generate default name if not provided
                task_name = f"{self.task_type} - {self.task_theme} ({self.complexity})"
            
            # Convert figures to serializable format
            serialized_figures = {}
            for (x, y), fig_type in self.figures.items():
                serialized_figures[f"{x},{y}"] = fig_type
            
            # Save to database
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (
                        name, type, theme, complexity, grid_size,
                        walls, figures, solution
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_name,
                    self.task_type,
                    self.task_theme,
                    self.complexity,
                    self.GRID_SIZE,
                    json.dumps(self.walls),
                    json.dumps(serialized_figures),
                    json.dumps(self.solution) if self.solution else None
                ))
                conn.commit()
                
            QtWidgets.QMessageBox.information(
                self, "Успех",
                "Задача успешно сохранена"
            )
            self.close()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка",
                f"Ошибка при сохранении задачи: {str(e)}"
            )

    def validate_task(self) -> bool:
        """Validate the generated task"""
        if not self.walls or not self.figures:
            return False

        # Проверяем наличие решения
        if not self.find_solution():
            return False

        # Проверяем уникальность решения
        if not self.check_solution_uniqueness():
            return False

        # Проверяем соответствие фигур теме
        allowed_figures = TASK_THEME_FIGURES.get(self.task_theme, [])
        if not all(fig_type in allowed_figures for fig_type in self.figures.values()):
            return False

        # Проверяем плотность стен
        total_cells = self.GRID_SIZE * self.GRID_SIZE
        wall_density = len(self.walls) / total_cells
        if not (VALIDATION_SETTINGS['min_wall_density'] <= wall_density <= VALIDATION_SETTINGS['max_wall_density']):
            return False

        return True

    def find_solution(self) -> bool:
        """Find a valid solution for the task"""
        if self.task_type == "Замкнутые":
            return self.find_closed_path_solution()
        else:
            return self.find_open_path_solution()

    def find_closed_path_solution(self) -> bool:
        """Find a solution for closed path tasks"""
        if not self.figures:
            return False

        points = [(x, y) for (x, y), fig_type in self.figures.items() 
                 if fig_type in [1, 2]]
        
        if not points:
            return False

        # Начинаем с первой точки
        start = points[0]
        remaining_points = set(points[1:])
        
        # Ищем путь через все точки
        path = self.find_path_a_star(start, start, remaining_points)
        if path:
            self.solution = path
            return True
        return False

    def find_open_path_solution(self) -> bool:
        """Find a solution for open path tasks"""
        start = None
        end = None
        for (x, y), fig_type in self.figures.items():
            if fig_type == 4:  # Start
                start = (x, y)
            elif fig_type == 5:  # End
                end = (x, y)
                
        if not start or not end:
            return False

        path = self.find_path_a_star(start, end)
        if path:
            self.solution = path
            return True
        return False

    def check_solution_uniqueness(self) -> bool:
        """Check if the task has a unique solution"""
        if not self.solution:
            return False

        # Сохраняем текущее решение
        original_solution = self.solution.copy()
        
        # Пробуем найти альтернативное решение, исключая первый ход из оригинального решения
        if len(original_solution) > 1:
            first_move = original_solution[1]
            # Временно блокируем первый ход
            self.walls.append((first_move[0], first_move[1], 'top'))
            self.wall_cache.clear()  # Очищаем кэш
            
            # Пробуем найти альтернативное решение
            self.solution = None
            found_alternative = self.find_solution()
            
            # Восстанавливаем состояние
            self.walls.pop()
            self.wall_cache.clear()
            self.solution = original_solution
            
            return not found_alternative
            
        return True

    def generate_closed_task(self):
        """Generate a closed path task"""
        self.walls = []
        self.figures = {}
        
        # Получаем допустимые фигуры для темы
        allowed_figures = TASK_THEME_FIGURES.get(self.task_theme, [])
        if not allowed_figures:
            raise ValueError(f"Нет допустимых фигур для темы {self.task_theme}")
        
        # Определяем количество фигур в зависимости от сложности
        num_figures = {
            'Легко': 3,
            'Средне': 4,
            'Сложно': 5,
            'Невозможно': 6
        }[self.complexity]
        
        # Размещаем фигуры в соответствии с темой
        if self.task_theme == "Цикл с пустыми и закрашенными точками":
            # Чередуем пустые и закрашенные точки
            for i in range(num_figures):
                x = random.randint(0, self.GRID_SIZE - 1)
                y = random.randint(0, self.GRID_SIZE - 1)
                while (x, y) in self.figures:
                    x = random.randint(0, self.GRID_SIZE - 1)
                    y = random.randint(0, self.GRID_SIZE - 1)
                self.figures[(x, y)] = 1 if i % 2 == 0 else 2
                
        elif self.task_theme == "Цикл с закрашенными точками":
            # Только закрашенные точки
            for i in range(num_figures):
                x = random.randint(0, self.GRID_SIZE - 1)
                y = random.randint(0, self.GRID_SIZE - 1)
                while (x, y) in self.figures:
                    x = random.randint(0, self.GRID_SIZE - 1)
                    y = random.randint(0, self.GRID_SIZE - 1)
                self.figures[(x, y)] = 1
                
        elif self.task_theme == "Замкнутый путь с перегородками":
            # Точки и стены
            for i in range(num_figures // 2):
                # Точка
                x = random.randint(0, self.GRID_SIZE - 1)
                y = random.randint(0, self.GRID_SIZE - 1)
                while (x, y) in self.figures:
                    x = random.randint(0, self.GRID_SIZE - 1)
                    y = random.randint(0, self.GRID_SIZE - 1)
                self.figures[(x, y)] = 1
                
                # Стена
                wx = random.randint(0, self.GRID_SIZE - 1)
                wy = random.randint(0, self.GRID_SIZE - 1)
                while (wx, wy) in self.figures or (wx, wy) in self.walls:
                    wx = random.randint(0, self.GRID_SIZE - 1)
                    wy = random.randint(0, self.GRID_SIZE - 1)
                orientation = random.choice(['left', 'top', 'right', 'bottom'])
                self.walls.append((wx, wy, orientation))
                
        elif self.task_theme == "Путь ладьи 1-2-3 с перегородками":
            # Числа и кресты
            numbers = list(range(1, num_figures + 1))
            random.shuffle(numbers)
            for i, num in enumerate(numbers):
                x = random.randint(0, self.GRID_SIZE - 1)
                y = random.randint(0, self.GRID_SIZE - 1)
                while (x, y) in self.figures:
                    x = random.randint(0, self.GRID_SIZE - 1)
                    y = random.randint(0, self.GRID_SIZE - 1)
                self.figures[(x, y)] = 6  # Число
                
                # Добавляем крест рядом с числом
                if i < len(numbers) - 1:  # Не добавляем крест после последнего числа
                    cx = x + random.choice([-1, 0, 1])
                    cy = y + random.choice([-1, 0, 1])
                    if 0 <= cx < self.GRID_SIZE and 0 <= cy < self.GRID_SIZE and (cx, cy) not in self.figures:
                        self.figures[(cx, cy)] = 7  # Крест
                        
        elif self.task_theme == "Несколько замкнутых циклов":
            # Чередуем пустые и закрашенные точки для разных циклов
            cycle_size = num_figures // 2
            for cycle in range(2):
                for i in range(cycle_size):
                    x = random.randint(0, self.GRID_SIZE - 1)
                    y = random.randint(0, self.GRID_SIZE - 1)
                    while (x, y) in self.figures:
                        x = random.randint(0, self.GRID_SIZE - 1)
                        y = random.randint(0, self.GRID_SIZE - 1)
                    self.figures[(x, y)] = 1 if cycle == 0 else 2
        
        # Добавляем дополнительные стены для усложнения
        wall_count = int(self.GRID_SIZE * self.GRID_SIZE * random.uniform(
            VALIDATION_SETTINGS['min_wall_density'],
            VALIDATION_SETTINGS['max_wall_density']
        ))
        
        walls_placed = 0
        attempts = 0
        while walls_placed < wall_count and attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            pos = (x, y)
            
            if pos not in self.walls and pos not in self.figures:
                orientation = random.choice(['left', 'top', 'right', 'bottom'])
                self.walls.append((x, y, orientation))
                walls_placed += 1
            attempts += 1
            
        # Проверяем и находим решение
        if not self.find_solution():
            # Если решение не найдено, пробуем сгенерировать заново
            self.generate_closed_task()

    def generate_open_task(self):
        """Generate an open path task"""
        self.walls = []
        self.figures = {}
        
        # Place start point
        x1 = random.randint(0, self.GRID_SIZE - 1)
        y1 = random.randint(0, self.GRID_SIZE - 1)
        self.figures[f"{x1},{y1}"] = 4  # Start
        
        # Place end point
        while True:
            x2 = random.randint(0, self.GRID_SIZE - 1)
            y2 = random.randint(0, self.GRID_SIZE - 1)
            if (x2, y2) != (x1, y1):
                self.figures[f"{x2},{y2}"] = 5  # End
                break
        
        # Add walls
        wall_count = int(self.GRID_SIZE * self.GRID_SIZE * random.uniform(
            VALIDATION_SETTINGS['min_wall_density'],
            VALIDATION_SETTINGS['max_wall_density']
        ))
        
        walls_placed = 0
        attempts = 0
        while walls_placed < wall_count and attempts < 100:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            pos = f"{x},{y}"
            
            if pos not in self.walls and pos not in self.figures:
                self.walls.append(pos)
                walls_placed += 1
            attempts += 1

    def update_ui(self):
        """Update UI with current values"""
        # Update grid settings based on new complexity
        settings = COMPLEXITY_SETTINGS[self.complexity]
        self.CELL_SIZE = int(settings['cell_size'])
        self.MARGIN = int(settings['margin'])
        self.GRID_SIZE = int(settings['grid_size'])
        
        # Update window title
        self.setWindowTitle("Генератор задач")
        
        # Update info label
        if hasattr(self, 'info_label'):
            self.info_label.setText(
                f"<b>Тип:</b> {self.task_type}<br>"
                f"<b>Тема:</b> {self.task_theme}<br>"
                f"<b>Сложность:</b> {self.complexity}"
            )
        
        # Reset task data
        self.walls = []
        self.figures = {}
        self.solution = None
        
        # Force canvas redraw
        if hasattr(self, 'canvas'):
            self.canvas.update()

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.finished.emit()  # Эмитим сигнал при закрытии
        super().closeEvent(event)

    def is_valid_move(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Оптимизированная проверка хода с кэшированием"""
        key = (x1, y1, x2, y2)
        if key in self.wall_cache:
            return self.wall_cache[key]
            
        for wx, wy, orientation in self.walls:
            if orientation == 'left' and x1 == x2 and y1 == y2 - 1 and wx == x1 and wy == y1:
                self.wall_cache[key] = False
                return False
            if orientation == 'right' and x1 == x2 and y1 == y2 + 1 and wx == x1 and wy == y1:
                self.wall_cache[key] = False
                return False
            if orientation == 'top' and x1 == x2 - 1 and y1 == y2 and wx == x1 and wy == y1:
                self.wall_cache[key] = False
                return False
            if orientation == 'bottom' and x1 == x2 + 1 and y1 == y2 and wx == x1 and wy == y1:
                self.wall_cache[key] = False
                return False
                
        self.wall_cache[key] = True
        return True

    def find_path_a_star(self, start: Tuple[int, int], end: Tuple[int, int], 
                        must_visit: Set[Tuple[int, int]] = None) -> Optional[List[Tuple[int, int]]]:
        """Поиск пути с использованием алгоритма A*"""
        if must_visit is None:
            must_visit = set()
            
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE and 
                    self.is_valid_move(x, y, nx, ny)):
                    neighbors.append((nx, ny))
            return neighbors
            
        # Очередь с приоритетом: (f_score, count, pos, path, visited)
        count = 0  # Для стабильной сортировки
        queue = [(0, count, start, [start], {start})]
        heapq.heapify(queue)
        
        # Множество посещенных позиций
        closed_set = set()
        
        while queue:
            _, _, pos, path, visited = heapq.heappop(queue)
            
            if pos == end and not (must_visit - visited):
                return path
                
            if pos in closed_set:
                continue
                
            closed_set.add(pos)
            
            for next_pos in get_neighbors(pos):
                if next_pos in closed_set:
                    continue
                    
                new_path = path + [next_pos]
                new_visited = visited | {next_pos}
                
                # Вычисляем f_score (g_score + h_score)
                g_score = len(new_path)
                h_score = heuristic(next_pos, end)
                f_score = g_score + h_score
                
                count += 1
                heapq.heappush(queue, (f_score, count, next_pos, new_path, new_visited))
                
        return None

class TaskCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw grid
        self.draw_grid(painter)
        
        # Draw walls
        self.draw_walls(painter)
        
        # Draw figures
        self.draw_figures(painter)
    
    def draw_grid(self, painter):
        """Draw the task grid"""
        painter.setPen(QPen(QColor(UI_COLORS['grid']), 1))
        
        # Draw vertical lines
        for i in range(self.parent.GRID_SIZE + 1):
            x = self.parent.MARGIN + i * self.parent.CELL_SIZE
            painter.drawLine(x, self.parent.MARGIN,
                           x, self.parent.MARGIN + self.parent.GRID_SIZE * self.parent.CELL_SIZE)
        
        # Draw horizontal lines
        for i in range(self.parent.GRID_SIZE + 1):
            y = self.parent.MARGIN + i * self.parent.CELL_SIZE
            painter.drawLine(self.parent.MARGIN, y,
                           self.parent.MARGIN + self.parent.GRID_SIZE * self.parent.CELL_SIZE, y)
    
    def draw_walls(self, painter: QPainter):
        """Draw walls on the grid"""
        painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
        
        for x, y, orientation in self.parent.walls:
            if orientation == 'left':
                start_x = x * self.parent.CELL_SIZE + self.parent.MARGIN
                start_y = y * self.parent.CELL_SIZE + self.parent.MARGIN
                end_x = start_x
                end_y = start_y + self.parent.CELL_SIZE
            elif orientation == 'right':
                start_x = (x + 1) * self.parent.CELL_SIZE + self.parent.MARGIN
                start_y = y * self.parent.CELL_SIZE + self.parent.MARGIN
                end_x = start_x
                end_y = start_y + self.parent.CELL_SIZE
            elif orientation == 'top':
                start_x = x * self.parent.CELL_SIZE + self.parent.MARGIN
                start_y = y * self.parent.CELL_SIZE + self.parent.MARGIN
                end_x = start_x + self.parent.CELL_SIZE
                end_y = start_y
            else:  # bottom
                start_x = x * self.parent.CELL_SIZE + self.parent.MARGIN
                start_y = (y + 1) * self.parent.CELL_SIZE + self.parent.MARGIN
                end_x = start_x + self.parent.CELL_SIZE
                end_y = start_y
                
            painter.drawLine(start_x, start_y, end_x, end_y)

    def draw_figures(self, painter: QPainter):
        """Draw figures on the grid"""
        for (x, y), fig_type in self.parent.figures.items():
            center_x = x * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            center_y = y * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            radius = self.parent.CELL_SIZE // 3
            
            if fig_type == 1:  # Empty point
                painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(center_x - radius, center_y - radius, 
                                  radius * 2, radius * 2)
            elif fig_type == 2:  # Filled point
                painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
                painter.setBrush(QBrush(QColor(UI_COLORS['grid'])))
                painter.drawEllipse(center_x - radius, center_y - radius, 
                                  radius * 2, radius * 2)
            elif fig_type == 3:  # Wall
                painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
                painter.setBrush(QBrush(QColor(UI_COLORS['grid'])))
                painter.drawRect(center_x - radius//2, center_y - radius//2, 
                               radius, radius)
            elif fig_type == 4:  # Start
                painter.setPen(QPen(QColor(UI_COLORS['accent']), 2))
                painter.setBrush(QBrush(QColor(UI_COLORS['accent'])))
                painter.drawEllipse(center_x - radius, center_y - radius, 
                                  radius * 2, radius * 2)
            elif fig_type == 5:  # End
                painter.setPen(QPen(QColor(UI_COLORS['accent']), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(center_x - radius, center_y - radius, 
                                  radius * 2, radius * 2)
            elif fig_type == 6:  # Cross
                painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
                painter.setBrush(Qt.NoBrush)
                # Draw cross
                cross_size = radius
                painter.drawLine(center_x - cross_size, center_y, 
                               center_x + cross_size, center_y)
                painter.drawLine(center_x, center_y - cross_size, 
                               center_x, center_y + cross_size)
            elif fig_type == 7:  # Number
                painter.setPen(QPen(QColor(UI_COLORS['grid']), 2))
                painter.setBrush(Qt.NoBrush)
                # Draw number (1-9)
                number = self.parent.figures.get((x, y), 1)  # Default to 1 if not specified
                painter.setFont(QFont('Arial', radius))
                painter.drawText(QRect(center_x - radius, center_y - radius, 
                                     radius * 2, radius * 2),
                               Qt.AlignCenter, str(number))

    def draw_solution(self, painter: QPainter):
        """Draw solution path if exists"""
        if not self.parent.solution:
            return
            
        painter.setPen(QPen(QColor(UI_COLORS['accent']), 2))
        painter.setBrush(Qt.NoBrush)
        
        # Draw lines between points
        for i in range(len(self.parent.solution) - 1):
            x1, y1 = self.parent.solution[i]
            x2, y2 = self.parent.solution[i + 1]
            
            start_x = x1 * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            start_y = y1 * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            end_x = x2 * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            end_y = y2 * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            
            painter.drawLine(start_x, start_y, end_x, end_y)
            
        # Draw points
        for x, y in self.parent.solution:
            center_x = x * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            center_y = y * self.parent.CELL_SIZE + self.parent.MARGIN + self.parent.CELL_SIZE // 2
            radius = self.parent.CELL_SIZE // 6
            
            painter.setBrush(QBrush(QColor(UI_COLORS['accent'])))
            painter.drawEllipse(center_x - radius, center_y - radius, 
                              radius * 2, radius * 2) 