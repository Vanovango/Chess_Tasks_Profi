import pygame
import json
import sqlite3


class CreateTaskForm:
    def __init__(self, task_id=None, theme=None, name=None, complexity=None, walls=None):
        complexity_variants = {
            'Легко': (110, 50, 6),
            'Средне': (90, 50, 8),
            'Сложно': (70, 50, 10),
            'Невозможно': (45, 50, 16)
        }

        self.task_id = task_id
        self.theme = theme
        self.name = name
        self.complexity = complexity
        self.walls = walls or {}

        self.CELL_SIZE, self.MARGIN, self.GRID_SIZE = complexity_variants[complexity]
        self.SCREEN_WIDTH = self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.GRID_SIZE + 2 * self.MARGIN + 140
        self.DB_FILE = "database.db"

        pygame.init()

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        if self.task_id is None:
            pygame.display.set_caption("Новая задача")
        else:
            pygame.display.set_caption(f"Редактирование: {self.name}")

        self.font = pygame.font.SysFont(None, 24)
        self.buttons = {}

    def save_to_db(self):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        walls_json = json.dumps(list(self.walls.keys()))
        cursor.execute("INSERT INTO tasks (theme, name, complexity, walls) VALUES (?, ?, ?, ?)",
                       (self.theme, self.name, self.complexity, walls_json))
        conn.commit()
        conn.close()
        print('Task added to database')

    def change_data(self):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        walls_json = json.dumps(list(self.walls.keys()))
        cursor.execute("UPDATE tasks SET walls = ? WHERE id = ?", (walls_json, self.task_id))
        conn.commit()
        conn.close()
        print('Task updated in database')

    def delete_from_db(self):
        conn = sqlite3.connect(self.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (self.task_id,))
        conn.commit()
        conn.close()
        print("Task deleted from database")

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
            return (col, row, col, row + 1)
        if dx > self.CELL_SIZE - 10 and col < self.GRID_SIZE:
            return (col + 1, row, col + 1, row + 1)
        if dy < 10 and row > 0:
            return (col, row, col + 1, row)
        if dy > self.CELL_SIZE - 10 and row < self.GRID_SIZE:
            return (col, row + 1, col + 1, row + 1)
        return None

    def draw_ui(self):
        self.buttons = {
            "reset": pygame.Rect(50, self.SCREEN_HEIGHT - 80, 120, 40),
            "save_db": pygame.Rect(200, self.SCREEN_HEIGHT - 80, 140, 40),
        }

        if self.task_id is not None:
            self.buttons["delete_task"] = pygame.Rect(370, self.SCREEN_HEIGHT - 80, 160, 40)

        for key, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (180, 180, 180), rect)

        self.screen.blit(self.font.render("Сброс", True, (0, 0, 0)),
                         (85, self.SCREEN_HEIGHT - 68))
        self.screen.blit(self.font.render("Сохранить", True, (0, 0, 0)),
                         (230, self.SCREEN_HEIGHT - 68))

        if self.task_id is not None:
            self.screen.blit(self.font.render("Удалить задачу", True, (0, 0, 0)),
                             (390, self.SCREEN_HEIGHT - 68))

        tips = [
            "ЛКМ — поставить стену",
            "ПКМ — удалить стену",
            "Сброс — очистка поля",
        ]
        for i, tip in enumerate(tips):
            self.screen.blit(self.font.render(tip, True, (0, 0, 255)),
                             (self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 100 + i * 20))

    def run(self):
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_walls()
            self.draw_ui()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.buttons["reset"].collidepoint(event.pos):
                        self.walls.clear()
                    elif self.buttons["save_db"].collidepoint(event.pos):
                        if self.task_id is None:
                            self.save_to_db()
                        else:
                            self.change_data()
                        running = False
                    elif "delete_task" in self.buttons and self.buttons["delete_task"].collidepoint(event.pos):
                        self.delete_from_db()
                        running = False
                    else:
                        line = self.get_line(event.pos)
                        if line:
                            if event.button == 1:
                                self.walls[line] = True
                            elif event.button == 3:
                                self.walls.pop(line, None)

        pygame.quit()


# Обёртка для запуска с PyQt5
class CreateTaskFormWrapper:
    def __init__(self, task_id, theme, name, complexity, walls):
        self.form = CreateTaskForm(task_id, theme, name, complexity, walls)

    def run(self):
        self.form.run()
