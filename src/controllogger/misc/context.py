import logging
import random
import string
from typing import Sequence, Type, Any, Union

from controllogger.misc.easy_logger import easy_logger
from controllogger.misc.input_logger_config import InputLoggerConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig
from controllogger.misc.logger_defaults_config import LoggerDefaultsConfig
from controllogger.misc.singleton import Singleton


class LoggerContext:
    def __init__(self,
                 context: str,
                 init: bool,
                 close: bool,
                 output_config: Union[OutputLoggerConfig, dict[str, any], Sequence[Union[OutputLoggerConfig, dict[str, any]]]] = None,
                 input_config: Union[InputLoggerConfig, dict[str, any], Sequence[Union[InputLoggerConfig, dict[str, any]]]] = None,
                 defaults_config: Union[LoggerDefaultsConfig, dict[str, any]] = None,
                 logger_cls: type[logging.Logger] = logging.Logger,
                 _parent_context: "LoggerContext" = None):
        # if context is None generate random context if not, check if context is in backups
        if context is None:
            generated_context = ""
            while self.control_logger.context_exists(generated_context) or generated_context == "":
                generated_context = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(10)])
        self._context = context

        self._init = init
        self._close = close

        if defaults_config is not None:
            if type(defaults_config) is dict:
                defaults_config = LoggerDefaultsConfig(**defaults_config)
        self._logger_defaults_config = defaults_config

        self._parent_context = _parent_context
        self._child_contexts = []
        self._is_closed = False
        self._logger_cls = logger_cls
        self._context_exists = False

        # create output logger
        if output_config is not None:
            if type(output_config) is dict:
                output_config = OutputLoggerConfig(**output_config)
            if type(output_config) is Sequence:
                output_config = [OutputLoggerConfig(**c) if type(c) is dict else c for c in output_config]

            self.create_output_logger(config=output_config)

        # create input logger
        if input_config is not None:
            if type(input_config) is dict:
                input_config = InputLoggerConfig(**input_config)
            if type(input_config) is Sequence:
                input_config = [InputLoggerConfig(**c) if type(c) is dict else c for c in input_config]

            self.create_input_logger(config=input_config)

    def __repr__(self):
        return f"{self.__class__.__name__}(context={self.context}, init={self._init}, close={self._close})"

    def __str__(self):
        return f"{self.context}"

    def __call__(self, close: bool = False):
        if self.is_closed:
            raise ValueError("Reusing context with close=True is not allowed. Create your context with close=False and close it manually.")
        for context_logger in self.control_logger.context_logger:
            if not context_logger.open:
                raise ValueError(f"Logger '{context_logger.name}' already closed.")
        child_context = LoggerContext(context=self.context, init=False, close=close, _parent_context=self)
        self._child_contexts.append(child_context)
        return child_context

    def __enter__(self) -> "LoggerContext":
        self._context_exists = self.control_logger.context_exists(self.context)
        if self._context_exists:
            easy_logger.info(f"Skip entering context -> Already on context '{self.context}'")
            return self
        easy_logger.info(f"Entering context '{self.context}'")
        _active_contexts = getattr(self.control_logger, "_active_contexts")

        if self.control_logger.active_context is not None:
            # backup current context
            _active_contexts.insert(0, self.control_logger.active_context)

        # create new context handler
        setattr(self.control_logger, "_active_context", self)

        if self._init:
            # check if loggers with context already exist
            for context_logger in self.control_logger.context_logger:
                if self.context == context_logger.contexts:
                    raise ValueError(f"Context '{self.context}' already exists.")

        # attach all loggers with context
        self.attach()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._context_exists:
            easy_logger.info(f"Skip exiting context -> Context '{self.context}' opened by other context handler.")
            return
        if self._close:
            self.close()
        else:
            self.detach()

        # restore context handler
        if len(getattr(self.control_logger, "_active_contexts")) > 0:
            setattr(self.control_logger, "_active_context", getattr(self.control_logger, "_active_contexts").pop(0))
        else:
            setattr(self.control_logger, "_active_context", None)

    @property
    def context(self) -> str:
        return self._context

    @property
    def control_logger(self):
        """
        Returns the control logger singleton

        :return: ControlLogger
        """

        return Singleton.get_by_type("ControlLogger")

    @property
    def context_logger(self) -> list[Union[logging.Logger, Any]]:
        """
        Returns a list of all loggers with context

        :return: list of all loggers with context
        """

        return self.control_logger.context_logger

    @property
    def parent(self) -> "LoggerContext":
        return self._parent_context

    @property
    def children(self) -> list["LoggerContext"]:
        return self._child_contexts

    @property
    def is_closed(self) -> bool:
        if self.parent is None:
            return self._is_closed
        return self.parent.is_closed

    @is_closed.setter
    def is_closed(self, value: bool):
        if self.parent is None:
            self._is_closed = value
        else:
            self.parent.is_closed = value

    @property
    def logger_defaults_config(self) -> LoggerDefaultsConfig:
        """
        Returns the default logger config for the context

        :return: LoggerDefaultsConfig
        """

        output_logger_config_dict = self.control_logger.logger_defaults_config.dict(exclude_none=True)
        # find self in active contexts
        found = False
        for active_context in self.control_logger.active_contexts[::-1]:
            if not found:
                if active_context.context != self.context:
                    continue
                found = True
                continue
            output_logger_config_dict.update(active_context.logger_defaults_config.dict(exclude_none=True))

        if self._logger_defaults_config is not None:
            output_logger_config_dict.update(self._logger_defaults_config.dict(exclude_none=True))
        return LoggerDefaultsConfig(**output_logger_config_dict)

    @logger_defaults_config.setter
    def logger_defaults_config(self, value: Union[LoggerDefaultsConfig, dict[str, any]]):
        if type(value) is dict:
            value = LoggerDefaultsConfig(**value)
        self._logger_defaults_config = value

    @property
    def logger_cls(self) -> type[logging.Logger]:
        return self._logger_cls

    def create_output_logger(self,
                             config: Union[OutputLoggerConfig, Sequence[OutputLoggerConfig], dict, list[dict]] = None,
                             logger_cls: Type[logging.Logger] = None) -> Union[logging.Logger, list[logging.Logger]]:
        """
        Creates output new logger for context

        :param config: OutputLoggerConfig or list of OutputLoggerConfig
        :param logger_cls: OutputLogger class to use
        :return: OutputLogger or list of OutputLogger
        """

        if logger_cls is None:
            logger_cls = self.logger_cls
        return self.control_logger.create_output_logger(config=config, logger_cls=logger_cls)

    def create_input_logger(self,
                            config: Union[InputLoggerConfig, Sequence[InputLoggerConfig], dict, list[dict]] = None,
                            logger_cls: Type[logging.Logger] = None) -> Union[logging.Logger, list[logging.Logger]]:
        """
        Creates input new logger for context

        :param config: InputLoggerConfig or list of InputLoggerConfig
        :param logger_cls: InputLogger class to use
        :return:
        """

        if logger_cls is None:
            logger_cls = self.logger_cls
        return self.control_logger.create_input_logger(config=config, logger_cls=logger_cls)

    def attach(self) -> None:
        """
        Attach all loggers with context
        :return: None
        """
        for context_logger in self.context_logger:
            found = False
            for context in context_logger.contexts:
                if context.context == self.context:
                    found = True
                    break
            if not found:
                continue
            if context_logger.attached:
                continue
            context_logger.attach()

    def detach(self) -> None:
        """
        Detach all loggers with context
        :return: None
        """

        for context_logger in self.context_logger:
            found = False
            for context in context_logger.contexts:
                if context.context == self.context:
                    found = True
                    break
            if not found:
                continue
            if not context_logger.attached:
                continue
            context_logger.detach()

    def close(self):
        """
        Close all loggers with context
        :return: None
        """

        self.is_closed = True

        for context_logger in self.context_logger:
            found = False
            for context in context_logger.contexts:
                if context.context == self.context:
                    found = True
                    break
            if not found:
                continue
            if not context_logger.open:
                continue
            context_logger.__del__()
