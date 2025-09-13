# Utility functions and helpers


def log_error(message: str, severity: str = "ERROR"):
    pass


def topic_matches_filter(topic: str, filter_pattern: str) -> bool:
    # Lógica existente de main.py
    topic_parts = topic.split("/")
    filter_parts = filter_pattern.split("/")
    if len(topic_parts) != len(filter_parts):
        return False
    for topic_part, filter_part in zip(topic_parts, filter_parts):
        if filter_part != "+" and filter_part != topic_part:
            return False
    return True
