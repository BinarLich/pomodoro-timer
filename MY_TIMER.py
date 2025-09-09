import time
import os
import sys
import tkinter as tk

# Константы
FILE1 = "Work.mp3" #дефолтные пути
FILE2 = "Rest.mp3"
MINUT = 60
COUNTER_TO = 4 #потом изменяется по желанию

# Функция для очистки консоли
def clear_screen():
    platform= sys.platform
    if platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

# Функция для воспроизведения файла системным плеером
def play_audio(file_path):
    platform= sys.platform
    if platform == "win32":
        os.system(f'start "" "{file_path}"')
    elif platform == "darwin":  # macOS
        os.system(f'open "{file_path}"')
    else:  # Linux
        os.system(f'mpg123 "{file_path}"')

# Основной цикл
# 25 min = 1500
# 30 min = 1800
# 5 min = 300
def main_loop():
    cycles = 0
    while True:
        play_audio(FILE1)
        for i in range(1500, 0, -10):
            clear_screen()
            print(f"Перерыв через: {i//MINUT} минут, {i%MINUT} секунд")
            time.sleep(10)
        cycles += 1
        
        play_audio(FILE2)
        if cycles < COUNTER_TO:
            for i in range(300, 0, -10):
                clear_screen()
                print(f"СЕЙЧАС ОТДЫХ!!!\nПродолжить через: {i//MINUT} минут, {i%MINUT} секунд")
                time.sleep(10)
        else:
            for i in range(1800, 0, -10):
                clear_screen()
                print(f"СЕЙЧАС БОЛЬШОЙ ОТДЫХ!!!\nПродолжить через: {i//MINUT} минут, {i%MINUT} секунд")
                time.sleep(10)

class MyGUI():
    def __init__(self):
        self.WIDTH=200
        self.HEIGHT=50
        self.DEF_MIN_WORK=25
        self.DEF_MIN_REST=5
        self.DEF_MIN_BIG_REST=30
        self.DEF_AMOUNT_CYCLES=4
        self.PADXY=5 # в пикселях
        self.PADXY_s=2 
        self.ENTRY_WIDTH = 5 #в символах
        self.FONT_STATUS=("Times","24","bold")
        self.FONT_MINS=("Times","32","bold")
        self.COLOR_GREEN="#00ff00"
        self.COLOR_GREY="#808080"
        self.COLOR_BLUE="#3B77BC"
        MINUT = 60
        
        #Оформить окошко в духе Win XP 
        self.main_window=tk.Tk()
        
        self.__init_info()
                        
        #Поля с настройками и всё к ним
        self.__init_settings()
        
        #5) кнопки старт, пауза, сброс, выход
        self.__init_butt()
        
        tk.mainloop()
    
    #дисплей с текущим статусом 
    def __init_info(self):
        #1) что сейчас за процесс ОТДЫХ/РАБОТА/ПАУЗА при отдыхе
        #мейн фон зеленый при работе синий при паузе серый
        #в эту же рамку сколько минут/секунд до следующего процесса (ОТДЫХ/РАБОТА)
        self.__process_status=3 #отслеживание в каком статусе поток 1= rest, 2= work, 3=pause
        
        # для статуса
        self.frame_info_status=tk.Frame(self.main_window)
        self.frame_info_status.pack(padx=self.PADXY,pady=self.PADXY)
        
        self.__output_status=tk.StringVar()
        self.__output_status_label=tk.Label(self.frame_info_status,textvariable=self.__output_status,font=self.FONT_STATUS)
        self.__output_status_label.pack(side="top")
        
        #для минут 
        self.frame_info_minutes=tk.Frame(self.main_window)
        self.frame_info_minutes.pack(padx=self.PADXY,pady=self.PADXY)
        
        self.label_mins_1 =tk.Label(self.frame_info_minutes,text="Until the end of current phase is:")
        #self.label_mins_2 =tk.Label(self.frame_info_minutes,text="minutes")
              
        self.__label_mins_output=tk.StringVar()
        self.__label_mins_output_label=tk.Label(self.frame_info_minutes,textvariable=self.__label_mins_output,font=self.FONT_MINS)
        
        self.label_mins_1.pack(side="top")
        self.__label_mins_output_label.pack(side="top")
        #self.label_mins_2.pack(side="top")
        
        
    #виджеты для настроек таймера
    def __init_settings(self):
        #2) окна с текущей конфигурацией сколько минут отдых/работа c возможностью задать время
        #3) какой цикл из скольки (сделать задаваемым) и сколько минут отдых после них
        #для 2-3, 3 рамки общую композицию, по одной для виджетов и лейблов, сверху поясняющие
        self.frame_set_n_info=tk.Frame(self.main_window)
        self.frame_set_n_info.pack(padx=self.PADXY,pady=self.PADXY)
        self.frame_settings_labels=[]

        self.label_settings_description=tk.Label(self.frame_set_n_info,text="You can specify amount of minutes for phases:")
        self.label_settings_description.pack(side="top",padx=self.PADXY)
        
        for i in range(4):
            self.frame_settings_labels.append(tk.Frame(self.frame_set_n_info))
            self.frame_settings_labels[i].pack(side="left",padx=self.PADXY,pady=self.PADXY)

        self.label_settings_mins_work=tk.Label(self.frame_settings_labels[0],text="Focus:")
        self.label_settings_mins_chill=tk.Label(self.frame_settings_labels[1],text="Small chill:")
        self.label_settings_mins_big_chill=tk.Label(self.frame_settings_labels[2],text="Big chill:")
        self.label_settings_mins_cycle_count=tk.Label(self.frame_settings_labels[3],text="Cycles:")
        
        self.label_settings_mins_work.pack(padx=self.PADXY)
        self.label_settings_mins_chill.pack(padx=self.PADXY)
        self.label_settings_mins_big_chill.pack(padx=self.PADXY)
        self.label_settings_mins_cycle_count.pack(padx=self.PADXY)
                
        self.__entry_settings_mins_work=tk.Entry(self.frame_settings_labels[0],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_work.insert(0,self.DEF_MIN_WORK)
        self.__entry_settings_mins_chill=tk.Entry(self.frame_settings_labels[1],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_chill.insert(0,self.DEF_MIN_REST)
        self.__entry_settings_mins_cycle_amount=tk.Entry(self.frame_settings_labels[2],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_cycle_amount.insert(0,self.DEF_AMOUNT_CYCLES)
        self.__entry_settings_mins_big_chill=tk.Entry(self.frame_settings_labels[3],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_big_chill.insert(0,self.DEF_MIN_BIG_REST)
        
        self.__entry_settings_mins_work.pack(padx=(self.PADXY))
        self.__entry_settings_mins_chill.pack(padx=(self.PADXY))
        self.__entry_settings_mins_cycle_amount.pack(padx=(self.PADXY))
        self.__entry_settings_mins_big_chill.pack(padx=(self.PADXY))

        #self.frame_settings_labels.pack(padx=self.PADXY)
        #self.frame_settings.pack(padx=self.PADXY,pady=self.PADXY_s)
        # в следующий раз я выберу писать это в цикле, а не "понятные" названия переменных. гавно
        

    
    #Инит кнопок
    def __init_butt(self):
        '''Buttons initialisation.'''
        self.__frame_butt=tk.Frame(self.main_window)
        
        self.__butt_start=tk.Button(self.__frame_butt,text="Start",command=self.__start)
        self.__butt_start.pack(side="left",padx=self.PADXY,pady=self.PADXY)
        
        self.__butt_pause=tk.Button(self.__frame_butt,text="Pause",command=self.__pause)
        self.__butt_pause.pack(side="left",padx=self.PADXY,pady=self.PADXY)
        
        self.__butt_reset=tk.Button(self.__frame_butt,text="Reset",command=self.__reset)
        self.__butt_reset.pack(side="left",padx=self.PADXY,pady=self.PADXY)
        
        self.__butt_exit=tk.Button(self.__frame_butt,text="Exit",command=self.main_window.destroy)
        self.__butt_exit.pack(side="left",padx=self.PADXY,pady=self.PADXY)
        
        self.__frame_butt.pack()
    
    def __start(self):
        pass
    def __reset(self):
        pass
    def __pause(self):
        pass
    def __change_colors(self):
        pass
        
if __name__=="__main__":
    #main_loop()
    mygui=MyGUI()