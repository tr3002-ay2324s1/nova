def get_name_time_from_job_name(job_name: str):
    # assume that once job for block is of the form once_{callback.__name__}_{when_formatted}_{chat_id}{job_name_suffix}
    # assume that job name suffix does not contain underscore

    parts = job_name.split("_")
    name = "_".join(parts[7:])
    time = parts[5]
    return name, time