from controllogger.misc.logger_class import LoggerContextImplementation, InputLoggerImplementation


# noinspection PyPropertyDefinition
class PydanticLoggerClass:
    @property
    def logger_context(self) -> LoggerContextImplementation:
        ...

    logger_context.fget.__isabstractmethod__ = True

    @property
    def logger(self) -> InputLoggerImplementation:
        ...

    logger.fget.__isabstractmethod__ = True
