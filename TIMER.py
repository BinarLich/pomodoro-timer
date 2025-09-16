import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox as mb
from pygame import mixer

# Добавить настройки пути внутрь GUI
# Изменить обображение количества пройденных циклов (добавить)


class MyGUI:
    def __init__(self):

        self.WIDTH = 336  # 289
        self.HEIGHT = 255  # 255
        self.PADXY = 5  # в пикселях
        self.PADXY_s = 2
        self.ENTRY_WIDTH = 5  # в символах
        self.FONT_STATUS = ("Times", "24", "bold")
        self.FONT_MINS = ("Times", "32", "bold")
        self.COLOR_REST = "#3BBF77"
        self.COLOR_PAUSE = "#808080"
        self.COLOR_WORK = "#3B77BC"
        self.MINUT = 60
        self.PATH_TO_CHECK_PATHFILE = "path.txt"

        self.path_to_work = "Work.mp3"  # дефолтные пути
        self.path_to_rest = "Rest.mp3"
        self.sound_enabled = True
        # инициализация логики

        self.buttons_dict = {
            "Start": lambda: self.__start(),
            "Pause": lambda: self.__pause(),
            "Reset": lambda: self.__reset(),
            "Sound": lambda: self.sound_enabler(),
            "Exit": lambda: (self.main_window.destroy(), mixer.quit()),
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

        # self.threads_pool=ThreadPoolExecutor(max_workers=3)
        # отслеживание в каком статусе поток 1= rest, 2= work,
        # 3=pause from rest, 4= pause from work (+ 4=start)
        self.__process_status = 4
        self.__seconds_till_next_phase = (
            self.MINUT * self.list_with_min_values[0]
        )
        self.__cycle = 0

        mixer.init()  # инициализировать миксер для проигрывания

        # Оформить окошко
        self.main_window = tk.Tk()
        self.main_window.title("Timer by @BinarLich")
        try:
            self.main_window.iconphoto(
                True, tk.PhotoImage(file="icons\\icon.png")
            )
        except Exception:
            print("not found icon.png")

        # отслеживание статуса
        self.__init_info()

        # Поля с настройками и всё к ним
        self.__init_settings()

        # 5) кнопки старт, пауза, сброс, выход
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
        # что сейчас за процесс ОТДЫХ/РАБОТА/ПАУЗА при отдыхе
        # мейн фон зеленый при работе синий при паузе серый
        # в эту же рамку сколько минут/секунд до следующего процесса
        # (ОТДЫХ/РАБОТА)
        # для статуса
        self.frame_info_status = tk.Frame(self.main_window)
        self.frame_info_status.pack(padx=self.PADXY, pady=self.PADXY)

        self.__output_status = tk.StringVar()
        self.__output_status_label = tk.Label(
            self.frame_info_status,
            textvariable=self.__output_status,
            font=self.FONT_STATUS,  # type: ignore
        )
        self.__output_status_label.pack(side="top")

        # для минут
        self.frame_info_minutes = tk.Frame(self.main_window)
        self.frame_info_minutes.pack(padx=self.PADXY, pady=self.PADXY)

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
        # окна с текущей конфигурацией сколько минут отдых/работа
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
            self.frame_settings_labels[i].pack(
                side="left", padx=self.PADXY, pady=self.PADXY
            )
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

    # Инит кнопок
    def __init_butt(self):
        """Buttons initialization."""
        self.__butts = []

        self.__frame_butt = tk.Frame(self.main_window)

        for k, v in self.buttons_dict.items():
            butt = tk.Button(self.__frame_butt, text=k, command=v)
            butt.pack(side="left", padx=self.PADXY, pady=self.PADXY)
            self.__butts.append(butt)
        self.__butts[3].config(relief=tk.SUNKEN)

        self.__frame_butt.pack()

    def __start(self):
        """entry in execution flow, logic of flow"""
        try:
            mixer.music.unpause()
        except Exception:
            print("in __start mixer err")

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
                self.__seconds_till_next_phase = int(
                    self.list_with_min_values[0] * self.MINUT
                )
                if self.sound_enabled:
                    self.play_audio(self.path_to_work)
                self.schedule_tick()
            elif self.__process_status == 2:
                self.__process_status = 1
                self.__cycle += 1
                self.__seconds_till_next_phase = int(
                    self.list_with_min_values[1] * self.MINUT
                )
                if self.sound_enabled:
                    self.play_audio(self.path_to_rest)
                self.schedule_tick()

            if self.__cycle >= self.list_with_min_values[3]:
                try:
                    self.main_window.after_cancel(self.id_to_cancel)
                except AttributeError:
                    pass
                self.__cycle = 0
                self.__seconds_till_next_phase = int(
                    self.list_with_min_values[2] * self.MINUT
                )
                self.schedule_tick()

    def schedule_tick(self):
        """tick creator"""
        self.update_status()
        self.id_to_cancel = self.main_window.after(
            1000, self.count_till_next_phase
        )

    def update_status(self):
        """updates status info"""
        minutes, seconds = divmod(self.__seconds_till_next_phase, self.MINUT)
        self.__label_mins_output.set(f"{minutes}:{seconds:02d}")

        if self.__process_status == 3 or self.__process_status == 4:  # "PAUSE"
            self.__output_status.set("PAUSE")
            self.frame_info_status["bg"] = self.COLOR_PAUSE
            self.frame_info_minutes["bg"] = self.COLOR_PAUSE
        elif self.__process_status == 2:  # WORK
            self.__output_status.set("WORK")
            self.frame_info_status["bg"] = self.COLOR_WORK
            self.frame_info_minutes["bg"] = self.COLOR_WORK
        elif self.__process_status == 1:  # REST
            self.__output_status.set("REST")
            self.frame_info_status["bg"] = self.COLOR_REST
            self.frame_info_minutes["bg"] = self.COLOR_REST

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
                self.list_with_min_values[i] = float(  # type: ignore
                    self.__entry_settings[i].get()
                )
        except ValueError:
            mb.showerror("Error", "You must use float values in input fields!")

        # отслеживание в каком статусе поток 1= rest, 2= work,
        # 3=pause from rest, 4= pause from work (+4=start)
        self.__process_status = 4
        self.__seconds_till_next_phase = int(
            self.MINUT * self.list_with_min_values[0]
        )
        self.__cycle = 0

        self.process_path()

        self.update_status()

    def __pause(self):
        """pauses countdown"""
        try:
            self.main_window.after_cancel(self.id_to_cancel)
            mixer.music.unpause()
            if mixer.music.get_busy():  # не потокобезопасен отключить если что
                mixer.music.pause()
        except Exception as err:
            print("Error in __pause", err)
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

    def process_path(self):
        """Processing path to needed form"""
        if (
            not os.path.exists(self.PATH_TO_CHECK_PATHFILE)
            or not self.sound_enabled
        ):
            return
        paths = []
        try:
            self.file = open("path.txt", "r")
            for line in self.file:
                line = line.strip()
                if not line.startswith("#") and line:
                    # у playsound какие-то проблемы с относительными путями
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
            print(
                "Path read successfully.", self.path_to_rest, self.path_to_work
            )
        finally:
            self.file.close()


if __name__ == "__main__":
    mygui = MyGUI()
