from datetime import datetime, timedelta


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
