from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import Field, BaseModel

from ..classes.pydantic_object_id import PydanticObjectId
from ..classes.singleton import Singleton
from ..enums.log import LogLevels
from ..enums.terminal_out_file import TerminalOutFile





class LogEntryModel(BaseModel):
    """
    Class for log entries
    """

    class Config:  # Shadows models.base.BaseModel.Config
        use_enum_values = True

    timestamp: datetime = Field(..., title="Timestamp", description="Timestamp of log entry")
    level: LogLevels = Field(..., title="Level", description="Level of log entry")
    msg: str = Field(..., title="Message", description="Message of log entry")


class BaseLogNewModel(BaseModel):
    """
    Base Class for new log
    """

    class Config:  # Shadows models.base.BaseModel.Config
        use_enum_values = True

    id: str = Field(..., title="ID", description="ID of background task")
    name: str = Field(..., title="Name", description="Name of background task")


class BaseLogReadModel(BaseModel):
    """
    Base Class for read log
    """

    class Config:  # Shadows models.base.BaseModel.Config
        use_enum_values = True

    # Shadows models.base.BaseDbReadModel:
    id: PydanticObjectId = Field(..., title="ID", description="ID of document")
    created_at: float = Field(..., title="Created At", description="Created at timestamp")
    updated_at: float = Field(..., title="Updated At", description="Updated at timestamp")
    # End Shadows

    name: str = Field(..., title="Name", description="Name of log")
    started_at: datetime = Field(None, title="Started At", description="Timestamp of when log started")
    finished_at: datetime = Field(None, title="Finished At", description="Timestamp of when log finished")
    log_lines: list[LogEntryModel] = Field([], title="Log Lines", description="List of log lines")


class BaseLogListModel(BaseModel):
    """
    Base Class for list log
    """

    class Config:  # Shadows models.base.BaseModel.Config
        use_enum_values = True

    # Shadows models.base.BaseDbReadModel:
    id: PydanticObjectId = Field(..., title="ID", description="ID of document")
    created_at: float = Field(..., title="Created At", description="Created at timestamp")
    updated_at: float = Field(..., title="Updated At", description="Updated at timestamp")
    # End Shadows

    name: str = Field(..., title="Name", description="Name of background task")
    started_at: datetime = Field(None, title="Started At", description="Started at")
    finished_at: datetime = Field(None, title="Finished At", description="Finished at")


class BaseLogWriteModel(BaseModel):
    """
    Base Class for write log
    """

    class Config:  # Shadows models.base.BaseModel.Config
        use_enum_values = True

    name: str = Field(..., title="Name", description="Name of log")
    started_at: datetime = Field(None, title="Started At", description="Timestamp of when log started")
    finished_at: datetime = Field(None, title="Finished At", description="Timestamp of when log finished")
    log_lines: list[LogEntryModel] = Field([], title="Log Lines", description="List of log lines")
