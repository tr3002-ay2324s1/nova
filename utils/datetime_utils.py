from datetime import datetime, timedelta
from typing import List, Tuple

from utils.constants import DAY_END_TIME, DAY_START_TIME, NEW_YORK_TIMEZONE_INFO


def get_day_start_end_datetimes() -> Tuple[datetime, datetime]:
    today_date = datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date()
    day_start = datetime.combine(
        today_date,
        DAY_START_TIME,
        tzinfo=NEW_YORK_TIMEZONE_INFO,
    )
    day_end = datetime.combine(
        today_date,
        DAY_END_TIME,
        tzinfo=NEW_YORK_TIMEZONE_INFO,
    )
    return day_start, day_end


def get_current_till_day_end_datetimes() -> Tuple[datetime, datetime]:
    current = datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
    day_end = datetime.combine(
        datetime.now(tz=NEW_YORK_TIMEZONE_INFO).date(),
        DAY_END_TIME,
        tzinfo=NEW_YORK_TIMEZONE_INFO,
    )
    return current, day_end


def get_current_till_midnight_datetimes() -> Tuple[datetime, datetime]:
    current = datetime.now(tz=NEW_YORK_TIMEZONE_INFO)
    midnight = datetime.now(tz=NEW_YORK_TIMEZONE_INFO).replace(
        hour=23, minute=59, second=59
    )

    return current, midnight


def get_tomorrow_start_end_datetimes() -> Tuple[datetime, datetime]:
    today_date = (datetime.now(tz=NEW_YORK_TIMEZONE_INFO) + timedelta(days=1)).date()
    day_start = datetime.combine(
        today_date,
        DAY_START_TIME,
        tzinfo=NEW_YORK_TIMEZONE_INFO,
    )
    day_end = datetime.combine(
        today_date,
        DAY_END_TIME,
        tzinfo=NEW_YORK_TIMEZONE_INFO,
    )
    return day_start, day_end


def get_closest_week() -> Tuple[datetime, datetime]:
    """
    Get the closest week, starting from Sunday 0000 and ending on Saturday 2359.
    """
    # Preserve timezone info in lambdas for precision
    gen_closest_sunday_midnight = lambda: datetime.now(
        tz=NEW_YORK_TIMEZONE_INFO
    ).replace(hour=0, minute=0, second=0) + timedelta(
        days=6 - datetime.now(tz=NEW_YORK_TIMEZONE_INFO).weekday()
    )
    gen_next_saturday_night = lambda: (
        gen_closest_sunday_midnight() + timedelta(days=6)
    ).replace(hour=23, minute=59, second=59)

    return gen_closest_sunday_midnight(), gen_next_saturday_night()


def is_within_a_week(date_string: str):
    # Convert the current date to the "MMDD" format
    current_date = datetime.now().strftime("%m%d")

    # Create datetime objects for the current date and the input date string
    current_datetime = datetime.strptime(current_date, "%m%d")
    input_datetime = datetime.strptime(date_string, "%m%d")

    # Add year to the datetime objects to make comparison possible
    current_year = datetime.now().year
    current_datetime = current_datetime.replace(year=current_year)
    input_datetime = input_datetime.replace(year=current_year)

    # Calculate the difference between the input date and the current date
    delta = input_datetime - current_datetime

    # Check if the input date is within a week from the current date
    if timedelta(days=0) <= delta <= timedelta(days=7):
        return True
    else:
        return False


def get_prettified_time_slots(slots: List[datetime]) -> str:
    """
    Given a list of datetime objects, return a string of the form:
    "
      Monday 8:00 AM - 9:00 AM
      Wednesday 9:00 AM - 10:00 AM
      Thursday 10:00 AM - 11:00 AM
    "
    """
    if not slots:
        return "No available slots"

    individual_slot_strings = []
    for slot in slots:
        # Prettify slot
        individual_slot_strings.append(slot.strftime("%A %I:%M %p"))

    # Join the prettified slots with a newline
    return "\n".join(individual_slot_strings)
