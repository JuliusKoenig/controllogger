import logging

last_resort = logging.getLogger("fastapi-easylogger-last-resort")
last_resort_handler = logging.StreamHandler()
last_resort_handler_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
last_resort_handler.setFormatter(last_resort_handler_formatter)
last_resort.addHandler(last_resort_handler)