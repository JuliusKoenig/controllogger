import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Union

from controllogger.enums.log_levels import LogLevels
from controllogger.enums.logger_event import LoggerEvent
from controllogger.logger.base_easy import BaseEasyLogger
from controllogger.misc.base_logger_config import BaseLoggerConfig
from controllogger.misc.context import LoggerContext
from controllogger.misc.easy_logger import easy_logger
from controllogger.misc.singleton import Singleton

# save if output logger on __new__ was called to prevent infinite loop
_on_new = False


class BaseLogger(BaseEasyLogger, ABC):
    _on_events: dict[str, list[callable]] = {}

    _ConfigClass = BaseLoggerConfig
    _my_type: str = "Logger"
    _control_logger_type_field: str = "None"

    __qwe__ = 123

    def __new__(cls, *args, **kwargs):
        global _on_new
        if not _on_new:
            _on_new = True
            control_logger = Singleton.get_by_type("ControlLogger")
            if cls._control_logger_type_field == "None":
                raise ValueError(f"Control logger type field not set for logger '{cls.__name__}'")
            logger_type = getattr(control_logger, cls._control_logger_type_field)
            __init__ = logger_type.__init__

            def __base_logger_init__(self, *a, **kw):
                if _on_new:
                    return
                self._use_control_logger_name = False
                __init__(self, *a, **kw)
                self.__post_init__()

            logger_type.__init__ = __base_logger_init__

            new_logger = logger_type(*args, **kwargs)
            _on_new = False
            return new_logger

        # register events
        cls.on_event(LoggerEvent.ATTACH)(cls.print_logger_attached)
        cls.on_event(LoggerEvent.INIT)(cls.print_logger_initialized)
        cls.on_event(LoggerEvent.DETACH)(cls.print_logger_detached)
        cls.on_event(LoggerEvent.DESTROY)(cls.print_logger_destroyed)

        return super().__new__(cls)

    def __init__(self, name: str = None, level: Union[LogLevels, int] = logging.NOTSET, config: Union[_ConfigClass, dict[str, any]] = None):
        # parse config
        if config is None:
            config = {}
        if type(config) is dict:
            if name is not None:
                config["name"] = name
            if level in [logging.NOTSET, None]:
                config["level"] = level

            config = self._ConfigClass(**config)
        elif type(config) is not self._ConfigClass:
            raise TypeError(f"config must be of type {self._ConfigClass.__name__} or dict[str, any]")

        self.config = config
        if self.control_logger.active_context is not None:
            self.config.__default_init__(logger_defaults_config=self.control_logger.active_context.logger_defaults_config)
        else:
            self.config.__default_init__(logger_defaults_config=self.control_logger.logger_defaults_config)

        if name is None:
            name = self.config.name
        if level not in [logging.NOTSET, None]:
            level = self.config.level

        # use control logger name
        if self._use_control_logger_name:
            name = self.control_logger.logger_defaults_config.name + "." + self.config.name
            if self.control_logger.active_context is not None:
                name = self.control_logger.active_context.logger_defaults_config.name + "." + self.config.name

        self._init = True
        if type(level) is Enum:
            level = level.value
        super().__init__(name, level)

        # check if logger already exists
        if self.control_logger.logger_exists(self.name):
            raise ValueError(f"Logger '{self.name}' already exists.")

        self._contexts: list[LoggerContext] = self.control_logger.active_contexts
        self._skip_handle = False  # resets after each log
        self._on_attaching = False

    def __post_init__(self):
        if self._init:
            # trigger init event
            self.trigger_event(LoggerEvent.INIT)
            self._init = False

    def __del__(self):
        # trigger destroy event
        self.trigger_event(LoggerEvent.DESTROY)

    @classmethod
    def _get_event_name(cls, event_name: Union[str, LoggerEvent]):
        if type(event_name) is not LoggerEvent:
            event_name = str(event_name)
            try:
                event_name = LoggerEvent[event_name.upper()]
            except KeyError:
                ...
        if event_name not in cls._on_events:
            cls._on_events[event_name] = []
        return event_name

    @classmethod
    def on_event(cls, event_name: Union[LoggerEvent, str]):

        event_name = cls._get_event_name(event_name)

        def decorator(func):
            easy_logger.debug(f"Registering event '{func.__name__}' for event '{event_name}' at logger '{cls.__name__}'")

            # get logger type name from calling class
            logger_type_str = func.__class__

            ...

            def wrapper(self, *args, **kwargs):
                control_logger = Singleton.get_by_type("ControlLogger")
                if not isinstance(self, cls):
                    return  # do nothing if self is not instance of cls
                easy_logger.debug(f"Calling method '{func.__name__}' for event '{event_name}' at logger '{cls.__name__}'")
                func(self, *args, **kwargs)
                easy_logger.debug(f"Called method '{func.__name__}' for event '{event_name}' at logger '{cls.__name__}'")

            cls._on_events[event_name].append(wrapper)

            return wrapper

        return decorator

    def trigger_event(self, event_name: Union[LoggerEvent, str], *args, **kwargs):
        event_name = self._get_event_name(event_name)

        easy_logger.debug(f"Triggering event '{event_name}' for logger '{self.name}'", stacklevel=10)

        if event_name in self._on_events:
            for func in self._on_events[event_name]:
                func(self, *args, **kwargs)

        easy_logger.debug(f"Triggered event '{event_name}' for logger '{self.name}'", stacklevel=10)

    def print_logger_attached(self):
        easy_logger.debug(f"Attached logger '{self.name}' to control logger")
        if self.config.log_attach:
            self.print_header(
                name=f"{self._my_type} '{self.name}' attached at {datetime.now()}",
                level=LogLevels.DEBUG,
                lines=[str(self)],
            )

    def print_logger_initialized(self):
        easy_logger.debug(f"Initialized logger '{self.name}'")
        if self.config.log_init:
            self.print_header(
                name=f"{self._my_type} '{self.name}' initialized at {datetime.now()}",
                level=LogLevels.DEBUG,
                lines=[str(self)],
            )

    def print_logger_detached(self):
        easy_logger.debug(f"Detached logger '{self.name}' from control logger")
        if self.config.log_detach:
            self.print_header(
                name=f"{self._my_type} '{self.name}' detached at {datetime.now()}",
                level=LogLevels.DEBUG,
                lines=[str(self)],
            )

    def print_logger_destroyed(self):
        easy_logger.debug(f"Destroyed logger '{self.name}'")
        if self.config.log_destroy:
            self.print_header(
                name=f"{self._my_type} '{self.name}' destroyed at {datetime.now()}",
                level=LogLevels.DEBUG,
                lines=[str(self)],
            )

    @property
    @abstractmethod
    def attached(self) -> bool:
        ...

    @property
    def control_logger(self):
        """
        Returns the control logger singleton

        :return: ControlLogger
        """

        return Singleton.get_by_type("ControlLogger")

    @property
    def contexts(self) -> list[LoggerContext]:
        """
        Returns a copy of the list of context used by the logger

        :return: copy of the list of context used by the logger
        """

        return self._contexts.copy()

    @property
    def open(self) -> bool:
        if self.name not in self.control_logger.all_logger and not self._init:
            return False
        # if logger on creation
        return True

    @property
    def closed(self) -> bool:
        return not self.open

    @property
    def skip_handle(self) -> bool:
        return self._skip_handle

    @abstractmethod
    def attach(self) -> None:
        if len(self.contexts) == 0:
            easy_logger.debug(f"Attaching logger '{self.name}' to control logger")
        else:
            context_str = ", ".join([str(context) for context in self.contexts])
            easy_logger.debug(f"Attaching logger '{self.name}' to context '{context_str}'")
        self._on_attaching = True
        # trigger attach event
        self.trigger_event(LoggerEvent.ATTACH)
        self._on_attaching = False

    @abstractmethod
    def detach(self) -> None:
        if len(self.contexts) == 0:
            easy_logger.debug(f"Detaching logger '{self.name}' from control logger")
        else:
            context_str = ", ".join([str(context) for context in self.contexts])
            easy_logger.debug(f"Detaching logger '{self.name}' from context '{context_str}'")
        # trigger detach event
        self.trigger_event(LoggerEvent.DETACH)

    def handle(self, record):
        # raise error if logger is closed
        if not self.open:
            if self.control_logger.config.raise_on_closed:
                raise ValueError(f"Logger '{self.name}' is closed.")
            else:
                easy_logger.warning(f"Logger '{self.name}' is closed.")
                return

        # raise error if logger is not attached
        if not self.attached and not self._on_attaching:
            if self.control_logger.config.raise_on_not_attached:
                raise ValueError(f"Logger '{self.name}' is not attached.")
            else:
                easy_logger.warning(f"Logger '{self.name}' is not attached.")
                return

        # skip handle if skip_handle is True
        skip_handle = self.skip_handle
        self._skip_handle = False
        if not skip_handle:
            return super().handle(record)

    def print_header(
            self,
            name: str,
            desc: str = None,
            lines: list[str] = None,
            level: LogLevels = LogLevels.INFO,
    ) -> None:
        """
        Prints a header to the terminal

        :param name: Name of the header
        :param desc: Description of the header
        :param lines: Lines to print
        :param level: Log level to use
        :return:
        """

        if not self.isEnabledFor(level):
            return

        if not isinstance(level, int):
            if logging.raiseExceptions:
                raise TypeError("level must be an integer")
            else:
                return
        if self.isEnabledFor(level):
            self._log(level,
                      "[HEADER]",
                      (),
                      extra={"header": {"name": name,
                                        "desc": desc,
                                        "lines": lines,
                                        }
                             },
                      stack_info=False,
                      stacklevel=2)

    def print_traceback(self):
        """
        Prints the traceback to the logger
        :return:
        """
        tb = traceback.format_exc()
        self.exception(f"Traceback: \n{tb}")
