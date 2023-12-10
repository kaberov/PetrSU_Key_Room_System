from tkinter import *
import requests
import ast
from datetime import datetime, timedelta
from get_staff import get_staff
import re
import tktabl
from get_stress import get_stress


# updates time
def update_time():
    global now
    now = datetime.now()
    time_label['text'] = now.strftime("%H:%M")
    for y in keys_info:
        if not keys_info[y]['free'] and keys_info[y]['end_time'] < now:
            update_specific_cell(y)
            if y == chosen_key:
                update_deb()

    root.after(1000, update_time)


# reshape data to array of documents
def reshape(e_data, t=1):
    columns = []
    for b in range(t):
        columns.append(e_data[b])
    count = 0
    d = {}
    lol = []
    for item in e_data:
        if count % t == 0:
            lol.append(d)
            d = {}
        d[columns[count % t]] = item
        count += 1
    if d != {}:
        lol.append(d)
    lol.pop(0)
    lol.pop(0)
    return lol


def click(event):
    try:
        cell = table.find_cell(event)
        global chosen_key
        if cell.get_value() != '':
            chosen_key = int(cell.get_value())
            update_deb()
    except:
        pass


def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def set_binds_canvas(event):
    frame4.bind_all('<Button-1>', click)
    frame4.bind_all("<MouseWheel>", on_mousewheel)


def unset_binds_canvas(event):
    frame4.unbind_all("<Button 1>")
    frame4.unbind_all("<MouseWheel>")


# get schedule what right now
def get_schedule_now(arr):
    min_answer = {'end_time': '24:01'}
    max_answer = {'end_time': '00:-01'}
    delimiters = r':|;|,|\.'

    for item in arr:
        if int(now.strftime("%H")) * 60 + int(now.strftime("%M")) <= \
                int(re.split(delimiters, item['end_time'])[0]) * 60 + int(re.split(delimiters, item['end_time'])[1]) \
                <= int(re.split(delimiters, min_answer['end_time'])[0]) * 60 + \
                int(re.split(delimiters, min_answer['end_time'])[1]):
            min_answer = item

        if int(re.split(delimiters, item['end_time'])[0]) * 60 + int(re.split(delimiters, item['end_time'])[1]) >= \
                int(re.split(delimiters, max_answer['end_time'])[0]) * 60 + \
                int(re.split(delimiters, max_answer['end_time'])[1]):
            max_answer = item

    if min_answer == {'end_time': '24:01'}:
        return max_answer

    return min_answer


# Update the listbox
def update(data):
    # Clear the listbox
    my_list.delete(0, END)

    # Add lectures to listbox
    for item in data:
        my_list.insert(END, item)


# Update the listbox of deb keys
def update_deb():
    # Clear the listbox
    deb_list.delete(0, END)

    # deb_list.itemconfig(END, fg='#ADFF2F')
    deb_list.insert(END, 'Аудитория ' + str(chosen_key), )
    deb_list.itemconfig(END, bg='gray')
    deb_list.insert(END, 'тут пишиться информация про кобинет', )
    deb_list.itemconfig(END, bg='#ADFF2F')
    deb_list.insert(END, 'разными цветами')
    deb_list.itemconfig(END, bg='#EEEE44')
    deb_list.insert(END, 'Свободно' if keys_info[chosen_key]['free'] is True else 'Занято и ' + (
        'просроченно' if keys_info[chosen_key]['end_time'] < now else 'не просроченно'))
    deb_list.itemconfig(END, bg='#FA8072')


# Update the entry with listbox clicked
def fill_out(e):
    # Clear the entry
    my_entry.delete(0, END)

    # Add clicked list item to entry box
    my_entry.insert(0, my_list.get(ANCHOR))

    # Update schedules and info for one lecture
    update_lecture_info(my_list.get(ANCHOR))


# Create function to check entry
def check(e):
    # grab what was typed
    typed = my_entry.get()

    if typed == '':
        data = lectures
    else:
        data = []
        for item in lectures:
            if typed.lower() in item.lower():
                data.append(item)

    # update our listbox with selected items
    update(data)


# Update our label schedules of one lecture
def update_lecture_info(name):
    stress_button['state'] = DISABLED

    info_label['text'] = name
    schedules_label['text'] = 'placeholder'

    if name in staff:
        for item in [staff[name]['job title'], staff[name]['academic degree'], staff[name]['job title']]:
            if item is not None:
                info_label['text'] += '; ' + item

    if name not in lectures_schedule:
        schedules_label['text'] = 'Расписание не найдено'
        return

    stress_button['state'] = NORMAL

    item = requests.get('https://petrsu.egipti.com/api/v2/lecturer?name=' + name)
    item.encoding = 'utf-8'
    global rego_data
    rego_data = ast.literal_eval(item.text)
    schedules = rego_data[week][weekday]
    item.close()

    # remove all distance learning
    schedules = [res for res in schedules if not (res['classroom'] == '')]

    if len(schedules) == 0:
        schedules_label['text'] = 'Занятий нет'
        return

    schedules = get_schedule_now(schedules)

    schedules_label['text'] = 'Номер: ' + schedules['number'] + '\n' + 'Название: ' + schedules['title'] + '\n' + \
                              'Начало: ' + schedules['start_time'] + '\n' + 'Конец: ' + schedules['end_time'] + '\n' + \
                              'Тип: ' + schedules['type'] + '\n' + 'Кабинет: ' + schedules['classroom']

    return


def update_chosen_cell():
    cell = table.get_cell(int((keys_id_in_table[chosen_key]) / 6), (keys_id_in_table[chosen_key]) % 6)
    cell.config(readonlybackground=colors[
        3 if cell.get_value() == '' else int(not keys_info[chosen_key]['free']) * (
                int(keys_info[chosen_key]['end_time'] < now) + 1)])


def update_specific_cell(key):
    cell = table.get_cell(int((keys_id_in_table[key]) / 6), (keys_id_in_table[key]) % 6)
    cell.config(readonlybackground=colors[
        3 if cell.get_value() == '' else int(not keys_info[key]['free']) * (
                int(keys_info[key]['end_time'] < now) + 1)])


# function to set an issuance flag true
def issuance_key():
    keys_info[chosen_key]['free'] = False
    keys_info[chosen_key]['end_time'] = now + delta
    update_deb()
    update_chosen_cell()


# function to open a return window on a button click
def return_key():
    keys_info[chosen_key]['free'] = True
    keys_info[chosen_key]['end_time'] = datetime.max
    update_deb()
    update_chosen_cell()


def issuance_return_key():
    keys_info[chosen_key]['free'] = not keys_info[chosen_key]['free']
    update_deb()
    update_chosen_cell()


# function to open a consultation window on a button click
def open_consultation_window():
    # Toplevel object which will be treated as a new window
    consultation_window = Toplevel(root)

    # object will be dominant
    consultation_window.grab_set()

    # sets the title of the Toplevel widget
    consultation_window.title("Консультация")

    # sets the geometry of toplevel
    consultation_window.geometry("200x200")

    # sets the icon of main root window
    # consultation_window.iconbitmap('key.ico')

    # A Label widget to show in toplevel
    Label(consultation_window, text="This is a new window").pack()


# Get staff
# staff = get_staff(skip_flag=True)
staff = get_staff(skip_flag=False)

# Get the list of lectures
page = requests.get('https://petrsu.egipti.com/api/v2/lecturers')
page.encoding = 'utf-8'
lectures_schedule = ast.literal_eval(page.text)
# Combine two lists of lectures without duplicates
lectures = lectures_schedule + list(set(staff.keys()) - set(lectures_schedule))
page.close()
lectures.sort()

# Get week numerator
page = requests.get('https://petrsu.egipti.com/api/v2/week')
page.encoding = 'utf-8'
week = ast.literal_eval(page.text)['week']
page.close()

# Get current datetime
now = datetime.now()

# For testing purposes
delta = timedelta(seconds=10)

# Get day of week as an integer
weekday = now.weekday()

# Array of days of week
weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

rego_data = []

# creates a Tk() object
root = Tk()
# sets the title of main root window
root.title("Курсовая работа")
# sets the icon of main root window
# root.iconbitmap('key.ico')
# sets the geometry of main root window
root.geometry("800x600")

frame1 = Frame(root)

# Create an entry box
my_entry = Entry(frame1, width=50)
my_entry.grid(pady=10)

# Create a list box
my_list = Listbox(frame1, width=50)
my_list.grid(pady=10)

frame1.grid(column=0, pady=10, padx=10)

# Add the lectures to our list
update(lectures)

frame2 = Frame(root)

# Create label for time
time_label = Label(frame2, text=now.strftime("%H:%M"), width=50, bg='#fff')
time_label.grid(pady=5)

# Create label for info of lecture
info_label = Label(frame2, text='Преподователь ещё не выбран', width=50, bg='#fff')
info_label.grid(pady=5)

# Create label for week numerator
numerator_label = Label(frame2, text='Числитель' if week == 'numerator' else 'Знаменатель', width=50, bg='#fff')
numerator_label.grid(pady=5)

# Create label for day of week
weekday_label = Label(frame2, text=weekdays[weekday], width=50, bg='#fff')
weekday_label.grid(pady=5)

# Create label for schedules
schedules_label = Label(frame2, text='', width=50, bg='#fff')
schedules_label.grid(pady=5)

# Create a binding on the listbox onclick
my_list.bind("<<ListboxSelect>>", fill_out)

# Create a binding on the entry box
my_entry.bind("<KeyRelease>", check)


def why_button_does_not_work_without_this():
    get_stress(root, rego_data)


stress_button = Button(frame2, text='Нагрузка преподавателя',
                       command=why_button_does_not_work_without_this,
                       state=DISABLED)
stress_button.grid(pady=5)

frame2.grid(column=0, row=1, pady=10, padx=10)

frame3 = Frame(root)

# Create a list box fo deb keys
deb_list = Listbox(frame3, width=60)
deb_list.configure(background="#F0F0ED")
deb_list.grid(pady=5, column=0, row=0, columnspan=3)

deb_list.insert(END, 'Ключ не выбран', )

# a button widget which will open a new window on button click
issuance_button = Button(frame3, text='Выдать ключ', command=issuance_key)
issuance_button.grid(pady=5, column=0, row=1, padx=2.5)

# a button widget which will open a new window on button click
return_button = Button(frame3, text='Сдать ключ', command=return_key)
return_button.grid(pady=5, column=1, row=1, padx=2.5)

# a button widget which will open a new window on button click
consultation_button = Button(frame3, text='Консультация', command=open_consultation_window)
# consultation_button = Button(frame3, text='Консультация', command=issuance_return_key)
consultation_button.grid(pady=5, column=2, row=1, padx=2.5)

frame3.grid(column=1, row=0, pady=10, padx=10, columnspan=2)

frame4 = Frame(root)

colors = ['#ADFF2F', '#EEEE44', '#FA8072', 'gray']

canvas = Canvas(frame4)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview, )

chosen_key = -1
keys_info = {}
keys_id_in_table = {}

for j in range(1, 500):
    keys_info[j] = {'free': True, 'end_time': datetime.max}
    keys_id_in_table[j] = j - 1

table = tktabl.Table(canvas, data=reshape(list(keys_info.keys()), t=6))


def update_table():
    for n in table.cells:
        n[0].config(justify=CENTER, width=9)
        n[0].config(readonlybackground=colors[
            3 if n[0].get_value() == '' else int(not keys_info[int(n[0].get_value())]['free']) *
                                             (int(keys_info[int(n[0].get_value())]['end_time'] < now))])
        # print(i[0].get_value())


update_table()

table._master.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=table._master, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

frame4.bind("<Enter>", set_binds_canvas)
frame4.bind("<Leave>", unset_binds_canvas)

canvas.pack()

frame4.grid(column=1, row=1, pady=10, padx=10)

scrollbar.grid(column=2, row=1, sticky='ns')

update_time()

root.mainloop()
