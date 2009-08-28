from System.Windows import Thickness, TextWrapping
from System.Windows.Controls import TextBox, TextBlock, ScrollBarVisibility
from System.Windows.Media import FontFamily

class ConsoleTextBox(TextBox):
    def __init__(self, width):
        self.FontSize = 15
        self.Margin = Thickness(0, 0, 0, 0)
        #self.TextWrapping = TextWrapping.Wrap
        self.FontFamily = FontFamily("Consolas, Global Monospace")
        self.TextChanged += self.text_changed
        self.AcceptsReturn = True
        self.BorderThickness = Thickness(0)
        self.VerticalScrollBarVisibility = ScrollBarVisibility.Auto
        self.MinWidth = 200
        self.Width = width

    def OnKeyDown(self, event):
        # needed so that we get KeyDown 
        # for del and backspace events etc
        pass
        
    def text_changed(self, sender, event):
        # replace any tabs that are pasted in
        if '\t' in self.Text:
            self.Text = self.Text.replace('\t', '    ')
            self.SelectionStart = len(self.Text)


def get_console_block():
    block = TextBlock()
    block.FontSize = 15
    block.Margin = Thickness(0, 0, 0, 0)
    block.TextWrapping = TextWrapping.Wrap
    block.FontFamily = FontFamily("Consolas, Global Monospace")
    return block