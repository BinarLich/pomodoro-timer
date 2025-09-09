import time
import os
import sys

# Укажите пути к вашим MP3 файлам
FILE1 = "Work.mp3"
FILE2 = "Rest.mp3"
MINUT = 60
COUNTER_TO = 4

# Функция для очистки консоли
def clear_screen():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

# Функция для воспроизведения файла
def play_audio(file_path):
    if sys.platform == "win32":
        os.system(f'start "" "{file_path}"')
    elif sys.platform == "darwin":  # macOS
        os.system(f'open "{file_path}"')
    else:  # Linux
        os.system(f'mpg123 "{file_path}"')

# Основной цикл
# 25 min = 1500
# 30 min = 1800
# 5 min = 300
cycles = 0
while True:
    play_audio(FILE1)
    for i in range(1500, 0, -10):
        clear_screen()
        print(f"Перерыв через: {i//MINUT} минут, {i%MINUT}секунд")
        time.sleep(10)
    cycles += 1
    
    play_audio(FILE2)
    if cycles < COUNTER_TO:
        for i in range(300, 0, -10):
            clear_screen()
            print(f"СЕЙЧАС ОТДЫХ!!!\nПродолжить через: {i//MINUT} минут, {i%MINUT}секунд")
            time.sleep(10)
    else:
        for i in range(1800, 0, -10):
            clear_screen()
            print(f"СЕЙЧАС БОЛЬШОЙ ОТДЫХ!!!\nПродолжить через: {i//MINUT} минут, {i%MINUT}секунд")
            time.sleep(10)