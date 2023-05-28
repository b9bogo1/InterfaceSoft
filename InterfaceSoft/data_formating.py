from datetime import datetime, timedelta


def hourly_formating(readings):
    # convert the readings list to a list of dictionaries using the as_dict method
    local_readings_dict = [reading.as_dict() for reading in readings]
    # group the readings by trans_id and have each trans_id have its own list of readings
    grouped_readings = {trans_id: [reading for reading in local_readings_dict if reading["trans_id"] == trans_id] for
                        trans_id in set(reading["trans_id"] for reading in local_readings_dict)}

    hourly_readings = {trans_id: [{"average_temp_1": round(sum(reading["temp_1"] for reading in readings if
                                                               reading["created_at"].hour == (
                                                                       datetime.now() - timedelta(
                                                                   hours=hour)).hour) / len(
        [reading["temp_1"] for reading in readings if
         reading["created_at"].hour == (datetime.now() - timedelta(hours=hour)).hour]), 3) if len(
        [reading["temp_1"] for reading in readings if
         reading["created_at"].hour == (datetime.now() - timedelta(hours=hour)).hour]) > 0 else 0,
                                   "average_temp_2": round(sum(reading["temp_2"] for reading in readings if
                                                               reading["created_at"].hour == (
                                                                       datetime.now() - timedelta(
                                                                   hours=hour)).hour) / len(
                                       [reading["temp_2"] for reading in readings if
                                        reading["created_at"].hour == (datetime.now() - timedelta(hours=hour)).hour]),
                                                           3) if len([reading["temp_2"] for reading in readings if
                                                                      reading["created_at"].hour == (
                                                                              datetime.now() - timedelta(
                                                                          hours=hour)).hour]) > 0 else 0,
                                   "reference_hour": (datetime.now() - timedelta(hours=hour))}
                                  for hour in range(24)]
                       for trans_id, readings in grouped_readings.items()}
    return hourly_readings
