import sys

from colorizer import colorize, blue
from consoletextbox import get_console_block
from utils import always_invoke, invoke

from utils import _debug



class StatefulPrinter(object):
    def __init__(self, parent, scroller, prompt):
        self.block = None
        self.parent = parent
        self.scroller = scroller
        self.prompt = prompt
        self.prompt.Foreground = blue
        
    
    @invoke
    def clear(self):
        self.parent.Children.Clear()
        self.prompt.Text = sys.ps1
    
    @invoke
    def set_prompt(self):
        self.prompt.Text = sys.ps1
        
        
    @invoke
    def write(self, data):
        if self.block is None:
            self.block = get_console_block()
            self.parent.Children.Add(self.block)
            
        block = self.block
        if data.endswith('\n'):
            data = data[:-1]
            self.block = None
        
        block.Text += data
    
    def print_new(self, data):
        if self.block is not None:
            self.block = None
        if not data.endswith('\n'):
            data += '\n'
        self.write(data)

    @invoke
    def print_lines(self, data):
        code = data.replace('\r\n', '\n').replace('\r', '\n')
        _debug('code', repr(code))

        self.block = get_console_block()
        self.parent.Children.Add(self.block)
        ps1 = sys.ps1
        ps2 = sys.ps2
        if not isinstance(ps1, str):
            ps1 = str(ps1)
            ps2 = str(ps2)
        for run in colorize(code, ps1, ps2):
            self.block.Inlines.Add(run)
            color = run.Foreground.Color
            #_debug("Printing run", repr(run.Text), color.R, color.G, color.B)
        #_debug(repr(self.block.Text))
        self.block = None
        
    def print_lines_old(self, data):
        lines = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        lines[0] = sys.ps1 + lines[0]
        lines[1:] = [sys.ps2 + line for line in lines[1:]]
        self.print_new('\n'.join(lines))


    @always_invoke
    def scroll(self):
        scroller = self.scroller
        if scroller.ScrollableHeight > 0:
            scroller.ScrollToVerticalOffset(scroller.ScrollableHeight + scroller.ActualHeight)

