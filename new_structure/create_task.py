import pygame
import json

class CreateTaskForm:
    def __init__(self, task_id=None, theme=None, name=None, complexity=None, walls=None, figures=None):
        complexity_variants = {
            'Легко': (100, 50, 6),
            'Средне': (80, 50, 8),
            'Сложно': (60, 50, 10),
            'Невозможно': (40, 50, 16)
        }

        self.task_id = task_id
        self.theme = theme
        self.name = name
        self.complexity = complexity
        self.walls = walls or {}
        self.figures = figures or {}

        self.CELL_SIZE, self.MARGIN, self.GRID_SIZE = complexity_variants[complexity]
        self.SCREEN_WIDTH = self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 200
        self.DB_FILE = DB_PATH

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Редактор задачи" if self.task_id else "Новая задача")
        self.font = pygame.font.SysFont(None, 30)
        self.big_font = pygame.font.SysFont(None, max(30, self.CELL_SIZE // 2))

        self.buttons = {}
        self.figure_mode = 1
        self.number_counter = 1

        self.FIGURE_LABELS = {
            1: "Залитый круг",
            2: "Не залитый круг",
            3: "Стена",
            4: "Цифра",
            5: "Перекрестье",
            6: "Заливка"
        }

    def save_to_db(self):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        walls_json = json.dumps(list(self.walls.keys()))
        figures_json = json.dumps({f"{k[0]},{k[1]}": v for k, v in self.figures.items()})
        if self.task_id is None:
            cursor.execute("INSERT INTO tasks (theme, name, complexity, walls, figures) VALUES (?, ?, ?, ?, ?)",
                           (self.theme, self.name, self.complexity, walls_json, figures_json))
        else:
            cursor.execute("UPDATE tasks SET walls = ?, figures = ? WHERE id = ?",
                           (walls_json, figures_json, self.task_id))
        conn.commit()
        conn.close()
        print("Задача сохранена в базу данных")

    def delete_from_db(self):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
        conn.commit()
        conn.close()
        print("Задача удалена из базы данных")

    def draw_grid(self):
        for i in range(self.GRID_SIZE + 1):
            pygame.draw.line(self.screen, (0, 0, 0),
                             (self.MARGIN + i * self.CELL_SIZE, self.MARGIN),
                             (self.MARGIN + i * self.CELL_SIZE, self.MARGIN + self.GRID_SIZE * self.CELL_SIZE))
            pygame.draw.line(self.screen, (0, 0, 0),
                             (self.MARGIN, self.MARGIN + i * self.CELL_SIZE),
                             (self.MARGIN + self.GRID_SIZE * self.CELL_SIZE, self.MARGIN + i * self.CELL_SIZE))

    def draw_walls(self):
        for (x1, y1, x2, y2) in self.walls:
            if x1 == x2:
                x = self.MARGIN + x1 * self.CELL_SIZE
                y1 = self.MARGIN + y1 * self.CELL_SIZE
                y2 = self.MARGIN + y2 * self.CELL_SIZE
                pygame.draw.line(self.screen, (255, 0, 0), (x, y1), (x, y2), 5)
            elif y1 == y2:
                y = self.MARGIN + y1 * self.CELL_SIZE
                x1 = self.MARGIN + x1 * self.CELL_SIZE
                x2 = self.MARGIN + x2 * self.CELL_SIZE
                pygame.draw.line(self.screen, (255, 0, 0), (x1, y), (x2, y), 5)

    def draw_figures(self):
        for (x, y), value in self.figures.items():
            cx = self.MARGIN + x * self.CELL_SIZE + self.CELL_SIZE // 2
            cy = self.MARGIN + y * self.CELL_SIZE + self.CELL_SIZE // 2
            r = int(self.CELL_SIZE * 0.33)

            if value == 1:  # залитый круг
                pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), r)

            elif value == 2:  # не залитый круг
                pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), r, 3)

            elif isinstance(value, int) and value >= 1000:  # цифра
                number = value - 1000
                text = self.big_font.render(str(number), True, (0, 128, 0))
                rect = text.get_rect(center=(cx, cy))
                self.screen.blit(text, rect)

            elif value == 5:  # крест
                offset = int(self.CELL_SIZE * 0.25)
                pygame.draw.line(self.screen, (0, 128, 0), (cx - offset, cy), (cx + offset, cy), 3)
                pygame.draw.line(self.screen, (0, 128, 0), (cx, cy - offset), (cx, cy + offset), 3)

            elif value == 6:  # заливка
                pygame.draw.rect(self.screen, (0, 0, 0), (
                    self.MARGIN + x * self.CELL_SIZE + 2,
                    self.MARGIN + y * self.CELL_SIZE + 2,
                    self.CELL_SIZE - 4,
                    self.CELL_SIZE - 4
                ))

    def get_cell(self, pos):
        x, y = pos
        x -= self.MARGIN
        y -= self.MARGIN
        if x < 0 or y < 0 or x >= self.GRID_SIZE * self.CELL_SIZE or y >= self.GRID_SIZE * self.CELL_SIZE:
            return None
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE
        return col, row

    def get_line(self, pos):
        x, y = pos
        x -= self.MARGIN
        y -= self.MARGIN
        if x < 0 or y < 0 or x > self.GRID_SIZE * self.CELL_SIZE or y > self.GRID_SIZE * self.CELL_SIZE:
            return None
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE
        dx = x % self.CELL_SIZE
        dy = y % self.CELL_SIZE
        if dx < 10 and col > 0:
            return col, row, col, row + 1
        if dx > self.CELL_SIZE - 10 and col < self.GRID_SIZE:
            return col + 1, row, col + 1, row + 1
        if dy < 10 and row > 0:
            return col, row, col + 1, row
        if dy > self.CELL_SIZE - 10 and row < self.GRID_SIZE:
            return col, row + 1, col + 1, row + 1
        return None

    def draw_ui(self):
        self.buttons = {
            "reset": pygame.Rect(50, self.SCREEN_HEIGHT - 80, 130, 40),
            "save_db": pygame.Rect(200, self.SCREEN_HEIGHT - 80, 150, 40),
        }

        if self.task_id is not None:
            self.buttons["delete_task"] = pygame.Rect(370, self.SCREEN_HEIGHT - 80, 200, 40)

        for key, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
        self.screen.blit(self.font.render("Сброс", True, (0, 0, 0)), (85, self.SCREEN_HEIGHT - 68))
        self.screen.blit(self.font.render("Сохранить", True, (0, 0, 0)), (230, self.SCREEN_HEIGHT - 68))

        if self.task_id is not None:
            self.screen.blit(self.font.render("Удалить задачу", True, (0, 0, 0)), (390, self.SCREEN_HEIGHT - 68))

        for i in range(1, 7):
            label = self.FIGURE_LABELS[i]
            color = (255, 0, 0) if self.figure_mode == i else (0, 0, 0)
            text = self.font.render(f"{i}: {label}", True, color)
            if i in [1,2,3]:
                self.screen.blit(text, (self.MARGIN + (i - 1) * 250, self.SCREEN_HEIGHT - 200))
            else:
                self.screen.blit(text, (self.MARGIN + (i - 4) * 250, self.SCREEN_HEIGHT - 160))
    def run(self):
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_walls()
            self.draw_figures()
            self.draw_ui()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.unicode in "123456":
                        self.figure_mode = int(event.unicode)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.buttons["reset"].collidepoint(pos):
                        self.walls.clear()
                        self.figures.clear()
                        self.number_counter = 1
                    elif self.buttons["save_db"].collidepoint(pos):
                        self.save_to_db()
                        running = False
                    elif "delete_task" in self.buttons and self.buttons["delete_task"].collidepoint(pos):
                        self.delete_from_db()
                        running = False
                    else:
                        if self.figure_mode == 3:  # стена
                            line = self.get_line(pos)
                            if line:
                                if event.button == 1:
                                    self.walls[line] = True
                                elif event.button == 3:
                                    self.walls.pop(line, None)
                        else:
                            cell = self.get_cell(pos)
                            if not cell:
                                continue
                            if event.button == 1:
                                if self.figure_mode == 4:
                                    self.figures[cell] = 1000 + self.number_counter
                                    self.number_counter += 1
                                else:
                                    self.figures[cell] = self.figure_mode
                            elif event.button == 3:
                                if cell in self.figures:
                                    val = self.figures[cell]
                                    if isinstance(val, int) and val >= 1001:
                                        self.number_counter = max(1, self.number_counter - 1)
                                    self.figures.pop(cell)

        pygame.quit()
