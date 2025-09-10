import os
import sys
import threading
import playsound
import tkinter as tk
from tkinter import messagebox as mb

class MyGUI():
    def __init__(self):
        
        self.WIDTH=336 #289 
        self.HEIGHT=255 #255
        self.PADXY=5 # в пикселях
        self.PADXY_s=2 
        self.ENTRY_WIDTH = 5 #в символах
        self.FONT_STATUS=("Times","24","bold")
        self.FONT_MINS=("Times","32","bold")
        self.COLOR_REST="#3BBF77"
        self.COLOR_PAUSE="#808080"
        self.COLOR_WORK="#3B77BC"
        self.MINUT = 60
        self.PATH_TO_CHECK_PATHFILE="path.txt"
        
        self.path_to_work = "Work.mp3" #дефолтные пути
        self.path_to_rest = "Rest.mp3"
        self.def_min_work=25
        self.def_min_rest=5
        self.def_min_big_rest=30
        self.def_amount_cycles=4
        
        
        #Оформить окошко
        self.main_window=tk.Tk()
        self.main_window.title("Timer by @BinarLich")
        try:
            self.main_window.iconphoto(True, tk.PhotoImage(file="icon.png"))
        except Exception:
            print("not found icon.png")
        #self.main_window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        
        #инициализация логики
        self.__process_status=4 #отслеживание в каком статусе поток 1= rest, 2= work, 3=pause from rest, 4= pause from work (+ 4=start)
        self.__seconds_till_next_phase=self.MINUT*self.def_min_work
        self.__cycle=0
        
        #отслеживание статуса
        self.__init_info()
                        
        #Поля с настройками и всё к ним
        self.__init_settings()
        
        #5) кнопки старт, пауза, сброс, выход
        self.__init_butt()
        
        self.update_status()
        
        self.process_path()

        tk.mainloop()
    
    #дисплей с текущим статусом 
    def __init_info(self):
        '''initialize info widgets'''
        #что сейчас за процесс ОТДЫХ/РАБОТА/ПАУЗА при отдыхе
        #мейн фон зеленый при работе синий при паузе серый
        #в эту же рамку сколько минут/секунд до следующего процесса (ОТДЫХ/РАБОТА)
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
              
        self.__label_mins_output=tk.StringVar()
        self.__label_mins_output_label=tk.Label(self.frame_info_minutes,textvariable=self.__label_mins_output,font=self.FONT_MINS)
        
        self.label_mins_1.pack(side="top")
        self.__label_mins_output_label.pack(side="top")
        
    #виджеты для настроек таймера
    def __init_settings(self):
        '''initializes settings widgets'''
        #окна с текущей конфигурацией сколько минут отдых/работа c возможностью задать время
        #какой цикл из скольки и сколько минут отдых после них
        self.frame_set_n_info=tk.Frame(self.main_window)
        self.frame_set_n_info.pack(padx=self.PADXY,pady=self.PADXY)
        self.frame_settings_labels=[]

        self.label_settings_description=tk.Label(self.frame_set_n_info,text="Hit reset to specify amount of minutes for phases:")
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
        self.__entry_settings_mins_work.insert(0,self.def_min_work)
        self.__entry_settings_mins_chill=tk.Entry(self.frame_settings_labels[1],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_chill.insert(0,self.def_min_rest)
        self.__entry_settings_mins_big_chill=tk.Entry(self.frame_settings_labels[2],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_big_chill.insert(0,self.def_min_big_rest)
        self.__entry_settings_mins_cycle_amount=tk.Entry(self.frame_settings_labels[3],width=self.ENTRY_WIDTH,justify=tk.RIGHT)
        self.__entry_settings_mins_cycle_amount.insert(0,self.def_amount_cycles)
        
        self.__entry_settings_mins_work.pack(padx=(self.PADXY))
        self.__entry_settings_mins_chill.pack(padx=(self.PADXY))
        self.__entry_settings_mins_cycle_amount.pack(padx=(self.PADXY))
        self.__entry_settings_mins_big_chill.pack(padx=(self.PADXY))

    #Инит кнопок
    def __init_butt(self):
        '''Buttons initialization.'''
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
        '''entry in execution flow, logic of flow'''
        #self.main_window.update_idletasks()
        #print(self.main_window.winfo_width()) 
        #print(self.main_window.winfo_height()) 
        #self.__process_status отслеживание в каком статусе поток 1= rest, 2= work, 3=pause from rest, 4= pause from work (+4=start)
        if self.__process_status==3:
            self.__process_status=1
            self.play_audio(self.path_to_rest)
            self.schedule_tick()
        elif self.__process_status==4:
            self.__process_status=2
            self.play_audio(self.path_to_work)
            self.schedule_tick()
        else:
            if self.__process_status==1: 
                self.__seconds_till_next_phase=int(self.def_min_rest*self.MINUT)
                self.play_audio(self.path_to_rest)
                self.schedule_tick()
            elif self.__process_status==2:
                self.__seconds_till_next_phase=int(self.def_min_work*self.MINUT)
                self.play_audio(self.path_to_work)
                self.schedule_tick()
                
        if self.__cycle>=self.def_amount_cycles:
            try:
                self.main_window.after_cancel(self.id_to_cancel)
            except AttributeError:
                pass
            self.__cycle=0
            self.__seconds_till_next_phase=int(self.def_min_big_rest*self.MINUT)
            self.schedule_tick()
        
    def count_till_next_phase(self):
        '''counts for seconds + moves phases'''
        if self.__seconds_till_next_phase>0:
            self.__seconds_till_next_phase-=1
            self.schedule_tick()
        else:
            if self.__process_status==1:
                self.__process_status=2
            elif self.__process_status==2:
                self.__process_status=1
                self.__cycle+=1
            self.__start()

    def schedule_tick(self):
        '''tick creator'''
        self.update_status()
        self.id_to_cancel=self.main_window.after(1000,self.count_till_next_phase)
    
    def update_status(self):
        '''updates status info'''
        minutes, seconds =divmod(self.__seconds_till_next_phase,self.MINUT)
        self.__label_mins_output.set(f"{minutes}:{seconds:02d}")

        if self.__process_status==3 or self.__process_status==4: #"PAUSE"
            self.__output_status.set("PAUSE")
            self.frame_info_status["bg"]=self.COLOR_PAUSE
            self.frame_info_minutes["bg"]=self.COLOR_PAUSE
        elif self.__process_status==2: #WORK
            self.__output_status.set("WORK")
            self.frame_info_status["bg"]=self.COLOR_WORK
            self.frame_info_minutes["bg"]=self.COLOR_WORK
        elif self.__process_status==1: #REST
            self.__output_status.set("REST")
            self.frame_info_status["bg"]=self.COLOR_REST
            self.frame_info_minutes["bg"]=self.COLOR_REST
        
    def __reset(self):
        '''resets flow and updates to specified by user values via entry widgets'''
        try:
            self.main_window.after_cancel(self.id_to_cancel)
        except AttributeError:
            pass
        try:
            self.def_min_work=float(self.__entry_settings_mins_work.get())
            self.def_min_rest=float(self.__entry_settings_mins_chill.get())
            self.def_min_big_rest=float(self.__entry_settings_mins_big_chill.get())
            self.def_amount_cycles=int(self.__entry_settings_mins_cycle_amount.get())
        except ValueError:
            mb.showerror("Error","You must use float values in input fields!\nIn cycle amount entry should be integer value!")
        
        self.__process_status=4 #отслеживание в каком статусе поток 1= rest, 2= work, 3=pause from rest, 4= pause from work (+4=start)
        self.__seconds_till_next_phase=int(self.MINUT*self.def_min_work)
        self.__cycle=0
        
        self.process_path()
        
        self.update_status()

    def __pause(self):
        '''pauses countdown'''
        try:
            self.main_window.after_cancel(self.id_to_cancel)
        except AttributeError:
            pass
        if self.__process_status==1:
            self.__process_status=3
        elif self.__process_status==2:
            self.__process_status=4
        self.update_status()
        
    # Функция для воспроизведения файла системным плеером с открытием окна (не используется)
    def play_audio_old(self,file_path):
        platform= sys.platform
        if platform == "win32":
            os.system(f'start "" "{file_path}"')
        elif platform == "darwin":  # macOS
            os.system(f'open "{file_path}"')
        else:  # Linux
            os.system(f'mpg123 "{file_path}"')
            
    # Другая функция для воспроизведения, без диалогового окна но с зависимостью от playsound
    def play_audio(self,file_path):
        try:
            self.in_thread=threading.Thread(target=playsound.playsound, args=(file_path,)) 
            self.in_thread.start()
        except RuntimeError:
            print("Thread to play sound can't be created")
            mb.showerror("Error", "Thread to play sound can't be created")
        except (FileNotFoundError, UnicodeDecodeError) as err:
            print(f"File not found at this path: {file_path}")
            print("Or pathway contains characters that cant be decoded right.")
            mb.showerror(f"Error","File not found at this path: {file_path}."+
                         "\nOr pathway contains characters that cant be decoded right."+
                         "\n"+err)
        except Exception as err:
            print(err)
            mb.showerror("Error", "Error with sound-player.\n"+err)
            
    def process_path(self):
        if not os.path.exists(self.PATH_TO_CHECK_PATHFILE):
            return
        paths=[]
        try:
            self.file=open("path.txt","r")
            for line in self.file:
                line=line.strip()
                if not line.startswith("#") and line:
                    paths.append(line)
            if len(paths)==2:
                self.path_to_rest=os.path.normpath(paths[0])
                self.path_to_work=os.path.normpath(paths[1])
            else:
                mb.showerror("Error", "You have more paths than two.")
                                        
        except Exception as err:
            mb.showerror("Error", "Error with path-reader\n"+err)
        else:
            print("Path read successfully.",paths)
        finally:
            self.file.close()
        
if __name__=="__main__":
    mygui=MyGUI()