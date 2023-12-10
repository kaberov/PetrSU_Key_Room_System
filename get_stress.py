import numpy as np
from collections import Counter
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection
from datetime import datetime
from matplotlib.ticker import MaxNLocator


def get_stress(root, data):
    consultation_window = Toplevel(root)
    consultation_window.grab_set()
    consultation_window.title("Нагрузка преподавателя")
    consultation_window.geometry("800x600")

    # рисунок 1
    # data[числитель/знаменатель][день недели][]

    clean_data = {"denominator": [], "numerator": []}

    for i in range(7):
        clean_data["denominator"].append({"numbers": {}})
        clean_data["numerator"].append({"numbers": {}})

        for item in data["denominator"][i]:
            clean_data["denominator"][i]["numbers"][item["number"]] = item["title"]

        for item in data["numerator"][i]:
            clean_data["numerator"][i]["numbers"][item["number"]] = item["title"]

    left = np.arange(7)

    labels = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

    fig1 = Figure(figsize=(4.7, 3.5), dpi=75, layout='tight')

    plot1 = fig1.add_subplot(111)

    plot1.bar(left, [len(clean_data["denominator"][i]["numbers"]) for i in range(7)],
              width=0.3, color='#FA8072', label='Знаменатель')

    plot1.bar(left + 0.15, np.zeros((7,), dtype=int), tick_label=labels,
              width=0)

    plot1.bar(left + 0.3, [len(clean_data["numerator"][i]["numbers"]) for i in range(7)],
              width=0.3, color='#4169E1', label='Числитель')

    plot1.plot(left, [len(clean_data["denominator"][i]["numbers"]) for i in range(7)],
               color='red')

    plot1.plot(left + 0.3, [len(clean_data["numerator"][i]["numbers"]) for i in range(7)],
               color='blue')

    plot1.set_title('График нагрузки преподавателя')
    plot1.yaxis.grid(linestyle='--')
    plot1.yaxis.set_major_locator(MaxNLocator(integer=True))
    plot1.set_xlabel('Дни недели')
    plot1.set_ylabel('Количество пар в день')  # , rotation=0)

    plot1.legend(loc="best")

    canvas1 = FigureCanvasTkAgg(fig1, master=consultation_window)
    canvas1.draw()

    canvas1.get_tk_widget().grid(row=0, column=0)

    # рисунок 2
    fig2 = Figure(figsize=(5.98, 3.5), dpi=75, layout='constrained')

    plot2 = fig2.add_subplot(111)

    counter = []

    for i in range(7):
        counter.extend(list(clean_data["denominator"][i]["numbers"].values()))
        counter.extend(list(clean_data["numerator"][i]["numbers"].values()))

    counter = dict(Counter(counter))

    titles = list(counter.keys())

    new_titles = []

    for item in titles:
        chunks, chunk_size = len(item), 21
        new_titles.append('\n'.join([item[i:i + chunk_size] for i in range(0, chunks, chunk_size)]))

    slices = list(counter.values())

    patches, texts, auto_suck = plot2.pie(slices, shadow=True, startangle=90, radius=1.2, autopct='%1.1f%%')

    plot2.set_title('Соотношение пар преподавателя')

    plot2.legend(patches, new_titles, loc="upper left", bbox_to_anchor=(1, 1))  # , bbox_to_anchor=(0.5, -0.25))

    canvas2 = FigureCanvasTkAgg(fig2, master=consultation_window)
    canvas2.draw()

    canvas2.get_tk_widget().grid(row=0, column=1)

    verts_denominator = []
    verts_numerator = []

    for i in range(7):
        for item in data["denominator"][i]:
            start = mdates.date2num(
                datetime.strptime(item['start_time'].replace('.', ':').replace(';', ':').replace(',', ':'), '%H:%M'))
            end = mdates.date2num(
                datetime.strptime(item['end_time'].replace('.', ':').replace(';', ':').replace(',', ':'), '%H:%M'))

            v = [(start, i - .4),
                 (start, i + .0),
                 (end, i + .0),
                 (end, i - .4),
                 (start, i - .4)]

            verts_denominator.append(v)
        for item in data["numerator"][i]:
            start = mdates.date2num(
                datetime.strptime(item['start_time'].replace('.', ':').replace(';', ':').replace(',', ':'), '%H:%M'))
            end = mdates.date2num(
                datetime.strptime(item['end_time'].replace('.', ':').replace(';', ':').replace(',', ':'), '%H:%M'))

            v = [(start, i - .0),
                 (start, i + .4),
                 (end, i + .4),
                 (end, i - .0),
                 (start, i - .0)]

            verts_numerator.append(v)

    bars_denominator = PolyCollection(verts_denominator, facecolors='red', label='Знаменатель')  # , hatch='//')
    bars_numerator = PolyCollection(verts_numerator, facecolors='blue', label='Числитель')  # , hatch='\\\\')

    fig3 = Figure(figsize=(16, 6), dpi=50, layout='tight')
    plot3 = fig3.add_subplot(111)

    plot3.add_collection(bars_denominator)
    plot3.add_collection(bars_numerator)

    plot3.autoscale()
    loc = mdates.MinuteLocator(byminute=[0, 30])
    plot3.xaxis.set_major_locator(loc)
    plot3.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))

    plot3.set_title('Расписание преподавателя')
    plot3.yaxis.grid(linestyle='--')

    plot3.set_yticks([0, 1, 2, 3, 4, 5, 6])
    plot3.set_yticklabels(['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'])

    plot3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plot3.invert_yaxis()

    plot3.legend(loc="lower right")

    canvas3 = FigureCanvasTkAgg(fig3, master=consultation_window)
    canvas3.draw()

    canvas3.get_tk_widget().grid(row=1, column=0, columnspan=3)
