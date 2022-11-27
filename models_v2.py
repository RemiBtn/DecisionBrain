# basic modules
import pandas as pd
import numpy as np
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from utils import parse_time, parse_time_minute


class Employee:
    list = []  # list of all employee instances
    count = 0  # employee count, i.e. the length of Employee.list
    speed = 50 * 1000 / 60  # unit: meter/minute
    __name_employee_correspondance = {}  # stores the correspondance between names and instances

    def __init__(self, name: str, latitude: float, longitude: float, skill: str, level: int, start_time, end_time):
        """
        Initialize an employee instance and store it to the list of employees
        :param name: name of the employee
        :param latitude: latitude of the employee's home
        :param longitude: longitude of the employee's home
        :param skill: the skill of the employee
        :param level: the level of the employee's skill
        :param start_time: the time at which the employee starts working
        :param end_time: the time at which the employee stops working
        """
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.skill = skill
        self.level = level
        self.start_time_str = parse_time(start_time)  # parse time into datetime object for printing
        self.end_time_str = parse_time(end_time)
        self.start_time = parse_time_minute(start_time)  # parse time into minutes
        self.end_time = parse_time_minute(end_time)
        self.unavails = []  # employee unavailabilities
        Employee.count += 1
        Employee.list.append(self)

    def index_of(self):
        for idx, employee in enumerate(Employee.list):
            if employee == self:
                return idx

    @classmethod
    def find_by_name(cls, name: str):
        """
        Find the instance of the employee from its name.
        :param name: name of the employee
        :return: the corresponding employee instance
        """
        for employee in cls.list:
            if employee.name == name:
                return employee

    @classmethod
    def load_excel(cls, path) -> None:
        """
        Load all employee data.
        :param path: path of the Excel file storing data about the city instance
        """

        # clear previously loaded data if any
        if cls.count:
            cls.count = 0
            cls.list = []

        # loading data into pandas dataframes
        df_employees = pd.read_excel(path, sheet_name="Employees")
        df_employees.set_index("EmployeeName")

        # instantiation of employee instances
        for index, row in df_employees.iterrows():
            Employee(row["EmployeeName"],
                     row["Latitude"],
                     row["Longitude"],
                     row["Skill"],
                     row["Level"],
                     row["WorkingStartTime"],
                     row["WorkingEndTime"])

    def home(self):
        return Employee.index_of(self)

    def __hash__(self):
        return hash(self.name)  # an employee is uniquely identified by its name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        """
        Return a string representation of the employee for debugging and displaying purposes
        :return:
        """
        return f"Employee(name={self.name}, " \
               f"position=[{self.longitude}, {self.latitude}], " \
               f"skill_requirement=level {self.level} {self.skill}," \
               f"available=[{self.start_time_str.strftime('%I:%M%p')}, {self.end_time_str.strftime('%I:%M%p')}] )"


class Node:
    list = []
    count = 0
    distance: np.array = None
    __is_initialized = False  # whether the distance matrix is initialized

    def __init__(self):
        if Node.__is_initialized:
            raise Exception("Cannot instantiate new task after initializing the distance matrix")
        Node.count += 1
        Node.list.append(self)

    @classmethod
    def clear_previous_data(cls):
        """When loading an instance, we need to clear the data of the old instance"""
        cls.list = []
        cls.count = 0
        cls.__is_initialized = False

    @staticmethod
    def calculate_distance(node1, node2):
        """
        :param node1:
        :param node2:
        :return: the distance, in meter, between node1 and node2
        """

        # the distance of a node to itself is zero
        if node1 is node2:
            return 0

        lon1, lat1 = radians(node1.longitude), radians(node1.latitude)
        lon2, lat2 = radians(node2.longitude), radians(node2.latitude)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371000  # radius of earth in meter
        return c * r

    @classmethod
    def initialize_distance(cls):
        if cls.__is_initialized:
            print("Warning: trying to reinitialize an initialized task list, recalculating the distance matrix")
        cls.__is_initialized = True
        cls.distance = np.zeros((cls.count, cls.count), dtype=np.float64)

        for i in range(cls.count):
            for j in range(i):
                node_i, node_j = cls.list[i], cls.list[j]
                cls.distance[i, j] = cls.distance[j, i] = cls.calculate_distance(node_i, node_j)

    @classmethod
    def load_excel(cls, path):
        pass


class Task(Node):
    list = []  # list of all tasks
    count = 0  # task count
    node_type = "task"

    def __init__(self, task_id, latitude, longitude, duration, skill, level, opening_time, closing_time):
        super().__init__()
        self.id = task_id
        self.latitude = latitude
        self.longitude = longitude
        self.duration = duration
        self.skill = skill
        self.level = level
        self.opening_time_str = parse_time(opening_time)  # for displaying time in __repr__
        self.closing_time_str = parse_time(closing_time)  # for displaying time in __repr__
        self.opening_time = parse_time_minute(opening_time)
        self.closing_time = parse_time_minute(closing_time)
        self.closed_intervals = []  # intervals during which tasks are unavailable

        Task.count += 1
        Task.list.append(self)

    @classmethod
    def find_by_id(cls, task_id):
        for task in Task.list:
            if task.id == task_id:
                return task
        return None

    def open_intervals(self):
        """
        Return a list of intervals for which the task is available
        """
        d, f = self.opening_time, self.closing_time
        task_duration = self.duration
        l = [d]
        for s, e in self.closed_intervals:
            l.append(s)
            l.append(e)
        l.append(f)
        return [(l[j], l[j + 1]) for j in range(0, len(l), 2) if l[j + 1] - l[j] >= task_duration]

    @classmethod
    def load_excel(cls, path: str):
        # clear previous data if any
        if cls.count:
            cls.list = []
            cls.count = 0

        # load tasks
        df = pd.read_excel(path, sheet_name="Tasks")
        df.set_index("TaskId")
        for index, row in df.iterrows():
            # parse the start time and end time into datetime object
            opening_time = datetime.strptime(row["OpeningTime"], '%I:%M%p')
            closing_time = datetime.strptime(row["ClosingTime"], '%I:%M%p')
            cls(row["TaskId"],
                row["Latitude"],
                row["Longitude"],
                row["TaskDuration"],
                row["Skill"],
                row["Level"],
                opening_time,
                closing_time)

        # load task unavailabilities
        df_unavail = pd.read_excel(path, sheet_name="Tasks Unavailabilities")
        df_unavail.set_index("TaskId")
        for _, row in df_unavail.iterrows():
            task = cls.find_by_id(row["TaskId"])
            start_closed_interval = row["Start"]
            end_closed_interval = row["End"]
            task.closed_intervals.append((parse_time_minute(start_closed_interval),
                                          parse_time_minute(end_closed_interval)))

    def __repr__(self):
        """Return string representation of task for debugging and displaying purposes"""
        if self.node_type == "task":
            return f"Task(id={self.id}, " \
                   f"position=[{self.longitude}, {self.latitude}], " \
                   f"duration={self.duration}, " \
                   f"skill_requirement=level {self.level} {self.skill}," \
                   f"opening_time=[{self.opening_time_str.strftime('%I:%M%p')}" \
                   f"to {self.closing_time_str.strftime('%I:%M%p')}] "


class Home(Node):
    list = []
    count = 0
    node_type = "home"

    def __init__(self, employee: str, latitude, longitude):
        super().__init__()
        self.employee = Employee.find_by_name(employee)
        self.latitude = latitude
        self.longitude = longitude
        Home.list.append(self)
        Home.count += 1

    @classmethod
    def load_excel(cls, path: str):
        # clear previous data if any
        if cls.count:
            cls.list = []
            cls.count = 0
        df_employees = pd.read_excel(path, sheet_name="Employees")
        df_employees.set_index("EmployeeName")
        for _, row in df_employees.iterrows():
            cls(row["EmployeeName"], row["Latitude"], row["Longitude"])

    def __repr__(self):
        return f"Home({self.employee})"


class Unavail(Node):
    list = []
    count = 0
    node_type = "unavail"

    def __init__(self, employee, latitude, longitude, opening_time, closing_time):
        super().__init__()
        self.employee = Employee.find_by_name(employee) # only for task
        self.employee.unavails.append(self) # add new unavailability of the employee instance's unavails list
        self.latitude = latitude
        self.longitude = longitude
        self.opening_time_str = parse_time(opening_time)
        self.closing_time_str = parse_time(closing_time)

        opening_time = parse_time_minute(opening_time)
        closing_time = parse_time_minute(closing_time)
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.duration = closing_time - opening_time
        Unavail.count += 1
        Unavail.list.append(self)

    @classmethod
    def load_excel(cls, path, initialize_distance=False):
        # clear previous data
        if cls.count:
            cls.list = []
            cls.count = 0
        # create a task for each unavailability at the bottom of the list
        df_employees_unavailabilities = pd.read_excel(path, sheet_name="Employees Unavailabilities")
        df_employees_unavailabilities.set_index("EmployeeName")

        for _, row in df_employees_unavailabilities.iterrows():
            open_time = row["Start"]
            close_time = row["End"]
            cls(row["EmployeeName"], row["Latitude"], row["Longitude"], open_time, close_time)

    def __repr__(self):
        return f"Unavailability({self.employee}, "\
               f"start={self.opening_time_str.strftime('%I:%M%p')}, "\
               f"end={self.closing_time_str.strftime('%I:%M%p')})"
