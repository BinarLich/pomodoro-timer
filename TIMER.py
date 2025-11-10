import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox as mb

# pip install keyboard
# sends PLAY/PAUSE media to system API, may ask root
from keyboard import send as send_to_system_api
from pygame import mixer

# TO DO:

# Добавить кнопку настроек, внутрь них:
# 1. настройки тем: темная светлая
# 2. Настройка пути к файлам .mp3
# 3.1 отдельная галочка для воспроизводить ли звук
# 3.2 отдельная галочка для отсылать ли play в system api
# 4. Перенести все entry в настройки с ползунками
# Сделать автоматическое считывание из Entry при изменении, не по Reset.
# entry.bind("<FocusOut>", lambda e: print("После редак:", entry.get()))
# 4.1 Sound оставить в главном окошке
# 5 Сделать отдельные reset кнопки одна для циклов другая для в целом настроек на дефолт
# 6. Галочку для паузы между фазами до подтверждения старта пользователем
# 7. сохранять и парсить .json для настроек, а не .txt

# Добавить кнопки перехода на следующую фазу и предыдущую,

# Изменить отображение количества пройденных циклов (добавить)

# Почистить код хехе

# Собрать в .exe с иконкой


class MyGUI:
    def __init__(self):

        self.WIDTH = 336  # 289
        self.HEIGHT = 255  # 255
        self.PADXY = 5  # в пикселях
        self.PADXY_s = 2
        self.PADXY_ss = 0  # в info - между минутами и статусом
        self.ENTRY_WIDTH = 5  # в символах
        self.FONT_STATUS = ("Times", "24", "bold")
        self.FONT_MINS = ("Times", "32", "bold")
        self.PADX_STATUS_LABEL = 0
        self.PADY_STATUS_LABEL = 0
        self.COLOR_REST = "#3BBF77"
        self.COLOR_PAUSE = "#808080"
        self.COLOR_WORK = "#3B77BC"
        self.MINUT = 60
        self.PATH_TO_CHECK_PATHFILE = "path.txt"

        self.path_to_work = "Work.mp3"  # дефолтные пути
        self.path_to_rest = "Rest.mp3"
        self.sound_enabled = True

        self.sound_api_enabled = True
        self.pause_between_phases_needed = False  # False отключить паузу между фазами

        self.buttons_dict = {
            "End-pause": lambda: self.pause_between_phases_toggle(),
            "Media": lambda: self.sound_api_enabler(),
            "↺ Reset": lambda: self.__reset(),
            "♫ Sound": lambda: self.sound_enabler(),
            "Exit": lambda: (mixer.quit(), self.main_window.destroy()),
        }
        self.STATUS_TITLE = {
            "pause": "⏸PAUSE",
            "focus": "▶FOCUS",
            "rest": "REST",
        }

        self.labels_settings_list = [
            "Focus:",
            "Small chill:",
            "Big chill:",
            "Cycles:",
        ]
        # default minutes values
        self.list_with_min_values = [
            25,  # focus/work
            5,  # small chill
            30,  # big chill
            4,  # циклы
        ]

        # отслеживание в каком статусе поток 1 = rest, 2 = work,
        # 3 = pause from rest, 4 = pause from work (+ 4=start)
        self.__process_status = 4
        self.__seconds_till_next_phase = self.MINUT * self.list_with_min_values[0]
        self.__cycle = 0

        # инициализировать миксер для проигрывания локальных медиафайлов
        mixer.init()

        # Оформить окошко
        self.main_window = tk.Tk()
        self.main_window.title("Timer by @BinarLich")
        try:
            self.main_window.iconphoto(True, tk.PhotoImage(file="icons\\icon.png"))
        except Exception:
            print("not found icon.png")

        # отслеживание статуса
        self.__init_info()

        # Поля с настройками и всё к ним
        self.__init_settings()

        # кнопки старт, пауза, сброс, выход
        self.__init_butt()

        self.update_status()

        self.process_path()

        if not os.path.exists(self.PATH_TO_CHECK_PATHFILE):
            self.sound_enabled = False
            self.__butts[3].config(relief=tk.RAISED)

        tk.mainloop()

    # дисплей с текущим статусом
    def __init_info(self):
        """initialize info widgets"""
        # что сейчас за процесс ОТДЫХ/ФОКУС/ПАУЗА при отдыхе
        # мейн фон зеленый при работе синий при паузе серый
        # в эту же рамку сколько минут/секунд до следующего процесса
        # (ОТДЫХ/ФОКУС)
        # для статуса
        self.frame_info_status = tk.Frame(self.main_window)
        self.frame_info_status.pack(padx=self.PADXY, pady=self.PADXY_ss)

        self.__output_status = tk.StringVar()
        self.__output_status_label = tk.Label(
            self.frame_info_status,
            textvariable=self.__output_status,
            font=self.FONT_STATUS,  # type: ignore
        )
        self.__output_status_label.pack(
            side="top",
            padx=self.PADX_STATUS_LABEL,
            pady=self.PADY_STATUS_LABEL,
        )

        # для минут
        self.frame_info_minutes = tk.Frame(self.main_window)
        self.frame_info_minutes.pack(padx=self.PADXY, pady=self.PADXY_ss)

        self.label_mins_1 = tk.Label(
            self.frame_info_minutes, text="Until the end of current phase is:"
        )

        self.__label_mins_output = tk.StringVar()
        self.__label_mins_output_label = tk.Label(
            self.frame_info_minutes,
            textvariable=self.__label_mins_output,
            font=self.FONT_MINS,  # type: ignore
        )

        self.label_mins_1.pack(side="top")
        self.__label_mins_output_label.pack(side="top")

    # виджеты для настроек таймера
    def __init_settings(self):
        """initializes settings widgets"""
        # окна с текущей конфигурацией сколько минут отдых/фокус
        # c возможностью задать время
        # какой цикл из скольки и сколько минут отдых после них
        self.frame_set_n_info = tk.Frame(self.main_window)
        self.frame_set_n_info.pack(padx=self.PADXY, pady=self.PADXY)
        self.frame_settings_labels = []
        self.label_settings = []
        self.__entry_settings = []

        self.label_settings_description = tk.Label(
            self.frame_set_n_info,
            text="Hit reset to specify amount of minutes for phases:",
        )
        self.label_settings_description.pack(side="top", padx=self.PADXY)

        for i in range(4):
            self.frame_settings_labels.append(tk.Frame(self.frame_set_n_info))
            self.frame_settings_labels[i].pack(side="left", padx=self.PADXY, pady=self.PADXY)
            self.label_settings.append(
                tk.Label(
                    self.frame_settings_labels[i],
                    text=self.labels_settings_list[i],
                )
            )
            self.label_settings[i].pack(padx=self.PADXY)
            self.__entry_settings.append(
                tk.Entry(
                    self.frame_settings_labels[i],
                    width=self.ENTRY_WIDTH,
                    justify=tk.RIGHT,
                )
            )
            self.__entry_settings[i].insert(0, self.list_with_min_values[i])
            self.__entry_settings[i].pack(padx=(self.PADXY))

        self.bind_play_pause_to_frames()

    # Инит кнопок
    def __init_butt(self):
        """Buttons initialization."""
        self.__butts = []

        self.__frame_butt = tk.Frame(self.main_window)

        # кнопки pause play не нужны
        items = list(self.buttons_dict.items())
        for k, v in items:
            butt = tk.Button(self.__frame_butt, text=k, command=v)
            butt.pack(side="left", padx=self.PADXY, pady=self.PADXY)
            self.__butts.append(butt)

        self.__frame_butt.pack()

        if self.pause_between_phases_needed:
            self.__butts[0].config(relief=tk.SUNKEN)
        if self.sound_api_enabled:
            self.__butts[1].config(relief=tk.SUNKEN)
        if self.sound_enabled:
            self.__butts[3].config(relief=tk.SUNKEN)

    def bind_play_pause_to_frames(self):
        """Create tag for children frames of __init_info"""
        tag = "frames_for_info"
        frames_to_tag = self.frame_info_minutes, self.frame_info_status

        def add_tag_to_children(w):
            tags = tuple(t for t in w.bindtags() if t != tag)
            w.bindtags((tag,) + tags)
            for child in w.winfo_children():
                add_tag_to_children(child)

        for frame in frames_to_tag:
            add_tag_to_children(frame)
            frame.bind_class(tag, "<Button-1>", self.choose_pause_or_play)

    def choose_pause_or_play(self, event):
        if getattr(self, "_handling_click", False):
            return
        self._handling_click = True
        try:
            if self.__process_status in (3, 4):
                self.__start()
            elif self.__process_status in (1, 2):
                self.__pause()
        finally:
            self._handling_click = False

    def send_play_to_sys_api(self):
        pass

    def __start(self):
        """entry in execution flow, logic of flow"""
        try:
            if self.sound_api_enabled:
                send_to_system_api("play/pause media")
            mixer.music.unpause()
        except Exception as err:
            print(f"in __start mixer or sys_api err:\n{err}")
        # self.__process_status отслеживание в каком статусе поток 1= rest,
        # 2= work, 3=pause from rest, 4= pause from work (+4=start)
        if self.__process_status == 3:
            self.__process_status = 1
            if self.sound_enabled and not mixer.music.get_busy():
                self.play_audio(self.path_to_rest)
            self.schedule_tick()
        elif self.__process_status == 4:
            self.__process_status = 2
            if self.sound_enabled and not mixer.music.get_busy():
                self.play_audio(self.path_to_work)
            self.schedule_tick()

    def count_till_next_phase(self):
        """counts for seconds + moves phases"""
        if self.__seconds_till_next_phase > 0:
            self.__seconds_till_next_phase -= 1
            self.schedule_tick()
        else:
            if self.__process_status == 1:
                self.__process_status = 2
                self.__seconds_till_next_phase = int(self.list_with_min_values[0] * self.MINUT)
                if self.sound_enabled:
                    self.play_audio(self.path_to_work)
                self.schedule_tick()
            elif self.__process_status == 2:
                self.__process_status = 1
                self.__cycle += 1
                self.__seconds_till_next_phase = int(self.list_with_min_values[1] * self.MINUT)
                if self.sound_enabled:
                    self.play_audio(self.path_to_rest)
                self.schedule_tick()

            if self.__cycle >= self.list_with_min_values[3]:
                try:
                    self.main_window.after_cancel(self.id_to_cancel)
                except AttributeError:
                    pass
                self.__cycle = 0
                self.__seconds_till_next_phase = int(self.list_with_min_values[2] * self.MINUT)
                self.schedule_tick()

            if self.sound_api_enabled:
                send_to_system_api("play/pause media")

            if self.pause_between_phases_needed:
                self.__pause()

    def schedule_tick(self):
        """tick creator"""
        self.update_status()
        self.id_to_cancel = self.main_window.after(1000, self.count_till_next_phase)

    def update_status(self):
        """updates status info"""
        minutes, seconds = divmod(self.__seconds_till_next_phase, self.MINUT)
        self.__label_mins_output.set(f"{minutes}:{seconds:02d}")

        if self.__process_status == 3 or self.__process_status == 4:  # "PAUSE"
            self.__output_status.set(self.STATUS_TITLE["pause"])
            self.frame_info_status["bg"] = self.COLOR_PAUSE
            self.frame_info_minutes["bg"] = self.COLOR_PAUSE
            # self.__output_status_label["bg"] = self.COLOR_PAUSE
        elif self.__process_status == 2:  # WORK
            self.__output_status.set(self.STATUS_TITLE["focus"])
            self.frame_info_status["bg"] = self.COLOR_WORK
            self.frame_info_minutes["bg"] = self.COLOR_WORK
            # self.__output_status_label["bg"] = self.COLOR_WORK
        elif self.__process_status == 1:  # REST
            self.__output_status.set(self.STATUS_TITLE["rest"])
            self.frame_info_status["bg"] = self.COLOR_REST
            self.frame_info_minutes["bg"] = self.COLOR_REST
            # self.__output_status_label["bg"] = self.COLOR_REST

    def __reset(self):
        """Resets flow and updates to specified by user
        values via entry widgets.
        """
        try:
            self.main_window.after_cancel(self.id_to_cancel)
            if mixer.music.get_busy():  # не потокобезопасен отключить если что
                mixer.music.stop()
        except AttributeError:
            pass
        try:
            for i in range(4):
                self.list_with_min_values[i] = float(self.__entry_settings[i].get())  # type: ignore
        except ValueError:
            mb.showerror("Error", "You must use float values in input fields!")

        # отслеживание в каком статусе поток 1= rest, 2= work,
        # 3=pause from rest, 4= pause from work (+4=start)
        self.__process_status = 4
        self.__seconds_till_next_phase = int(self.MINUT * self.list_with_min_values[0])
        self.__cycle = 0

        self.process_path()

        self.update_status()

    def __pause(self):
        """pauses countdown"""
        try:
            if self.sound_api_enabled:
                send_to_system_api("play/pause media")
            self.main_window.after_cancel(self.id_to_cancel)
            mixer.music.unpause()
            if mixer.music.get_busy():  # не потокобезопасен отключить если что
                mixer.music.pause()
        except Exception as err:
            print("Error in __pause\n", err)
        if self.__process_status == 1:
            self.__process_status = 3
        elif self.__process_status == 2:
            self.__process_status = 4
        self.update_status()

    # Функция для воспроизведения файла
    # системным плеером с открытием окна (не используется)
    def play_audio_old(self, file_path):
        platform = sys.platform
        if platform == "win32":
            os.system(f'start "" "{file_path}"')
        elif platform == "darwin":  # macOS
            os.system(f'open "{file_path}"')
        else:  # Linux
            os.system(f'mpg123 "{file_path}"')

    def sound_enabler(self):
        """enables/disables sound"""
        if self.sound_enabled:
            self.sound_enabled = False
            self.__butts[3].config(relief=tk.RAISED)
            if mixer.music.get_busy():  # не потокобезопасен отключить если что
                mixer.music.stop()
        else:
            self.sound_enabled = True
            self.__butts[3].config(relief=tk.SUNKEN)

    def sound_api_enabler(self):
        """enables/disables system multimedia signals"""
        if self.sound_api_enabled:
            self.sound_api_enabled = False
            self.__butts[1].config(relief=tk.RAISED)
        else:
            self.sound_api_enabled = True
            self.__butts[1].config(relief=tk.SUNKEN)

    def pause_between_phases_toggle(self):
        """enables/disables pause between phases"""
        if self.pause_between_phases_needed:
            self.pause_between_phases_needed = False
            self.__butts[0].config(relief=tk.RAISED)
        else:
            self.pause_between_phases_needed = True
            self.__butts[0].config(relief=tk.SUNKEN)

    # Другая функция для воспроизведения,
    # без диалогового окна но с зависимостью от pygame
    def play_audio(self, file_path):
        """Planning audio player"""
        if not self.sound_enabled:
            print("Audio is off.")
            return
        elif not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            # mb.showerror("Error",f"Audio file not found at: {file_path}")
            return

        try:
            self.in_thread = threading.Thread(
                target=self.play_audio_thread,
                args=(
                    file_path,
                    lambda erro: print("Audio thread error.\n", str(erro)),
                ),
                daemon=True,
            )
            # Добавить ли полноценную колбэк функцию, а не lambda?
            # mb.showerror("Error", "Error with sound-player.\n"+str(err))
            self.in_thread.start()
        except RuntimeError:
            print("Thread to play sound can't be created")
            mb.showerror("Error", "Thread to play sound can't be created")
        except Exception as err:
            print(err)
            mb.showerror("Error", "Error with sound-player.\n" + str(err))

    def play_audio_thread(self, file_path, err_func=None):
        """To be done by thread, plays audio"""
        try:
            mixer.music.load(file_path)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as err:
            if err_func:
                self.main_window.after(0, err_func, err)

    def process_path(self):  # переписать, абсолютные пути не используются уже
        """Processing path to needed form"""
        if not os.path.exists(self.PATH_TO_CHECK_PATHFILE) or not self.sound_enabled:
            return
        paths = []
        try:
            self.file = open("path.txt", "r")
            for line in self.file:
                line = line.strip()
                if not line.startswith("#") and line:
                    if not os.path.isabs(line):
                        line = os.path.abspath(line)
                        paths.append(line)
                    else:
                        paths.append(line)
            if len(paths) == 2:

                self.path_to_rest = os.path.normpath(paths[0])
                self.path_to_work = os.path.normpath(paths[1])

            else:
                mb.showerror("Error", "You have more paths than two.")

        except Exception as err:
            mb.showerror("Error", "Error with path-reader\n" + str(err))
        else:
            print("Path read successfully.", self.path_to_rest, self.path_to_work)
        finally:
            self.file.close()


class SettingsMyGUI:
    pass


if __name__ == "__main__":
    mygui = MyGUI()
