# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/12-debug-utils.ipynb (unless otherwise specified).

__all__ = ['IpyLogger']

# Internal Cell
import logging
from typing import List, Any

from IPython.core.display import display
from ipywidgets import Output
from pubsub import pub

# Internal Cell
class OutputWidgetHandler(logging.Handler):
    """ Custom logging handler sending logs to an output widget """

    def __init__(self, *args, **kwargs):
        super(OutputWidgetHandler, self).__init__(*args, **kwargs)
        layout = {
            'border': '1px solid black'
        }
        self.out = Output(layout=layout)

    def emit(self, record):
        """ Overload of logging.Handler method """
        formatted_record = self.format(record)
        new_output = {
            'name': 'stdout',
            'output_type': 'stream',
            'text': formatted_record+'\n'
        }
        self.out.outputs = (new_output, ) + self.out.outputs

    def show_logs(self):
        """ Show the logs """
        display(self.out)

    def clear_logs(self):
        """ Clear the current logs """
        self.out.clear_output()

# Cell

class IpyLogger:
    """
    Redirects logging and pubsub messages (if subscribed) to output widget.

    Use `@subscribe` class decorator or `subscribe_to_states` method to listen pubsub events.
    """

    def __init__(self, class_name: str, log_level=logging.INFO):
        self._class_name = class_name

        # config the logger/output
        logger = logging.getLogger(__name__)
        handler = OutputWidgetHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(log_level)
        self._logger = logger
        self._handler = handler

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def subscribe(self, states):
        def wrapper(cls):
            def inside_wrapper(*args, **kwargs):
                self.subscribe_to_states(states=states)
                return cls(*args, **kwargs)
            return inside_wrapper
        return wrapper

    def show_logs(self):
        return self._handler.show_logs()

    def clear_logs(self):
        return self._handler.clear_logs()

    def subscribe_to_states(self, states: List[Any]):
        states = self._validate_states(states)
        for state in states:
            pub.subscribe(self._pub_handler, state)

    def _pub_handler(self, topic_obj=pub.AUTO_TOPIC, *args, **kwargs):
        self._logger.info(f"[{self._class_name} - {topic_obj.getName()}] : {kwargs}")

    @staticmethod
    def _validate_states(states):
        """Avoids errors where string is handled as list"""
        if isinstance(states, str):
            states = [states]
        return states