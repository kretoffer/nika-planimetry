from sc_kpm import ScModule
from .TaskAgent import TaskAgent
from .ThemeAgent import ThemeAgent


class MessageProcessingModule(ScModule):
    def __init__(self):
        super().__init__(TaskAgent(), ThemeAgent())
