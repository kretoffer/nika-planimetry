from sc_kpm import ScModule
from .TaskAgent import TaskAgent


class MessageProcessingModule(ScModule):
    def __init__(self):
        super().__init__(TaskAgent())
