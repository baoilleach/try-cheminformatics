import sys

import clr
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from System import Uri
from System.Threading import Thread, ManualResetEvent, ThreadStart
from System.Windows import Thickness, TextWrapping, Visibility
from System.Windows.Browser import HtmlPage
from System.Windows.Controls import TextBox, TextBlock, ScrollBarVisibility
from System.Windows.Input import Key, Keyboard, ModifierKeys
from System.Windows.Media import Colors, SolidColorBrush, FontFamily

from IronPython.Hosting import Python
from Microsoft.Scripting import ScriptCodeParseResult, SourceCodeKind

import traceback

from consolehistory import ConsoleHistory
from context import banner, home

from utils import (
    empty_or_comment_only, get_indent, is_terminator,
    magic_function, invoke, blow_up, _debug
)


# Magic flag from the codeop module
PyCF_DONT_IMPLY_DEDENT = 0x200

class ConsoleTextBox(TextBox):
    def __new__(cls, width, printer, context, root):
        return TextBox.__new__(cls)
    
    def __init__(self, width, printer, context, root):
        self.original_context = context
        self.printer = printer
        self.prompt = root.prompt
        self.root = root
        
        self.FontSize = 15
        self.Margin = Thickness(0)
        self.FontFamily = FontFamily("Consolas, Monaco, Lucida Console, Global Monospace")
        self.AcceptsReturn = True
        self.BorderThickness = Thickness(0)
        self.VerticalScrollBarVisibility = ScrollBarVisibility.Auto
        self.MinWidth = 200
        self.Width = width
        
        def reset():
            "Clear the console, its history and the execution context."
            self._reset_needed = True
        def input(prompt='Input:'):
            'input([prompt]) -> value\n\nEquivalent to eval(raw_input(prompt)).'
            return eval(self.context['raw_input'](prompt), self.context, self.context)
        gohome = invoke(lambda: HtmlPage.Window.Navigate(Uri(home)))
        
        self.original_context['reset'] = magic_function(reset, 'resetting')
        self.original_context['gohome'] = magic_function(gohome,'Leaving...')
        self.original_context['exit'] = 'There is no escape...'
        self.original_context['raw_input'] = self.raw_input
        self.original_context['input'] = input

        
        # for debugging only!
        self.original_context['root'] = root
        
        self.context = {}
        self.history = None
        self._reset_needed = False
        self._thread = None
        self._thread_reset = None
        self._raw_input_text = ''
        self._temp_context = None
        self.engine = Python.CreateEngine()
        self.scope = self.engine.CreateScope()
        
        self._original_caret = None
        if hasattr(self, 'CaretBrush'):
            self._original_caret = self.CaretBrush
        self._disabled = SolidColorBrush(Colors.White)
        
        self.KeyDown += self.handle_key
        self.TextChanged += self.text_changed

    
    def reset(self):
        self.printer.clear()
        self._reset_needed = False
        self.context.clear()
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
        
        modifiers = Keyboard.Modifiers
        control = (modifiers & ModifierKeys.Control) or (modifiers & ModifierKeys.Apple)
        if key == Key.C and control:
            event.Handled = True
            self.keyboard_interrupt()
            return
        
        if self._thread is not None:
            # ignore key events (we have already checked for Ctrl-C)
            event.Handled = True
            return

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
            self.printer.scroll()
            return
        
        if not self.is_complete(contents, start):
            self.do_indent(start)
        else:
            self.execute(contents)


    def execute(self, contents):
        self.printer.print_lines(contents)
        self.Text = ''
        self.history.append(contents)
        
        started = ManualResetEvent(False)
        if self._temp_context is not None:
            self.context.update(self._temp_context)
        def _execute():
            context = self.context
            started.Set()
            try:
                code = compile(contents + '\n', '<stdin>', 'single', 
                               PyCF_DONT_IMPLY_DEDENT)
                exec code in context
            except:
                if reset_event.WaitOne(1):
                    # don't print exception messages if thread has been terminated
                    return
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
                    # we don't print the 'Traceback...' part for SyntaxError
                    message.insert(0, "Traceback (most recent call last):\n")
                message.extend(traceback.format_exception_only(exc_type, value))
                self.printer.print_new(''.join(message))
                
            # access through closure not on self as we may be an orphaned
            # thread - with a new reset_event on self
            result = reset_event.WaitOne(0)
            if not reset_event.WaitOne(0):
                self.completed()
            
        self._thread_reset = reset_event = ManualResetEvent(False)
        self._thread = Thread(ThreadStart(_execute))
        self._thread.IsBackground = True
        self._thread.Name = "executing"
        self._thread.Start()
        self.prompt.Visibility = Visibility.Collapsed
        if self._original_caret is not None:
            self.CaretBrush = self._disabled
        started.WaitOne()
        
        
    @invoke
    def completed(self, reset_temp=True):
        if reset_temp:
            self._temp_context = None
        self._thread = None
        self.prompt.Visibility = Visibility.Visible
        if self._original_caret is not None:
            self.CaretBrush = self._original_caret
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

        
    def keyboard_interrupt(self):
        # Aborting threads doesn't work on Silverlight :-(
        #self._thread.Abort()
        reset_temp = True
        if self._thread_reset is not None:
            reset_temp = False
            # signal to background thread not to complete
            self._thread_reset.Set()
            context = self.context
            self._temp_context = context.copy()
            # This will hopefully cause the existing thread to error out
            context.clear()
            context['raw_input'] = context['input'] = blow_up
            
        self._thread_reset = None
        self._thread = None
        
        if self.Text.strip():
            self.history.append(self.Text)
        self.printer.print_new('KeyboardInterrupt')
        self.Text = ''
        self.completed(reset_temp)


    @invoke
    def setup_input_box(self, prompt):
        self.Visibility = Visibility.Collapsed
        self.root.rawInputPrompt.Text = prompt + ' '
        self.root.rawInputField.Text = ''
        self.root.rawInputField.Width = self.Width - 60
        self.root.rawInput.Visibility = Visibility.Visible
        self.root.rawInputField.KeyDown += self.check_for_enter
        self.root.rawInputField.Focus()


    @invoke
    def remove_input_box(self):
        self.Visibility = Visibility.Visible
        self.root.rawInput.Visibility = Visibility.Collapsed
        self.root.rawInputField.KeyDown -= self.check_for_enter
        self.printer.print_new(self.root.rawInputPrompt.Text + self._raw_input_text)
        self.Focus()


    def check_for_enter(self, sender, event):
        if event.Key == Key.Enter:
            event.Handled = True
            self._raw_input_text = self.root.rawInputField.Text
            self.input_event.Set()


    def raw_input(self, prompt='Input:'):
        if not isinstance(prompt, str):
            prompt = str(prompt)
        self.input_event = ManualResetEvent(False)
        self.setup_input_box(prompt)
        self.input_event.WaitOne()
        self.remove_input_box()
        return self._raw_input_text
    
        


def get_console_block():
    block = TextBlock()
    block.FontSize = 15
    block.Margin = Thickness(0, 0, 0, 0)
    block.TextWrapping = TextWrapping.Wrap
    block.FontFamily = FontFamily("Consolas, Global Monospace")
    return block
