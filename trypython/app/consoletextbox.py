import sys

import clr
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from System import Uri
from System.Windows import Thickness, TextWrapping
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import TextBox, TextBlock, ScrollBarVisibility
from System.Windows.Input import Key
from System.Windows.Media import FontFamily

from IronPython.Hosting import Python
from Microsoft.Scripting import ScriptCodeParseResult, SourceCodeKind

import traceback

from consolehistory import ConsoleHistory
from context import banner, home

from utils import (
    empty_or_comment_only, get_indent, is_terminator,
    magic_function
)


# Magic flag from the codeop module
PyCF_DONT_IMPLY_DEDENT = 0x200


class ConsoleTextBox(TextBox):
    def __new__(cls, width, printer, context):
        return TextBox.__new__(cls)
    
    def __init__(self, width, printer, context):
        self.original_context = context
        self.printer = printer
        self.FontSize = 15
        self.Margin = Thickness(0, 0, 0, 0)
        self.FontFamily = FontFamily("Consolas, Global Monospace")
        self.TextChanged += self.text_changed
        self.AcceptsReturn = True
        self.BorderThickness = Thickness(0)
        self.VerticalScrollBarVisibility = ScrollBarVisibility.Auto
        self.MinWidth = 200
        self.Width = width
        
        def reset():
            self._reset_needed = True
        self.original_context['reset'] = magic_function(reset, 'resetting')
        self.original_context['gohome'] = magic_function(lambda: HtmlPage.Window.Navigate(Uri(home)), 
                                                         'Leaving...')
        
        self.context = None
        self.engine = Python.CreateEngine()
        self.scope = self.engine.CreateScope()
        self.history = None
        self._reset_needed = False
        self.KeyDown += self.handle_key

    
    def reset(self):
        self.printer.clear()
        self._reset_needed = False
        self.context = self.original_context.copy()
        self.history = ConsoleHistory()
        self.printer.print_new(banner)

        
    def OnKeyDown(self, event):
        # needed so that we get KeyDown 
        # for del and backspace events etc
        pass


    def text_changed(self, sender, event):
        # replace any tabs that are pasted in
        if '\t' in self.Text:
            self.Text = self.Text.replace('\t', '    ')
            self.SelectionStart = len(self.Text)

        
    def write(self, data):
        self.printer.write(data)

    
    def is_complete(self, text, pos):
        if len(text.splitlines()) > 1 and pos < len(text.rstrip()):
            return False
        
        source = self.engine.CreateScriptSourceFromString(text, '<stdin>', SourceCodeKind.InteractiveCode)
        
        result = source.GetCodeProperties()
        if result == ScriptCodeParseResult.IncompleteToken:
            return False
        elif result == ScriptCodeParseResult.IncompleteStatement:
            if not text.rstrip(' ').endswith('\n'):
                return False
        return True
    
    
    def on_first_line(self, text):
        first_line_end = text.find('\n')
        if first_line_end == -1:
            return True
        return self.SelectionStart <= first_line_end
    
    
    def on_last_line(self, text):
        last_line_end = text.rfind('\n')
        if last_line_end == -1:
            return True
        return self.SelectionStart > last_line_end
        
    
    def handle_key(self, sender, event):
        # Mac Safari uses '\r' for newlines in Silverlight TextBox??
        contents = self.Text.replace('\r\n', '\n').replace('\r', '\n')
        key = event.Key
        start = self.SelectionStart
        end = start + self.SelectionLength

        if key != Key.Enter:
            if key == Key.Up:
                if self.on_first_line(contents):
                    event.Handled = True
                    previous = self.history.back(contents)
                    if previous is not None:
                        self.Text = previous
                        self.SelectionStart = len(previous)
                    return
                
            elif key == Key.Down:
                if self.on_last_line(contents):
                    event.Handled = True
                    next = self.history.forward(contents)
                    if next is not None:
                        self.Text = next
                        self.SelectionStart = len(next)
                    return
            
            elif key == Key.Tab:
                event.Handled = True
                self.Text = self.Text[:start] + '    ' + self.Text[end:]
                self.SelectionStart = start + 4
                return
                
            TextBox.OnKeyDown(self, event)
            return
        
        event.Handled = True
        if empty_or_comment_only(contents):
            # needed or we get a SyntaxError
            self.Text = ''
            self.printer.print_lines(contents)
            return
        
        if not self.is_complete(contents, start):
            self.do_indent(start)
        else:
            self.execute(contents)


    def execute(self, contents):
        self.printer.print_lines(contents)
        self.Text = ''
        self.history.append(contents)
        try:
            code = compile(contents + '\n', '<stdin>', 'single', PyCF_DONT_IMPLY_DEDENT)
            exec code in self.context
        except:
            exc_type, value, tb = sys.exc_info()
            if value is None:
                # String exceptions
                # workaround for IronPython bug
                exc_type = Exception
                value = Exception('StringException')
                
            tblist = traceback.extract_tb(tb)
            message = traceback.format_list(tblist)
            del message[:1]
            if message:
                message.insert(0, "Traceback (most recent call last):\n")
            message.extend(traceback.format_exception_only(exc_type, value))
            self.printer.print_new(''.join(message))
    
        if self._reset_needed:
            self.reset()
        else:
            self.printer.scroll()


    def do_indent(self, start):
        to_the_left = self.Text[:start + 1]
        lines = to_the_left.splitlines()
        initial_indent = '    '
        for line in lines:
            # we do this incase the user is using one or two space
            # indent instead of four
            if line.startswith(' '):
                initial_indent = get_indent(line)
                break
        
        # there *must* be something here because an empty textbox
        # would already have been caught by empty_or_comment_only
        last_line = lines[-1]
        new_indent = current_indent = get_indent(last_line)
        if last_line.rstrip().endswith(':'):
            new_indent = current_indent + initial_indent
        elif is_terminator(last_line):
            new_indent = ' ' * (len(current_indent) - len(initial_indent))
        
        new_start = self.SelectionStart
        new_pos = new_start + len(new_indent)
        self.Text = self.Text[:new_start] + '\n' + new_indent + self.Text[new_start:]
        self.SelectionStart = new_pos + 1


def get_console_block():
    block = TextBlock()
    block.FontSize = 15
    block.Margin = Thickness(0, 0, 0, 0)
    block.TextWrapping = TextWrapping.Wrap
    block.FontFamily = FontFamily("Consolas, Global Monospace")
    return block
