
class ConsoleHistory(object):
    """Written by Kamil Dworakowski for the Resolver One console.
    Contributed by Resolver Systems."""

    def __init__(self):
        self.commands = [""]
        self.immutableHistory = []
        self.cursor = 0

        
    def append(self, commandText):
        if commandText in self.immutableHistory:
            self.immutableHistory.remove(commandText)
        self.immutableHistory.append(commandText)
        self.commands = self.immutableHistory + [""]
        self.cursor = len(self.commands) - 1

    def back(self, currentCommand):
        self.commands[self.cursor] = currentCommand
        if self.cursor > 0:
            self.cursor -= 1
            return self.commands[self.cursor]
    
    def forward(self, currentCommand):
        self.commands[self.cursor] = currentCommand
        if self.cursor < len(self.commands) - 1:
            self.cursor += 1
            return self.commands[self.cursor]
