from datetime import datetime
from tkinter import *

from orjson import orjson
from tkcalendar import DateEntry
from tkinter import filedialog
from tkinter.ttk import Combobox
import matplotlib.pyplot as plt
from PIL import Image, ImageTk


class Resize(Frame):

    def __init__(self, master, image_path):
        Frame.__init__(self, master)
        self.image = Image.open(image_path)
        self.img_copy = self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=BOTH,
                             expand=YES)

        self.background.bind('<Configure>', self.resize_background)

    def resize_background(self, event):
        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background.configure(image=self.background_image)


def load_file():
    global file_name
    file_name = filedialog.askopenfilename(filetypes=[("JSON file", "*.json")])
    set_dates_to_entries(file_name)


def set_dates_to_entries(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = orjson.loads(file.read())
    dates = []

    for key, value in data.items():
        date_obj = datetime.strptime(value["Date"], "%Y-%m-%d %H:%M:%S")
        dates.append(date_obj)

    dates.sort()

    first = dates[0]
    first = datetime(first.year, first.month, first.day)
    last = dates[-1]
    last = datetime(last.year, last.month, last.day)

    date_from.set_date(first)
    date_to.set_date(last)


def analyze(sensors, start_date, end_date, average, measurement, graph_type):
    global file_name
    start_date = datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime(end_date.year, end_date.month, end_date.day)

    end_by_measurement = {
        "Температура": "temp",
        "Влажность": "humidity",
        "Давление": "pressure",
        "Освещенность": "lux",
        "Цветовая температура": "tempct",
        "Температура воздуха за окном": "soilt"
    }

    with open(file_name, "r", encoding="utf-8") as file:
        data = orjson.loads(file.read())

    sensor_data = {}

    for key, value in data.items():
        name = value['uName']
        serial = value['serial']
        if name == 'Hydra-L1' and serial == '01':
            name = 'Hydra-L1(1)'
        elif name == 'Hydra-L1' and serial == '02':
            name = 'Hydra-L1(2)'
        if name == 'Hydra-L' and serial == '01':
            name = 'Hydra-L(1)'
        if name == 'Hydra-L' and serial == '02':
            name = 'Hydra-L(2)'
        if name == 'Hydra-L' and serial == '03':
            name = 'Hydra-L(3)'
        if name == 'Hydra-L' and serial == '04':
            name = 'Hydra-L(4)'
        if name == 'Hydra-L' and serial == '05':
            name = 'Hydra-L(5)'
        if name == 'Hydra-L' and serial == '06':
            name = 'Hydra-L(6)'
        if name == 'Hydra-L' and serial == '07':
            name = 'Hydra-L(7)'
        if name == 'Hydra-L' and serial == '08':
            name = 'Hydra-L(8)'

        dates = []
        date_str = value['Date']
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        dates.append(date_obj)


        valid = True
        if average == "По дням":
            date_obj_key = datetime(date_obj.year, date_obj.month, date_obj.day)
        elif average == "По часам":
            date_obj_key = datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour)
        elif average == "По 3 часам":
            date_obj_key = datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour)
            if date_obj.hour not in list(range(0, 24, 3)):
                valid = False
        elif average == "Данные как есть":
            date_obj_key = datetime(date_obj.year, date_obj.month, date_obj.day, date_obj.hour, date_obj.minute,
                                    date_obj.second)

        if (start_date.day <= date_obj.day <= end_date.day) and name in sensors and valid:
            if name not in sensor_data:
                sensor_data[name] = {}

            if date_obj_key not in sensor_data[name] and average != "Данные как есть":
                sensor_data[name][date_obj_key] = []

            for measure_key, measure_value in value['data'].items():
                if measure_key.lower().endswith(end_by_measurement[measurement]):
                    if measure_value != "":
                        measure = float(measure_value)
                    else:
                        measure = 0
                    if average != "Данные как есть":
                        sensor_data[name][date_obj_key].append(measure)
                    else:
                        sensor_data[name][date_obj_key] = measure
                        break

    plt.figure(figsize=(18, 9))

    if average != "Данные как есть":
        average_measures = {}
        for key, value in sensor_data.items():
            for key_date, list_values in value.items():
                if len(list_values) != 0:
                    average_measures[key_date] = sum(list_values) / len(list_values)

            dates = sorted(average_measures.keys())
            avg_measures = [average_measures[key] for key in dates]


            if graph_type == "Линейный":
                plt.plot(dates, avg_measures,label=key)
            elif graph_type == "Столбчатый":
                plt.bar(dates, avg_measures,label=key)
            elif graph_type == "Точечная диаграмма":
                plt.scatter(dates, avg_measures,label=key)
        plt.legend()

    else:

        for key, value in sensor_data.items():
            average_measures = sensor_data[key].copy()
            dates = sorted(average_measures.keys())
            avg_measures = [average_measures[key] for key in dates]

            if graph_type == "Линейный":
                plt.plot(dates, avg_measures, label=key)
            elif graph_type == "Столбчатый":
                plt.bar(dates, avg_measures, label=key)
            elif graph_type == "Точечная диаграмма":
                plt.scatter(dates, avg_measures, label=key)
        plt.legend()

    plt.xlabel("Даты")
    plt.ylabel(measurement)

    plt.grid(True)

    plt.xticks(rotation=45)
    plt.savefig("graphic")

    see_result_btn.pack()




def open_result():
    global image1
    tk1 = Toplevel()
    tk1.geometry("1800x900")
    e = Resize(tk1, "graphic.png")
    e.pack(fill=BOTH, expand=YES)
    tk1.mainloop()


def build_graph():
    see_result_btn.pack_forget()

    sensors_inds = sensors_listbox.curselection()
    sensors = [sensors_listbox.get(i) for i in sensors_inds]
    start_date = date_from.get_date()
    end_date = date_to.get_date()
    average = averaging_comb.get()
    value = values_comb.get()
    graph_type = graph_types_comb.get()
    analyze(sensors, start_date, end_date, average, value, graph_type)


def update_sensors(event):
    temps_list = ['Паскаль', 'Hydra-L(1)', 'Hydra-L(2)', 'Hydra-L(3)', 'Hydra-L(4)', 'Hydra-L(5)', 'Hydra-L(6)',
                  'Hydra-L(7)', 'Hydra-L(8)', 'Опорный барометр', 'Hydra-L1(1)', 'Hydra-L1(2)', 'Тест Студии',
                  'РОСА К-2', 'Роса-К-1', 'Сервер K3edu']
    pressure_list = ['Паскаль', 'Hydra-L(1)', 'Hydra-L(2)', 'Hydra-L(3)', 'Hydra-L(4)', 'Hydra-L(5)', 'Hydra-L(6)',
                     'Hydra-L(7)', 'Hydra-L(8)', 'Опорный барометр', 'Hydra-L1(1)', 'Hydra-L1(2)', 'Тест Студии',
                     'РОСА К-2', 'Роса-К-1']
    humidity_list = ['Hydra-L(1)', 'Hydra-L(2)', 'Hydra-L(3)', 'Hydra-L(4)', 'Hydra-L(5)', 'Hydra-L(6)', 'Hydra-L(7)',
                     'Hydra-L(8)', 'Hydra-L1(1)', 'Hydra-L1(2)', 'Тест Студии', 'РОСА К-2', 'Роса-К-1']
    lux_list = ['Тест Студии', 'РОСА К-2', 'Роса-К-1']
    temp_ct_list = ['Тест Студии', 'РОСА К-2', 'Роса-К-1']
    soil_t_list = ['РОСА К-2', 'Роса-К-1']

    current_selection = sensors_listbox.curselection()
    current_values = [sensors_listbox.get(i) for i in current_selection]

    value = values_comb.get()
    if value == "Температура":
        var = Variable(value=temps_list)
    elif value == "Влажность":
        var = Variable(value=humidity_list)
    elif value == "Давление":
        var = Variable(value=pressure_list)
    elif value == "Освещенность":
        var = Variable(value=lux_list)
    elif value == "Цветовая температура":
        var = Variable(value=temp_ct_list)
    elif value == "Температура воздуха за окном":
        var = Variable(value=soil_t_list)

    sensors_listbox.config(listvariable=var)

    for i, item in enumerate(sensors_listbox.get(0, END)):
        if item in current_values:
            sensors_listbox.select_set(i)

wind = Tk()
wind.geometry("500x700")
wind.protocol("WM_DELETE_WINDOW", wind.destroy)

load_file_btn1 = Button(text='Загрузить файл', font=("Arial", 15), command=load_file)
load_file_btn1.pack(pady=8)

Label(text="Выберите величину анализа", font=("Arial", 12)).pack()
values = ['Температура', "Влажность", "Давление", "Освещенность", "Цветовая температура",
          "Температура воздуха за окном"]

image1 = None
file_name = None
values_comb = Combobox(values=values)
values_comb.current(0)
values_comb.pack(pady=8)
values_comb.bind("<<ComboboxSelected>>", update_sensors)

Label(text="Выберите осреднение", font=("Arial", 12)).pack()
averaging = ["По часам", "По дням", "По 3 часам", "Данные как есть"]
averaging_comb = Combobox(values=averaging)
averaging_comb.current(0)
averaging_comb.pack(pady=8)

Label(text="Выберите дату начала", font=("Arial", 12)).pack()
date_from = DateEntry()
date_from.pack(pady=8)

Label(text="Выберите дату конца", font=("Arial", 12)).pack()
date_to = DateEntry()
date_to.pack(pady=8)

Label(text="Выберите тип графика", font=("Arial", 12)).pack()
graph_types = ["Линейный", "Столбчатый", "Точечная диаграмма"]
graph_types_comb = Combobox(values=graph_types)
graph_types_comb.current(0)
graph_types_comb.pack(pady=8)


Label(text="Выберите датчики", font=("Arial", 12)).pack()
sensors_listbox = Listbox(selectmode=EXTENDED)
sensors_listbox.pack(pady=8)


analyze_btn = Button(text='Построить график', command=build_graph)
analyze_btn.pack(pady=8)

see_result_btn = Button(text='Увидеть график', font=("Arial", 15), command=open_result)

wind.mainloop()