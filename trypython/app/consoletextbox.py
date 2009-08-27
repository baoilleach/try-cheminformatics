from System.Windows import Thickness, TextWrapping
from System.Windows.Controls import TextBox
from System.Windows.Media import FontFamily

class ConsoleTextBox(TextBox):
    def __init__(self):
        self.FontSize = 15
        self.Margin = Thickness(5, 5, 5, 5)
        self.TextWrapping = TextWrapping.Wrap
        self.FontFamily = FontFamily("Consolas, Global Monospace")
        self.TextChanged += self.text_changed
        self.AcceptsReturn = True

    def OnKeyDown(self, event):
        # needed so that we get KeyDown 
        # for del and backspace events etc
        pass
        
    def text_changed(self, sender, event):
        # replace any tabs that are pasted in
        if '\t' in self.Text:
            self.Text = self.Text.replace('\t', '    ')
            self.SelectionStart = len(self.Text)
