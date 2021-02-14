from collections import namedtuple
from ploomber.io import TerminalWriter
from io import StringIO

_sep = '\n\n' + '-' * 80 + '\n' + '-' * 80 + '\n\n'

Message = namedtuple('Message', ['task_str', 'message', 'obj'])


class MessageCollector:
    """Collect messages and display them as a single str with task names
    Utilities for exception handling

    When a DAG is rendered or built, exceptions/warnings might happen, this
    class helps collect them all to show a meaninful error message where each
    one is shown along with the task name it generated it.
    """
    def __init__(self, messages=None):
        self.messages = messages or []

    def append(self, task_str, message, obj=None):
        self.messages.append(
            Message(task_str=task_str, message=message, obj=obj))

    def __str__(self):
        return self.to_str()

    def to_str(self, title=None, file=None):
        """
        Return the string representation of the collected messages

        Parameters
        ----------
        title
            Title to show at the beginning
        file
            Text stream to use. If None, uses a temporary StringIO object
        """
        if file is None:
            sio = StringIO()
        else:
            sio = file

        self.tw = TerminalWriter(file=sio)

        if title:
            self.tw.sep('=', title=title, red=True)

        for exp in self.messages:
            self.tw.sep('-', title=exp.task_str, red=True)
            self.tw._write_source(exp.message.splitlines(), lexer='pytb')

        self.tw.sep('=',
                    title=f'Failed tasks summary ({len(self.messages)})',
                    red=True)

        for exp in self.messages:
            # TODO: include original exception type and error message
            self.tw.write(f'{exp.task_str}\n')

        self.tw.sep('=', red=True)

        sio.seek(0)
        out = sio.read()

        if file is None:
            sio.close()

        return out

    def __len__(self):
        return len(self.messages)

    def __bool__(self):
        return bool(self.messages)

    def __iter__(self):
        for message in self.messages:
            yield message
