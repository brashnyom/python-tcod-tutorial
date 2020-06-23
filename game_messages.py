import tcod
import textwrap

from typing import List


class Message:
    def __init__(self, text: str, color=tcod.white):
        self.text: str = text
        self.color = color


class MessageLog:
    def __init__(self, x: int, width: int, height: int):
        self.messages: List[Message] = list()
        self.x: int = x
        self.width: int = width
        self.height: int = height

    def add_message(self, message: Message):
        # Split the message if necessary, among multiple lines
        new_message_lines: List[str] = textwrap.wrap(message.text, self.width)

        for line in new_message_lines:
            # If the buffer is full, remove the oldest message to free up space
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and color
            self.messages.append(Message(line, message.color))
