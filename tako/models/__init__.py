from .job import DjangoJob, DjangoJobExecution
from .task import ScriptVersion, Task


_models = [
    DjangoJob, DjangoJobExecution,
    Task, ScriptVersion,
]
