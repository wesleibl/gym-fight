from datetime import date

from app.models.schedule import ScheduleType
from app.models.user import Gender, User


def allowed_types(user: User):
    types = [ScheduleType.COMMON]
    if user.is_athletic:
        types += [ScheduleType.ATHLETE.value]
    
    if user.gender == Gender.FEMALE:
        types += [ScheduleType.FEMALE.value]

    if calculate_age(user.birth_date) < 12:
        types += [ScheduleType.KIDS.value]

    return types

def calculate_age(birth_date: date) -> int:
    today = date.today()
    calc = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return calc