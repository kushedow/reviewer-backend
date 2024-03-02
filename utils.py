from loguru import logger


def __grab_keys_from_sheet(worksheet):
    keys = worksheet.row_values(1)
    keys.remove("ticket_id")
    logger.debug(f"Groups found {keys}")
    return keys


def __count_avg_value_by_topic(items, topic_name):

    values = []
    for item in items:
        if item.get('group') == topic_name:
            values.append(int(item.get("grade"))-3)

    return round(sum(values) / (len(values) * 2), 2) if len(values) > 0 else 0


def __count_min_value_by_criteria(items, criteria_name):

    values = []
    for item in items:
        if item.get('criteria') == criteria_name:
            values.append(int(item.get("grade")))

    return min(values) if len(values) > 0 else 0
