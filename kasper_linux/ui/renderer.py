from abc import ABC, abstractclassmethod
from rx.subject import Subject
from .. import kasperLoop


class Renderer(ABC):
    def __init__(self):
        super().__init__()
        self.subject = Subject()
        self.kasper_loop = kasperLoop(self)
        self.kasper_loop.start(background = True)

    @abstractclassmethod
    def receive_message(self, message_type, payload=None):
        pass

    def on_mic_pressed(self):
        self.subject.on_next('mic_button_pressed')
