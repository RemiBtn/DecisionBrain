from datetime import datetime
import matplotlib.pyplot as plt
import random as rd


class Colors:
    """For printing colored text"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NORMAL = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_time(time):
    """Parse time from string into datetime object"""
    if not time:
        return
    if type(time) == str:
        return datetime.strptime(time, '%I:%M%p')
    return time


def parse_time_minute(time):
    """
    Parse time from datetime object into minutes

    :param time: datetime object representing the time
    :return: the number of minutes elapsed since midnight
    """
    if not time:
        return
    return int((parse_time(time) - datetime(year=1901, month=1, day=1, hour=0)).seconds / 60)


def store_result(target_path, employees, tasks, lunch_times, z, b):
    w, t = len(tasks), len(employees)
    with open(target_path, "w") as f:
        f.write("taskId;performed;employeeName;startTime; \n")
        for i in tasks:
            if i in z.keys():
                f.write(f"T{i - t + 1};1;{employees[z[i]].name};{b[i].x};\n")
            else:
                f.write(f"T{i - t + 1};0;;;\n")
        f.write("\n")
        f.write("employeeName;lunchBreakStartTime;\n")
        for k in range(t):
            f.write(f"{employees[k].name};{lunch_times[k]};\n")
    return

def store_result_V3(target_path, employees, tasks, lunch_times, z, b):
    w, t = len(tasks), len(employees)
    with open(target_path, "w") as f:
        f.write("taskId;performed;employeeName;startTime; \n")
        for i in tasks:
            if i in z.keys():
                f.write(f"T{i -t + 1};1;{employees[z[i]].name};{b[i]};\n")
            else:
                f.write(f"T{i - t + 1};0;;;\n")
        f.write("\n")
        f.write("employeeName;lunchBreakStartTime;\n")
        for k in range(t):
            f.write(f"{employees[k].name};{lunch_times[k]};\n")
    return


def cm_to_inch(value):
    return value / 2.54


def plot_map(employee_list, node_list, tasks, unavails, X, L, Z):
    plt.figure(figsize=(cm_to_inch(100), cm_to_inch(100)))

    number_of_colors = 8  # hardcoded
    color = ["#" + ''.join([rd.choice('0123456789ABCDEF') for _ in range(6)])
             for _ in range(number_of_colors)]

    node_pos = []
    for k in range(len(employee_list)):
        node_pos.append([employee_list[k].longitude, employee_list[k].latitude])
        plt.scatter([employee_list[k].longitude], [employee_list[k].latitude], label=f"Maison de {employee_list[k].name}", c=color(k),
                    marker="$(H)$", s=10000)

    t = len(employee_list)
    all_indexes = list(range(t)) + tasks + unavails

    for k in range(t):
        for i in all_indexes:
            if L[(k, i)].x == 1:
                employee = employee_list[k]
                node = node_list[i]
                plt.scatter([node.longitude], [node.latitude], label=f"Pause de {employee.name}", marker="$(P)$",
                            s=10000)

    for i in tasks:
        if i in Z.keys():
            task = node_list[i]
            node_pos.append([task.longitude, task.latitude])
            plt.scatter([task.longitude], [task.latitude],
                        marker=f"$({task.id})$",c = color[Z[i]] ,s=10000)
        else:
            task = node_list[i]
            node_pos.append([task.longitude, task.latitude])
            plt.scatter([task.longitude], [task.latitude],
                         marker=f"$({task.id})$",s=10000)

    for i in unavails:
        unavail = node_list[i]
        node_pos.append([unavail.longitude, unavail.latitude])
        plt.scatter([unavail.longitude], [unavail.latitude], label="Indisponibilité de " + unavail.employee.name,
                    marker="$(X)$", c = color[unavail.employee.index_of()], s=10000)

def plot_map_V3(employee_list, node_list, tasks, unavails, X, Z):
    plt.figure(figsize=(cm_to_inch(100), cm_to_inch(100)))

    number_of_colors = len(employee_list)  # hardcoded
    color = ["#" + ''.join([rd.choice('0123456789ABCDEF') for _ in range(6)])
             for _ in range(number_of_colors)]

    node_pos = []
    for k in range(len(employee_list)):
        node_pos.append([employee_list[k].longitude, employee_list[k].latitude])
        plt.scatter([employee_list[k].longitude], [employee_list[k].latitude], label=f"Maison de {employee_list[k].name}", c=color[k],
                    marker="$(H)$", s=10000)

    t = len(employee_list)
    all_indexes = list(range(t)) + tasks + unavails

    for i in tasks:
        if i in Z.keys():
            task = node_list[i]
            node_pos.append([task.longitude, task.latitude])
            plt.scatter([task.longitude], [task.latitude]
                        , marker=f"$({task.id})$",c = color[Z[i]] ,s=10000)
        else:
            task = node_list[i]
            node_pos.append([task.longitude, task.latitude])
            plt.scatter([task.longitude], [task.latitude],
                         marker=f"$({task.id})$",c = "grey", s=10000)

    for i in unavails:
        unavail = node_list[i]
        node_pos.append([unavail.longitude, unavail.latitude])
        plt.scatter([unavail.longitude], [unavail.latitude], label="Indisponibilité de " + unavail.employee.name,
                    marker="$(X)$", c = color[unavail.employee.index_of()], s=10000)

    
    n = len(node_pos)
    for a in range(n):
        for b in range(n):
            i = all_indexes[a]
            j = all_indexes[b]
            if i != j and (i, j) in list(X.keys()):
                lbl = ""
                clr = "black"
                if i in range(t):
                    lbl = f"{employee_list[Z[j]].name}"
                    clr = color[Z[i]]
                elif j in range(t):
                    clr = color[Z[j]]
                else:
                    clr = color[Z[i]]

                plt.plot([node_pos[a][0], node_pos[b][0]], [
                         node_pos[a][1], node_pos[b][1]], c=clr, label=lbl)

    plt.legend(prop={'size': 40}, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()


def time_format(min):
    return f"{int(min//60)}:{int(min%60)}"


def plot_agenda(employee_list, node_list, tasks, unavails, B, Z, lunch_times):
    N = len(employee_list)

    plan = [[] for i in range(N)]

    for t in tasks:
        if t in Z.keys():
            plan[Z[t]].append((B[t].x, f"tâche {t-N+1}"))
            plan[Z[t]].append((B[t].x+node_list[t].duration, f"tâche {t-N+1}"))
    for k in range(N):
        plan[k].append((lunch_times[k], f"pause déjeuner"))
        plan[k].append((lunch_times[k]+60, f"pause déjeuner"))
    for u in unavails:
        plan[Z[u]].append((B[u].x, f"indisponibilité"))
        plan[Z[u]].append((B[u].x+node_list[u].duration, f"indisponibilité"))

    column_labels = [[] for i in range(N)]
    for k in range(N):
        column_labels[k].append("horaires")
        column_labels[k].append(f"{employee_list[k].name}")

    for k in range(N):
        plan[k].sort(key=lambda x: x[0])

        chose = []
        for i in range(0, len(plan[k])-1, 2):
            chose.append(
                [f"{time_format(plan[k][i][0])} - {time_format(plan[k][i+1][0])}", plan[k][i][1]])
        plan[k] = chose

    left, width = 0.1, 2.0
    bottom, height = 0.1, 0.8

    for k in range(N):
        plt.figure(k+1)

        Table = [left + width/N*k, bottom, width/N - 0.1, height]

        Ax = plt.axes(Table, frameon=False)
        Ax.axis('tight')
        Ax.axis('off')
        Ax.table(cellText=plan[k], colLabels=column_labels[k])

    plt.show()

def plot_agenda_V3(employee_list, node_list, tasks, unavails, B, Z, lunch_times):
    N = len(employee_list)

    plan = [[] for i in range(N)]

    for t in tasks:
        if t in Z.keys():
            plan[Z[t]].append((B[t], B[t]+node_list[t].duration, f"tâche {t-N+1}"))
    for k in range(N):
        plan[k].append((lunch_times[k], lunch_times[k]+60, f"pause déjeuner"))
    for u in unavails:
        plan[Z[u]].append((B[u], B[u]+node_list[u].duration, f"indisponibilité"))

    column_labels = [[] for i in range(N)]
    for k in range(N):
        column_labels[k].append("horaires")
        column_labels[k].append(f"{employee_list[k].name}")

    for k in range(N):
        plan[k].sort(key=lambda x: x[0])

        chose = []
        for i in range(len(plan[k])):
            chose.append(
                [f"{time_format(plan[k][i][0])} - {time_format(plan[k][i][1])}", plan[k][i][2]])
        plan[k] = chose

    left, width = 0.1, 0.5
    bottom, height = 0.1, 2

    for k in range(N):
        plt.figure(k+1)

        Table = [left, bottom, width, height]

        Ax = plt.axes(Table, frameon=False)
        Ax.axis('tight')
        Ax.axis('off')
        Ax.table(cellText=plan[k], colLabels=column_labels[k])

    plt.show()