import time
import farmhash


# type_main：社会招聘，校园招聘
class Job:

    def __init__(
            self,
            name: str = None,
            position: str = None,
            job_id: str = None,
            bank_name: str = None,
            branch_name: str = None,
            department: str = None,
            type_main: str = None,
            type_next: str = None,
            place: str = None,
            date_publish: str = None,
            date_close: str = None,
            content: str = None,
            requirement: str = None,
            education: str = None,
            major: str = None,
            recruit_num: str = None,
            salary: str = None,
            years_work: str = None,
            url: str = None,
            create_time: str = time.strftime('%Y-%m-%d %H:%M:%S'),
            status: str = 'undo'
    ):
        self._name = name
        self._position = position
        self._job_id = job_id
        self._bank_name = bank_name
        self._branch_name = branch_name
        self._department = department
        self._type_main = type_main
        self._type_next = type_next
        self._place = place
        self._date_publish = date_publish
        self._date_close = date_close
        self._content = content
        self._requirement = requirement
        self._education = education
        self._major = major
        self._recruit_num = recruit_num
        self._salary = salary
        self._years_work = years_work
        self._url = url
        self._status = status
        self._create_time = create_time

    def __repr__(self):
        return f"【bank_name: {self._bank_name}, name: {self._name}, url: {self._url}, type_main: {self._type_main}, place: {self._place}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        data['_id'] = str(farmhash.hash64(self._job_id))
        return data

    @classmethod
    def do_load(cls, data: dict):
        target = cls()
        elements = [one for one in dir(cls) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        for one in elements:
            if one in data.keys():
                setattr(target, one, data[one])
        return target

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, value):
        self._job_id = value

    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def branch_name(self):
        return self._branch_name

    @branch_name.setter
    def branch_name(self, value):
        self._branch_name = value

    @property
    def department(self):
        return self._department

    @department.setter
    def department(self, value):
        self._department = value

    @property
    def type_main(self):
        return self._type_main

    @type_main.setter
    def type_main(self, value):
        self._type_main = value

    @property
    def type_next(self):
        return self._type_next

    @type_next.setter
    def type_next(self, value):
        self._type_next = value

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, value):
        self._place = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def date_publish(self):
        return self._date_publish

    @date_publish.setter
    def date_publish(self, value):
        self._date_publish = value

    @property
    def date_close(self):
        return self._date_close

    @date_close.setter
    def date_close(self, value):
        self._date_close = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def requirement(self):
        return self._requirement

    @requirement.setter
    def requirement(self, value):
        self._requirement = value

    @property
    def education(self):
        return self._education

    @education.setter
    def education(self, value):
        self._education = value

    @property
    def major(self):
        return self._major

    @major.setter
    def major(self, value):
        self._major = value

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):
        self._salary = value

    @property
    def recruit_num(self):
        return self._recruit_num

    @recruit_num.setter
    def recruit_num(self, value):
        self._recruit_num = value

    @property
    def years_work(self):
        return self._years_work

    @years_work.setter
    def years_work(self, value):
        self._years_work = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value
