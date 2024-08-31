from .job import DjangoJob, DjangoJobExecution
from .task import Script, ScriptVersion, Task


_models = [
    DjangoJob, DjangoJobExecution,
    Task, Script, ScriptVersion,
]
