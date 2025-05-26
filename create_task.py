import pygame
import json
import sqlite3
import os

# Настройки
CELL_SIZE = 65
MARGIN = 50
GRID_SIZE = 8
SCREEN_WIDTH = CELL_SIZE * GRID_SIZE + 2 * MARGIN
SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 2 * MARGIN + 140

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Шахматные заграждения")
font = pygame.font.SysFont(None, 24)

# Стены
walls = {}

# DB
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        walls TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_to_db(name="Без названия"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    walls_json = json.dumps(list(walls.keys()))
    cursor.execute("INSERT INTO tasks (name, walls) VALUES (?, ?)", (name, walls_json))
    conn.commit()
    conn.close()
    print('Task added to database')

def load_latest_from_db():
    global walls
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT walls FROM tasks ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        loaded = json.loads(result[0])
        walls = {tuple(w): True for w in loaded}

# Графика
def draw_grid():
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, (0, 0, 0),
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE * CELL_SIZE))
        pygame.draw.line(screen, (0, 0, 0),
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + GRID_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE))

def draw_walls():
    for (x1, y1, x2, y2) in walls:
        if x1 == x2:
            x = MARGIN + x1 * CELL_SIZE
            y1 = MARGIN + y1 * CELL_SIZE
            y2 = MARGIN + y2 * CELL_SIZE
            pygame.draw.line(screen, (255, 0, 0), (x, y1), (x, y2), 5)
        elif y1 == y2:
            y = MARGIN + y1 * CELL_SIZE
            x1 = MARGIN + x1 * CELL_SIZE
            x2 = MARGIN + x2 * CELL_SIZE
            pygame.draw.line(screen, (255, 0, 0), (x1, y), (x2, y), 5)

def get_line(pos):
    x, y = pos
    x -= MARGIN
    y -= MARGIN
    if x < 0 or y < 0 or x > GRID_SIZE * CELL_SIZE or y > GRID_SIZE * CELL_SIZE:
        return None
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    dx = x % CELL_SIZE
    dy = y % CELL_SIZE
    if dx < 10 and col > 0:
        return (col, row, col, row + 1)
    if dx > CELL_SIZE - 10 and col < GRID_SIZE:
        return (col + 1, row, col + 1, row + 1)
    if dy < 10 and row > 0:
        return (col, row, col + 1, row)
    if dy > CELL_SIZE - 10 and row < GRID_SIZE:
        return (col, row + 1, col + 1, row + 1)
    return None

def draw_ui():
    buttons = {
        "reset": pygame.Rect(50, SCREEN_HEIGHT - 80, 120, 40),
        "save_file": pygame.Rect(200, SCREEN_HEIGHT - 80, 120, 40),
        "save_db": pygame.Rect(350, SCREEN_HEIGHT - 80, 140, 40),
        "load_db": pygame.Rect(510, SCREEN_HEIGHT - 80, 140, 40)
    }

    pygame.draw.rect(screen, (180, 180, 180), buttons["reset"])
    pygame.draw.rect(screen, (180, 180, 180), buttons["save_file"])
    pygame.draw.rect(screen, (180, 180, 180), buttons["save_db"])
    pygame.draw.rect(screen, (180, 180, 180), buttons["load_db"])

    screen.blit(font.render("Сброс", True, (0, 0, 0)), (85, SCREEN_HEIGHT - 68))
    screen.blit(font.render("Сохранить файл", True, (0, 0, 0)), (210, SCREEN_HEIGHT - 68))
    screen.blit(font.render("Сохранить в БД", True, (0, 0, 0)), (360, SCREEN_HEIGHT - 68))
    screen.blit(font.render("Загрузить из БД", True, (0, 0, 0)), (520, SCREEN_HEIGHT - 68))

    tips = [
        "ЛКМ — поставить стену",
        "ПКМ — удалить стену",
        "Сброс — очистка поля",
        "Сохранить — записать в файл или БД"
    ]
    for i, tip in enumerate(tips):
        screen.blit(font.render(tip, True, (0, 0, 255)), (50, SCREEN_HEIGHT - 120 + i * 20))

    return buttons

# Сохранение в файл (опционально)
def save_to_file():
    with open("walls_state.pkl", "wb") as f:
        import pickle
        pickle.dump(walls, f)

# Основной цикл
def main():
    init_db()
    running = True
    while running:
        screen.fill((255, 255, 255))
        draw_grid()
        draw_walls()
        buttons = draw_ui()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["reset"].collidepoint(event.pos):
                    walls.clear()
                elif buttons["save_file"].collidepoint(event.pos):
                    save_to_file()
                elif buttons["save_db"].collidepoint(event.pos):
                    save_to_db("Новая задача")
                elif buttons["load_db"].collidepoint(event.pos):
                    load_latest_from_db()
                else:
                    line = get_line(event.pos)
                    if line:
                        if event.button == 1:
                            walls[line] = True
                        elif event.button == 3:
                            walls.pop(line, None)

    pygame.quit()

if __name__ == "__main__":
    main()
