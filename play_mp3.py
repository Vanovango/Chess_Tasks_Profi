import sys
import os
import pygame
import threading

def play_mp3(file_path):
    if not os.path.isfile(file_path):
        print(f"[ОШИБКА] Файл не найден: {file_path}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print(f"[OK] Воспроизведение: {file_path}")
        print("Нажмите 's' + Enter для выхода.")

        while pygame.mixer.music.get_busy():
            command = input().strip().lower()
            if command == 's':
                pygame.mixer.music.stop()
                print("[INFO] Воспроизведение завершено.")
                break

    except Exception as e:
        print(f"[ОШИБКА] Не удалось воспроизвести файл: {e}")

def main():
    if len(sys.argv) < 2:
        print("Использование: play_mp3.exe путь_к_файлу.mp3")
    else:
        play_mp3(sys.argv[1])

if __name__ == "__main__":
    main()