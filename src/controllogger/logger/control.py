import asyncio
import inspect
import json
import logging
import time
from abc import ABC, abstractmethod
from functools import wraps
from json import JSONEncoder
from typing import Type, Callable, Sequence, Any, Union, Optional

from controllogger.enums.log_levels import LogLevels
from controllogger.logger.input import InputLogger
from controllogger.logger.output import OutputLogger
from controllogger.misc.context import LoggerContext
from controllogger.misc.easy_logger import easy_logger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.input_logger_config import InputLoggerConfig
from controllogger.misc.last_resort import last_resort
from controllogger.misc.log_function_config import LogFuntionConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.singleton import Singleton
from controllogger.misc.snake_case import snake_case

try:
    from rich.pretty import pretty_repr
except ImportError:
    def pretty_repr(obj, indent_size=2) -> str:
        class LogJSONEncoder(JSONEncoder):
            def default(self, o):
                return repr(o)

        if isinstance(obj, dict):
            pretty_obj_str = json.dumps(obj, indent=indent_size, cls=LogJSONEncoder)
        elif hasattr(obj, "__dict__"):
            pretty_obj_str = json.dumps({k: getattr(obj, k) for k in obj.__slots__}, indent=indent_size, cls=LogJSONEncoder)
        else:
            raise TypeError(f"Object '{obj}' is not pretty repr-able.")
        return pretty_obj_str


    easy_logger.warning("Could not import rich.pretty.pretty_repr. Using default pretty_repr.")


class ControlBase(ABC):
    """
    Base class for better type hinting.
    """

    @abstractmethod
    def __init__(self, easy_logger_config: Union[EasyLoggerConfig, dict[str, any]] = None):
        ...

    @property
    @abstractmethod
    def all_logger(self) -> dict[str, logging.Logger]:
        """
        Returns all loggers from logging.root.manager.loggerDict
        Note: no copy is returned, so be careful with this function.

        :return:
        """

        ...

    @abstractmethod
    def logger_exists(self, name: str) -> bool:
        """
        Checks if logger exists.

        :param name: Name of the logger
        :return: True if logger exists, False if not
        """

        ...

    @abstractmethod
    def handle(self, record) -> None:
        """
        Handles log records to output loggers by context.
        :param record: Current log record
        :return: None
        """

        ...

    @property
    @abstractmethod
    def logger_defaults_config(self) -> LoggerDefaultsConfig:
        """
        Returns the default logger config.

        :return: LoggerDefaultsConfig
        """

        ...

    @classmethod
    @abstractmethod
    def get_logger(cls, name: str) -> InputLogger:
        """
        A Pythonic way to get a logger. And for better type hinting to InputLogger.
        :param name:
        :return: InputLogger
        """

        ...

    @property
    @abstractmethod
    def input_loggers(self) -> dict[str, InputLogger]:
        """
        Returns all input loggers.
        :return: list of input loggers
        """

        ...

    @abstractmethod
    def set_temp_input_logger_cls(self, logger_cls: Union[Type[logging.Logger], Type[InputLogger], Sequence[Type[InputLogger]]] = None) -> None:
        """
        Sets the temporary input logger class.
        :param logger_cls: InputLogger class
        :return: None
        """

        ...

    @abstractmethod
    def reset_temp_input_logger_cls(self) -> None:
        """
        Resets the temporary input logger class.
        :return: None
        """

        ...

    @property
    @abstractmethod
    def input_logger_type(self) -> type:
        """
        Returns the input logger type.

        :return: InputLogger type
        """

        ...

    @abstractmethod
    def create_input_logger(self, config: Union[InputLoggerConfig, Sequence[InputLoggerConfig], dict, list[dict]] = None) -> Union[InputLogger, list[InputLogger]]:
        """
        Creates input new logger.

        :param config: InputLoggerConfig or list of OutputLoggerConfig
        :return: InputLogger or list of InputLogger
        """

        ...

    @property
    @abstractmethod
    def output_loggers(self) -> dict[str, OutputLogger]:
        """
        Returns all output loggers.

        :return: list of output loggers
        """

        ...

    @abstractmethod
    def set_temp_output_logger_cls(self, logger_cls: Union[Type[OutputLogger], Sequence[Type[OutputLogger]]] = None) -> None:
        """
        Sets the temporary output logger class.
        :param logger_cls: OutputLogger class
        :return: None
        """

        ...

    @abstractmethod
    def reset_temp_output_logger_cls(self) -> None:
        """
        Resets the temporary output logger class.
        :return: None
        """

        ...

    @property
    @abstractmethod
    def output_logger_type(self) -> type:
        """
        Returns the output logger type.
        :return: OutputLogger type
        """

        ...

    @abstractmethod
    def create_output_logger(self,
                             config: Union[OutputLoggerConfig, Sequence[OutputLoggerConfig], dict, list[dict]] = None,
                             logger_cls: Union[Type[OutputLogger], Sequence[Type[OutputLogger]]] = None) -> Union[OutputLogger, list[OutputLogger]]:
        """
        Creates output new logger.

        :param config: OutputLoggerConfig or list of OutputLoggerConfig
        :param logger_cls: OutputLogger class to use
        :return: OutputLogger or list of OutputLogger
        """

        ...

    @property
    @abstractmethod
    def active_contexts(self) -> list[LoggerContext]:
        """
        Returns all active contexts.
        Note: a copy is returned, so it's safe to use the output.

        :return: list of active contexts
        """

        ...

    @property
    @abstractmethod
    def active_context(self) -> LoggerContext:
        """
        Returns the active context.

        :return: Current active context
        """

        ...

    @property
    @abstractmethod
    def decorator_contexts(self) -> list[LoggerContext]:
        """
        Returns all decorator contexts.
        Note: a copy is returned, so it's safe to use the output.

        :return: list of decorator contexts
        """

        ...

    @property
    @abstractmethod
    def context_logger(self) -> list[Union[InputLogger, OutputLogger]]:
        ...

    @property
    @abstractmethod
    def context_exists(self, context: str) -> bool:
        ...

    @abstractmethod
    def get_function_context(self, context: str) -> LoggerContext:
        ...

    @abstractmethod
    def __call__(self,
                 context: str = None,
                 init: bool = True,
                 close: bool = True,
                 output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                 input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                 defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                 logger_cls: Type[logging.Logger] = None) -> LoggerContext:
        """
        Creates a new context.

        :param context: Context name
        :param init: Initialize context
        :param close: Close context after use
        :param output_config: OutputLoggerConfig or list of OutputLoggerConfig to create new output loggers with context
        :param input_config: InputLoggerConfig or list of InputLoggerConfig to create new input loggers with context
        :param defaults_config: LoggerDefaultsConfig to create new loggers in context
        :param logger_cls: OutputLogger class to use
        :return: LoggerContext
        """

        ...

    @abstractmethod
    def function_logger(self,
                        func_config: Union[LogFuntionConfig, dict[str, any]] = None,
                        name: Optional[str] = None,
                        context: Optional[str] = None,
                        output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                        input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                        defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                        pass_logger_context: Optional[str] = ...,
                        pass_input_logger: Optional[str] = ...) -> Callable:
        """
        Decorator to log a function.

        :param func_config: LogFuntionConfig or dict -> config for function logger
        :param name: str -> name of the function in the log
        :param context: str -> context of the function
        :param output_config: dict, OutputLoggerConfig or list of dict or OutputLoggerConfig -> config for output logger created with context
        :param input_config: dict, InputLoggerConfig or list of dict or InputLoggerConfig -> config for input logger created with context if None a default input logger is created
        :param defaults_config: LoggerDefaultsConfig or dict -> default config for output and input loggers created with context
        :param pass_logger_context: str -> name of the variable to pass the logger context to the function
        :param pass_input_logger: str -> name of the variable to pass the first input logger to the function
        :return: Callable
        """

        ...

    @abstractmethod
    def class_logger(self,
                     func_config: Union[LogFuntionConfig, dict[str, any]] = None,
                     func_configs: dict[str, Union[LogFuntionConfig, dict[str, any]]] = None,
                     name: str = None,
                     context: str = None,
                     cls_init_method: str = "__init__",
                     output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                     input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                     defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                     pass_logger_context: Optional[str] = ...,
                     pass_input_logger: Optional[str] = ...) -> Callable:
        """
        Decorator to log a class.

        :param func_config: LogFuntionConfig or dict -> config for __init__ function logger or custom init function set via cls_init_method
        :param func_configs: dict[str, LogFuntionConfig or dict] -> config for class functions
        :param name: str -> name of the class in the log
        :param context: str -> context of the class
        :param cls_init_method: str -> name of the init method
        :param output_config: dict, OutputLoggerConfig or list of dict or OutputLoggerConfig -> config for output logger created with context
        :param input_config: dict, InputLoggerConfig or list of dict or InputLoggerConfig -> config for input logger created with context if None a default input logger is created
        :param defaults_config: LoggerDefaultsConfig or dict -> default config for output and input loggers created with context
        :param pass_logger_context: str -> name of the context property set to class by decorator
        :param pass_input_logger: str -> name of the input logger property set to class by decorator, only first input logger is passed
        :return: Decorated Class
        """

        ...

    @abstractmethod
    def class_logger_method(self, func_config: Union[LogFuntionConfig, dict[str, any]] = None) -> Callable:
        """
        Decorator to log a class method.

        :param func_config: LogFuntionConfig or dict -> config for function logger
        :return: Callable
        """

        ...


def _wrap_control_base(obj) -> Union[ControlBase, Type[ControlBase]]:
    """ Wraps ControlBase to obj. For better type hinting. """
    return obj


@_wrap_control_base
class ControlLogger(logging.Logger, ControlBase, metaclass=Singleton):
    """
    Control logger for easy logger.

    This logger is used to control all other loggers.
    You can create input and output loggers with this logger.
    It also handles the context for input and output loggers.
    """

    def __init__(self, easy_logger_config: Union[EasyLoggerConfig, dict[str, any]] = None):
        # convert dict to EasyLoggerConfig
        if easy_logger_config is None:
            easy_logger_config = EasyLoggerConfig()
        elif type(easy_logger_config) is dict:
            easy_logger_config = EasyLoggerConfig(**easy_logger_config)

        self.config = easy_logger_config

        super().__init__(self.config.name, self.config.level)
        self.propagate = True
        self.disabled = False

        # setup last_resort logger
        if self.config.last_resort:
            last_resort.setLevel(logging.DEBUG)
        else:
            last_resort.setLevel(logging.ERROR)

        # log first message
        easy_logger.info(f"Initializing {self.__class__.__name__} with config:")
        easy_logger.debug(self.config.json(indent=4))

        self._input_loggers = {}
        self._output_loggers = {}

        # context variables
        self._active_context: Union[LoggerContext, None] = None
        self._active_contexts: list[LoggerContext] = []
        self._decorator_contexts: list[LoggerContext] = []

        # set logger classes
        self._temp_output_logger_cls: list[type[OutputLogger]] = []
        self._temp_input_logger_cls: list[type[InputLogger]] = []

        # current class_logger_cls
        self._class_logger_cls: Union[type[Any], None] = None

        # create output loggers
        self.create_output_logger(self.config.output_loggers)

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        _str = f"{self.__class__.__name__}("
        _str += f"name={self.name}, "
        _str += f"level={LogLevels(self.level).name}, "
        if not self.propagate:
            _str += f"propagate={self.propagate}, "
        if self.disabled:
            _str += f"disabled={self.disabled}, "
        if len(self.active_contexts) > 0:
            _str += f"active_contexts=[{', '.join([str(context) for context in self.active_contexts])}], "

        _str = _str[:-2]
        _str += ")"

        return _str

    @property
    def all_logger(self) -> dict[str, logging.Logger]:
        return logging.root.manager.loggerDict

    def logger_exists(self, name: str) -> bool:
        logger = self.all_logger.get(name, None)
        if logger is None:
            return False
        if type(logger) is logging.PlaceHolder:
            return False
        return True

    def handle(self, record) -> None:
        contexts = getattr(record, "contexts")
        record_handled = False
        for context_logger in self.context_logger:
            # skip all InputLogger
            if isinstance(context_logger, InputLogger):
                continue

            # check if context_logger has context
            if len(context_logger.contexts) > 0:
                # check if context_logger has the right context
                found = False
                for context in contexts:
                    if context in context_logger.contexts:
                        found = True
                        break
                if not found:
                    continue  # skip if context not found
            else:  # context_logger has no context so it handles all records
                pass

            # check if context_logger is attached
            if context_logger.attached:
                record_handled = True
                context_logger.handle(record)

        # if record not handled, log to last resort
        if not record_handled:
            easy_logger.debug(f"ControlLogger: Could not handle record '{record}' because no context logger available.")
            last_resort.handle(record)

    @property
    def logger_defaults_config(self) -> LoggerDefaultsConfig:
        config_dict = self.config.dict(exclude_none=True)

        # remove raise_on_closed
        del config_dict["raise_on_closed"]

        # remove raise_on_not_attached
        del config_dict["raise_on_not_attached"]

        # remove output_loggers
        del config_dict["output_loggers"]

        # remove input_logger_cls
        del config_dict["input_logger_cls"]

        # remove output_logger_cls
        del config_dict["output_logger_cls"]

        return LoggerDefaultsConfig(**config_dict)

    @classmethod
    def get_logger(cls, name: str) -> InputLogger:
        get_logger = getattr(logging, "getLogger")
        return get_logger(name)

    @property
    def input_loggers(self) -> dict[str, InputLogger]:
        return self._input_loggers

    def set_temp_input_logger_cls(self, logger_cls: Union[Type[logging.Logger], Type[InputLogger], Sequence[Type[InputLogger]]] = None) -> None:
        if logger_cls is not None:
            if not isinstance(logger_cls, Sequence):
                logger_cls = [logger_cls]
        else:
            logger_cls = []

        self._temp_input_logger_cls = logger_cls

    def reset_temp_input_logger_cls(self) -> None:
        self._temp_input_logger_cls = []

    @property
    def input_logger_type(self) -> type:
        logger_classes = []
        for input_logger_cls in self._temp_input_logger_cls:
            logger_classes.append(input_logger_cls)
        if self.config.output_logger_cls is not None:
            logger_classes.append(self.config.input_logger_cls)
        input_logger_type = type(InputLogger.__name__, tuple(logger_classes), {})
        return input_logger_type

    def create_input_logger(self, config: Union[InputLoggerConfig, Sequence[InputLoggerConfig], dict, list[dict]] = None) -> Union[InputLogger, list[InputLogger]]:
        if not isinstance(config, Sequence):
            config = [config]

        input_logger = []
        for c in config:
            self.set_temp_input_logger_cls(logger_cls=c.logger_cls)
            input_logger.append(InputLogger(config=c))
            self.reset_temp_input_logger_cls()

        if len(input_logger) == 1:
            return input_logger[0]
        else:
            return input_logger

    @property
    def output_loggers(self) -> dict[str, OutputLogger]:
        return self._output_loggers

    def set_temp_output_logger_cls(self, logger_cls: Union[Type[OutputLogger], Sequence[Type[OutputLogger]]] = None) -> None:
        if logger_cls is not None:
            if not isinstance(logger_cls, Sequence):
                logger_cls = [logger_cls]
        else:
            logger_cls = []

        self._temp_output_logger_cls = logger_cls

    def reset_temp_output_logger_cls(self) -> None:
        self._temp_output_logger_cls = []

    @property
    def output_logger_type(self) -> type:
        logger_classes = []
        for output_logger_cls in self._temp_output_logger_cls:
            logger_classes.append(output_logger_cls)
        if self.config.output_logger_cls is not None:
            logger_classes.append(self.config.output_logger_cls)
        output_logger_type = type(OutputLogger.__name__, tuple(logger_classes), {})
        return output_logger_type

    def create_output_logger(self,
                             config: Union[OutputLoggerConfig, Sequence[OutputLoggerConfig], dict, list[dict]] = None,
                             logger_cls: Union[Type[OutputLogger], Sequence[Type[OutputLogger]]] = None) -> Union[OutputLogger, list[OutputLogger]]:
        if not isinstance(config, Sequence):
            config = [config]

        self.set_temp_output_logger_cls(logger_cls=logger_cls)
        output_logger = []
        for c in config:
            output_logger.append(OutputLogger(config=c))
        self.reset_temp_output_logger_cls()

        if len(output_logger) == 1:
            return output_logger[0]
        else:
            return output_logger

    @property
    def active_contexts(self) -> list[LoggerContext]:
        context = self._active_contexts.copy()
        if self._active_context is not None:
            context.append(self._active_context)
        return context

    @property
    def active_context(self) -> LoggerContext:
        return self._active_context

    @property
    def decorator_contexts(self) -> list[LoggerContext]:
        return self._decorator_contexts.copy()

    @property
    def context_logger(self) -> list[Union[InputLogger, OutputLogger]]:
        out = []
        for logger_name in logging.root.manager.loggerDict.keys():
            logger = logging.root.manager.loggerDict[logger_name]
            if isinstance(logger, InputLogger) or isinstance(logger, OutputLogger):
                is_context_logger = False
                if len(logger.contexts) == 0:
                    is_context_logger = True
                for context in logger.contexts:
                    found = False
                    for active_context in self.active_contexts:
                        if context.context == active_context.context:
                            found = True
                            break
                    if found:
                        is_context_logger = True
                        break
                if is_context_logger:
                    out.append(logger)
        return out

    def context_exists(self, context: str) -> bool:
        for context_handler in self.active_contexts:
            if context_handler.context == context:
                return True
        return False

    def get_function_context(self, context: str) -> LoggerContext:
        function_context = None
        for function_context in self.decorator_contexts:
            if function_context.context == context:
                break
        if function_context is None:
            raise ValueError(f"Could not find function context '{context}'.")
        return function_context

    def __call__(self,
                 context: str = None,
                 init: bool = True,
                 close: bool = True,
                 output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                 input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                 defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                 logger_cls: Type[logging.Logger] = None) -> LoggerContext:
        return LoggerContext(context=context,
                             init=init,
                             close=close,
                             output_config=output_config,
                             input_config=input_config,
                             defaults_config=defaults_config,
                             logger_cls=logger_cls)

    @staticmethod
    def _get_var_from_signature(signature: inspect.Signature, cls_type: Optional[Type], prefer_name: list[str], _matched: list[str]) -> tuple[list[str], str]:
        # fist looking fo type annotation
        if cls_type is not None:
            for param in signature.parameters.values():
                # skip all marked parameters
                if param.name in _matched:
                    continue
                if issubclass(param.annotation, cls_type):
                    # mark parameter as matched
                    _matched.append(param.name)
                    return _matched, param.name

        # if not found, looking for name
        for param in signature.parameters.values():
            # skip all marked parameters
            if param.name in _matched:
                continue
            # skip if a type annotation is set
            if param.annotation is not inspect.Parameter.empty:
                continue
            if param.name in prefer_name:
                # mark parameter as matched
                _matched.append(param.name)
                return _matched, param.name

        # if not found, get first parameter
        for param in signature.parameters.values():
            # skip all marked parameters
            if param.name in _matched:
                continue
            # skip if a type annotation is set
            if param.annotation is not inspect.Parameter.empty:
                continue
            # mark parameter as matched
            _matched.append(param.name)
            return _matched, param.name

        # if not found, raise error
        if cls_type is None:
            raise ValueError(f"Could not find parameter {prefer_name} in signature '{signature}'")
        raise ValueError(f"Could not find parameter of type '{cls_type.__name__}' in signature '{signature}'")

    @staticmethod
    def _parse_dict(*args, callback_signature: inspect.Signature, **kwargs) -> dict:

        parsed_kwargs = {}
        arg_index = 0

        def arg_value(ai):
            if arg_index >= len(args):
                a = "..."
            else:
                a = args[arg_index]
            ai += 1
            return a, ai

        def kwarg_value(p):
            if param.name in kwargs:
                return kwargs[param.name]
            if param.default is not inspect.Parameter.empty:
                return param.default
            return "..."

        for param in callback_signature.parameters.values():
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                parsed_kwargs[param.name] = args[arg_index:]
                arg_index = len(args)
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                parsed_kwargs[param.name] = kwargs
            elif param.kind == inspect.Parameter.POSITIONAL_ONLY:
                parsed_kwargs[param.name], arg_index = arg_value(arg_index)
            elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                if param.name not in kwargs:
                    parsed_kwargs[param.name], arg_index = arg_value(arg_index)
                else:
                    parsed_kwargs[param.name] = kwarg_value(param)
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                kwarg_value(param)

        return parsed_kwargs

    @classmethod
    def _log_function_start(cls,
                            *args,
                            func_signature: inspect.Signature,
                            func_or_cls: Union[Callable, Type],
                            self_or_cls: Optional[str],
                            input_logger: InputLogger,
                            func_config: LogFuntionConfig,
                            **kwargs) -> dict:
        # parse dict
        parse_dict = cls._parse_dict(callback_signature=func_signature, *args, **kwargs)

        # get func_name name
        func_name = func_or_cls.__name__
        if "self" == self_or_cls:
            func_name = f"{parse_dict['self'].__class__.__name__}.{func_or_cls.__name__}"
        elif "cls" == self_or_cls:
            func_name = f"{parse_dict['cls'].__name__}.{func_or_cls.__name__}"
        elif self_or_cls is None:
            func_name = func_or_cls.__name__
        func_name += "()"

        # parse start message
        if func_config.start_msg is not None:
            s_msg = func_config.start_msg.format(**parse_dict)
        else:
            s_msg = ""

        # log header
        if func_config.header:
            pretty_parse_dict = pretty_repr(parse_dict, indent_size=2).split("\n")
            input_logger.print_header(
                name=f"{func_name}",
                desc=func_or_cls.__doc__,
                lines=[f"Arguments:", *pretty_parse_dict],
                level=func_config.header_footer_level,
            )

        # log start message
        if s_msg:
            input_logger.log(func_config.start_end_msg_level, s_msg)

        return parse_dict

    @classmethod
    def _log_function_end(cls,
                          result: Any,
                          parse_dict: dict,
                          func_or_cls: Union[Callable, Type],
                          self_or_cls: Optional[str],
                          input_logger: InputLogger,
                          func_config: LogFuntionConfig,
                          start: float = None) -> Any:

        # get func_name name
        func_name = func_or_cls.__name__
        if "self" == self_or_cls:
            func_name = f"{parse_dict['self'].__class__.__name__}.{func_or_cls.__name__}"
        elif "cls" == self_or_cls:
            func_name = f"{parse_dict['cls'].__name__}.{func_or_cls.__name__}"
        elif self_or_cls is None:
            func_name = func_or_cls.__name__
        func_name += "()"

        # perform time measurement
        measure_time_str = ""
        if func_config.measure_time:
            end = time.perf_counter()
            measure_time_str = f"Time elapsed: {end - start:.2f} seconds"

        # parse end message
        if func_config.end_msg is not None:
            e_msg = func_config.end_msg.format(**parse_dict)
        else:
            e_msg = ""

        # log end message
        if e_msg:
            input_logger.log(func_config.start_end_msg_level, e_msg)

        # log footer
        if func_config.footer:
            input_logger.print_header(
                name=f"{func_name} called",
                desc=func_or_cls.__doc__,
                lines=[f"Result: {result}", measure_time_str],
                level=func_config.header_footer_level,
            )
        else:
            if func_config.measure_time:
                input_logger.log(func_config.header_footer_level, measure_time_str)

    def _get_sig_vars(self,
                      func_signature: inspect.Signature,
                      pass_logger_context: Optional[str] = ...,
                      pass_input_logger: Optional[str] = ...,
                      _matched: list[str] = None) -> tuple[list[str], str, str]:
        # init matched
        if _matched is None:
            _matched = []

        # get input logger var from signature
        prefer_input_logger_name = ["l", "lg", "logger"]
        if pass_input_logger is not None:
            prefer_input_logger_name = [pass_input_logger]
        if pass_input_logger is Ellipsis:
            try:
                _matched, _pass_input_logger = self._get_var_from_signature(signature=func_signature,
                                                                            cls_type=InputLogger,
                                                                            prefer_name=prefer_input_logger_name,
                                                                            _matched=_matched)
            except ValueError:
                _pass_input_logger = None
        else:
            _pass_input_logger = pass_input_logger

        # get contex var from signature
        prefer_logger_context_name = ["c", "ctx", "context", "logger_context"]
        if pass_logger_context is not None:
            prefer_logger_context_name = [pass_logger_context]
        if pass_logger_context is Ellipsis:
            try:
                _matched, _pass_logger_context = self._get_var_from_signature(signature=func_signature,
                                                                              cls_type=LoggerContext,
                                                                              prefer_name=prefer_logger_context_name,
                                                                              _matched=_matched)
            except ValueError:
                _pass_logger_context = None
        else:
            _pass_logger_context = pass_logger_context

        return _matched, _pass_input_logger, _pass_logger_context

    def function_logger(self,
                        func_config: Union[LogFuntionConfig, dict[str, any]] = None,
                        name: Optional[str] = None,
                        context: Optional[str] = None,
                        output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                        input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                        defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                        pass_logger_context: Optional[str] = ...,
                        pass_input_logger: Optional[str] = ...) -> Callable:
        if func_config is None:
            func_config = LogFuntionConfig()
        elif type(func_config) is dict:
            func_config = LogFuntionConfig(**func_config)
        elif not isinstance(func_config, LogFuntionConfig):
            raise TypeError(f"func_config must be of type {LogFuntionConfig.__name__} or dict.")

        def decorator(func: Union[Callable, Type]) -> Callable:
            # check if function or type
            if inspect.isclass(func):
                raise NotImplementedError(f"Cant decorate class with {self.__class__.__name__}.function_logger(). Please use {self.__class__.__name__}.class_logger() instead.")

            # init matched
            _matched = []

            if isinstance(func, classmethod):
                raise RuntimeError(f"Please decorate first with @{self.__class__.__name__}.function_logger() then with @classmethod.")
            if isinstance(func, staticmethod):
                raise RuntimeError(f"Please decorate first with @{self.__class__.__name__}.function_logger() then with @staticmethod.")
            if isinstance(func, property):
                raise RuntimeError(f"Can't decorate property with {self.__class__.__name__}.function_logger(). Please use {self.__class__.__name__}.class_logger_method() instead.")

            # get signature
            func_signature = inspect.signature(func)

            # check if self or cls is in signature
            try:
                _matched, _self_or_cls = self._get_var_from_signature(signature=func_signature,
                                                                      cls_type=None,
                                                                      prefer_name=["self", "cls"],
                                                                      _matched=_matched)
            except ValueError:
                _self_or_cls = None

            if _self_or_cls == "self":
                if func.__name__ == "__init__":
                    raise NotImplementedError(
                        f"Cant decorate class method __init__ with {self.__class__.__name__}.function_logger(). Please use {self.__class__.__name__}.class_logger() instead.")
                raise NotImplementedError(
                    f"Cant decorate class method with {self.__class__.__name__}.function_logger(). Please use {self.__class__.__name__}.class_logger_method() instead.")
            elif _self_or_cls == "cls":
                ...
            else:
                _self_or_cls = None
                _matched = []

            # set default values
            _name = name
            if name is None:
                _name = snake_case(func.__name__)

            _context = context
            if context is None:
                _context = func.__name__

            input_logger_name = f"{_name}.logger"
            # get first input logger
            if type(input_config) is list:
                input_logger_name = input_config[0].name

            # check if function or type
            easy_logger.debug(f"Creating context '{_context}' with name '{_name}' for function '{func.__name__}'")

            _pass_input_logger = pass_input_logger
            _pass_logger_context = pass_logger_context
            _matched, _pass_input_logger, _pass_logger_context = self._get_sig_vars(func_signature=func_signature,
                                                                                    pass_logger_context=pass_logger_context,
                                                                                    pass_input_logger=pass_input_logger,
                                                                                    _matched=_matched)
            # create function context
            with self(context=_context,
                      init=True,
                      close=False,
                      defaults_config=defaults_config) as lc:
                # add function context to decorator_contexts
                self._decorator_contexts.append(lc)

                # create output logger
                if output_config is not None:
                    self.create_output_logger(config=output_config)

                # create input logger
                if input_config is not None:
                    self.create_input_logger(config=input_config)
                input_logger = ControlLogger.get_logger(input_logger_name)

            # create synchronous or asynchronous wrapper
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def wrapper(*args, **kwargs):
                    # perform time measurement
                    start = None
                    if func_config.measure_time:
                        start = time.perf_counter()

                    # pass context and input logger to function
                    if _pass_logger_context is not None:
                        kwargs[_pass_logger_context] = lc
                    if _pass_input_logger is not None:
                        kwargs[_pass_input_logger] = input_logger

                    # enter context
                    with lc(close=False) as _lc:
                        parse_dict = self._log_function_start(*args,
                                                              func_signature=func_signature,
                                                              func_or_cls=func,
                                                              self_or_cls=None,
                                                              input_logger=input_logger,
                                                              func_config=func_config,
                                                              start=start,
                                                              **kwargs)
                        result = await func(*args, **kwargs)
                        self._log_function_end(result=result,
                                               parse_dict=parse_dict,
                                               func_or_cls=func,
                                               self_or_cls=None,
                                               input_logger=input_logger,
                                               func_config=func_config,
                                               start=start)

                    return result

                easy_logger.debug(f"Created asynchronous context '{_context}' with name '{_name}' for function '{func.__name__}'")
            else:
                @wraps(func)
                def wrapper(*args, **kwargs):
                    # perform time measurement
                    start = None
                    if func_config.measure_time:
                        start = time.perf_counter()

                    # pass context and input logger to function
                    if pass_logger_context is not None:
                        kwargs[_pass_logger_context] = lc
                    if pass_input_logger is not None:
                        kwargs[_pass_input_logger] = input_logger

                    # enter context
                    with lc(close=False) as _lc:
                        parse_dict = self._log_function_start(*args,
                                                              func_signature=func_signature,
                                                              func_or_cls=func,
                                                              self_or_cls=None,
                                                              input_logger=input_logger,
                                                              func_config=func_config,
                                                              start=start,
                                                              **kwargs)
                        result = func(*args, **kwargs)
                        self._log_function_end(result=result,
                                               parse_dict=parse_dict,
                                               func_or_cls=func,
                                               self_or_cls=None,
                                               input_logger=input_logger,
                                               func_config=func_config,
                                               start=start)

                    return result

            easy_logger.debug(f"Created context '{_context}' with name '{_name}' for function '{func.__name__}'")

            return wrapper

        return decorator

    def class_logger(self,
                     func_config: Union[LogFuntionConfig, dict[str, any]] = None,
                     func_configs: dict[str, Union[LogFuntionConfig, dict[str, any]]] = None,
                     name: str = None,
                     context: str = None,
                     cls_init_method: str = "__init__",
                     output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                     input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                     defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                     pass_logger_context: Optional[str] = ...,
                     pass_input_logger: Optional[str] = ...) -> Callable:

        if func_config is None:
            func_config = LogFuntionConfig()
        elif type(func_config) is dict:
            func_config = LogFuntionConfig(**func_config)
        elif not isinstance(func_config, LogFuntionConfig):
            raise TypeError(f"func_config must be of type {LogFuntionConfig.__name__} or dict.")

        if func_configs is None:
            func_configs = {}
        elif type(func_configs) is not dict:
            raise TypeError(f"func_configs must be of type dict[str, {LogFuntionConfig.__name__}] or dict[str, dict].")

        def decorator(cls) -> Callable:
            # check if function or type
            if not inspect.isclass(cls):
                raise NotImplementedError(f"Cant decorate function with {self.__class__.__name__}.class_logger(). Please use {self.__class__.__name__}.function_logger() instead.")

            # init matched
            _matched = []

            # set default values
            _name = name
            if name is None:
                _name = snake_case(cls.__name__)

            _context = context
            if context is None:
                _context = cls.__name__

            input_logger_name = f"{_name}.logger"
            # get first input logger
            if type(input_config) is list:
                input_logger_name = input_config[0].name

            _pass_input_logger = pass_input_logger
            if pass_input_logger is Ellipsis:
                _pass_input_logger = "logger"

            _pass_logger_context = pass_logger_context
            if pass_logger_context is Ellipsis:
                _pass_logger_context = "logger_context"

            def logger_context_property(_self):
                for function_context in self.decorator_contexts:
                    if function_context.context == _context:
                        return function_context
                raise ValueError(f"Could not find context '{_context}' for class '{cls.__name__}'")

            def logger_property(_self):
                logger_context = ControlLogger.get_logger(input_logger_name)
                return logger_context

            # check if function or type
            easy_logger.debug(f"Creating context '{_context}' with name '{_name}' for type '{cls.__name__}'")

            # create type context
            with self(context=_context,
                      init=True,
                      close=False,
                      defaults_config=defaults_config) as lc:
                # add type context to decorator_contexts
                self._decorator_contexts.append(lc)

                # create output logger
                if output_config is not None:
                    self.create_output_logger(config=output_config)

                # create input logger
                if input_config is not None:
                    self.create_input_logger(config=input_config)

            # set logger context property
            if _pass_logger_context is not None:
                if hasattr(cls, _pass_logger_context):
                    func = getattr(cls, _pass_logger_context)
                    if not getattr(func, "__isabstractmethod__", False):
                        raise AttributeError(f"Class '{cls.__name__}' already has a 'logger_context' attribute.")
                setattr(cls, _pass_logger_context, property(logger_context_property))
            setattr(cls, "__class_logger_context__", property(logger_context_property))
            # set logger property
            if _pass_input_logger is not None:
                if hasattr(cls, _pass_input_logger):
                    func = getattr(cls, _pass_input_logger)
                    if not getattr(func, "__isabstractmethod__", False):
                        raise AttributeError(f"Class '{cls.__name__}' already has a 'logger' attribute.")
                setattr(cls, _pass_input_logger, property(logger_property))
            setattr(cls, "__class_logger__", property(logger_property))

            # check cls_init_method in cls
            if not hasattr(cls, cls_init_method):
                raise ValueError(f"Could not find function '{cls_init_method}' in class '{cls.__name__}'.")
            __cls_init_method__ = getattr(cls, cls_init_method)
            if inspect.isfunction(__cls_init_method__):
                # get signature
                cls_init_method_signature = inspect.signature(__cls_init_method__)

                # check if self or cls is in signature
                try:
                    _matched, _self_or_cls = self._get_var_from_signature(signature=cls_init_method_signature,
                                                                          cls_type=None,
                                                                          prefer_name=["self", "cls"],
                                                                          _matched=_matched)
                except ValueError:
                    _self_or_cls = None

                # overwrite cls_init_method
                @wraps(__cls_init_method__)
                def __class_logger_cls_init_method__(*args, **kwargs):
                    # perform time measurement
                    start = None
                    if func_config.measure_time:
                        start = time.perf_counter()

                    # enter context
                    with lc(close=False) as _lc:
                        parse_dict = self._log_function_start(*args,
                                                              func_signature=cls_init_method_signature,
                                                              func_or_cls=__cls_init_method__,
                                                              self_or_cls=None,
                                                              input_logger=logger_property(None),
                                                              func_config=func_config,
                                                              start=start,
                                                              **kwargs)
                        result = __cls_init_method__(*args, **kwargs)
                        self._log_function_end(result=result,
                                               parse_dict=parse_dict,
                                               func_or_cls=__cls_init_method__,
                                               self_or_cls=None,
                                               input_logger=logger_property(None),
                                               func_config=func_config,
                                               start=start)
                    return result

                setattr(cls, cls_init_method, __class_logger_cls_init_method__)

            # check if __del__ in cls
            # ToDo:

            # create logger methods for class
            for func_name in func_configs:
                # check if function in cls
                if not hasattr(cls, func_name):
                    raise ValueError(f"Could not find function '{func_name}' in class '{cls.__name__}'.")
                __func__ = getattr(cls, func_name)
                if hasattr(__func__, "__logger_class_method__"):
                    raise ValueError(f"Function '{func_name}' in class '{cls.__name__}' is already decorated with {self.__class__.__name__}.class_logger_method().")

                # decorate function
                __func__ = self.class_logger_method(func_config=func_configs[func_name])(__func__)

                # overwrite function
                setattr(cls, func_name, __func__)

            # get all logger_class_methods
            logger_class_methods = []
            for attr_name in dir(cls):
                # noinspection PyBroadException
                try:
                    attr = getattr(cls, attr_name)
                except Exception:
                    continue
                if hasattr(attr, "__logger_class_method__"):
                    logger_class_methods.append(attr)

            return cls

        return decorator

    def class_logger_method(self, func_config: Union[LogFuntionConfig, dict[str, any]] = None) -> Callable:
        if func_config is None:
            func_config = LogFuntionConfig()
        elif type(func_config) is dict:
            func_config = LogFuntionConfig(**func_config)
        elif not isinstance(func_config, LogFuntionConfig):
            raise TypeError(f"func_config must be of type {LogFuntionConfig.__name__} or dict.")

        def decorator(func: Union[Callable, Type]) -> Callable:
            # check if function or type
            if inspect.isclass(func):
                raise NotImplementedError(f"Cant decorate class with {self.__class__.__name__}.function_logger(). Please use {self.__class__.__name__}.class_logger() instead.")

            # init matched
            _matched = []

            if isinstance(func, classmethod):
                raise RuntimeError(f"Can't decorate class method with {self.__class__.__name__}.class_logger_method(). "
                                   f"Please use {self.__class__.__name__}.function_logger() instead.")
            if isinstance(func, staticmethod):
                raise RuntimeError(f"Can't decorate class method with {self.__class__.__name__}.class_logger_method(). "
                                   f"Please use {self.__class__.__name__}.function_logger() instead.")

            if isinstance(func, property):
                func = func.fget

            # get signature
            func_signature = inspect.signature(func)

            # check if self or cls is in signature
            try:
                _matched, _self_or_cls = self._get_var_from_signature(signature=func_signature,
                                                                      cls_type=None,
                                                                      prefer_name=["self", "cls"],
                                                                      _matched=_matched)
            except ValueError:
                _self_or_cls = None

            if _self_or_cls is None:
                raise ValueError(f"Could not find parameter 'self' or 'cls' in signature '{func_signature}'")

            # create synchronous or asynchronous wrapper
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def wrapper(self_or_cls, *args, **kwargs):
                    # perform time measurement
                    start = None
                    if func_config.measure_time:
                        start = time.perf_counter()

                    lc = self_or_cls.__class_logger_context__

                    # add _self to kwargs
                    args = [self_or_cls, *args]

                    with lc(close=False) as _lc:
                        parse_dict = self._log_function_start(*args,
                                                              func_signature=func_signature,
                                                              func_or_cls=func,
                                                              self_or_cls=_self_or_cls,
                                                              input_logger=self_or_cls.__class_logger__,
                                                              func_config=func_config,
                                                              start=start,
                                                              **kwargs)
                        result = await func(*args, **kwargs)
                        self._log_function_end(result=result,
                                               parse_dict=parse_dict,
                                               func_or_cls=func,
                                               self_or_cls=_self_or_cls,
                                               input_logger=self_or_cls.__class_logger__,
                                               func_config=func_config,
                                               start=start)
                    return result
            else:
                @wraps(func)
                def wrapper(self_or_cls, *args, **kwargs):
                    # perform time measurement
                    start = None
                    if func_config.measure_time:
                        start = time.perf_counter()

                    lc = self_or_cls.__class_logger_context__

                    # add _self to kwargs
                    args = [self_or_cls, *args]

                    with lc(close=False) as _lc:
                        parse_dict = self._log_function_start(*args,
                                                              func_signature=func_signature,
                                                              func_or_cls=func,
                                                              self_or_cls=_self_or_cls,
                                                              input_logger=self_or_cls.__class_logger__,
                                                              func_config=func_config,
                                                              start=start,
                                                              **kwargs)
                        result = func(*args, **kwargs)
                        self._log_function_end(result=result,
                                               parse_dict=parse_dict,
                                               func_or_cls=func,
                                               self_or_cls=_self_or_cls,
                                               input_logger=self_or_cls.__class_logger__,
                                               func_config=func_config,
                                               start=start)
                    return result

            wrapper.__logger_class_method__ = True

            return wrapper

        return decorator


# set logger class
logging.setLoggerClass(InputLogger)
