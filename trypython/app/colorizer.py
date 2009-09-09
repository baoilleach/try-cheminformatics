
from IronPython.Hosting import Python
from IronPython.Compiler import Tokenizer
from Microsoft.Scripting.Hosting.Providers import HostingHelpers
from Microsoft.Scripting import SourceCodeKind, TokenCategory

from System.Windows.Documents import Run
from System.Windows.Media import Color, SolidColorBrush

from utils import _debug


styles = {
    TokenCategory.NumericLiteral: SolidColorBrush(Color.FromArgb(255, 255, 238, 152)), #"#FFEE98",
    TokenCategory.Keyword: SolidColorBrush(Color.FromArgb(255, 255, 102, 0)), #"#FF6600",
    TokenCategory.Identifier: SolidColorBrush(Color.FromArgb(255, 255, 204, 0)), #"#FFCC00",
    TokenCategory.StringLiteral: SolidColorBrush(Color.FromArgb(255, 102, 255, 0)), #"#66FF00",
    TokenCategory.Comment: SolidColorBrush(Color.FromArgb(255, 153, 51, 204)), #"#9933CC",
    TokenCategory.Error: SolidColorBrush(Color.FromArgb(255, 255, 0, 0)), #"#FF0000",
    TokenCategory.None: SolidColorBrush(Color.FromArgb(255, 255, 255, 255)), #"#FFFFFF"
}

default_style = SolidColorBrush(Color.FromArgb(255, 0, 0, 0))
blue = SolidColorBrush(Color.FromArgb(255, 0, 0, 255))

engine = Python.CreateEngine()
context = HostingHelpers.GetLanguageContext(engine)


def get_prompt(prompt):
    run = Run()
    run.Text = prompt
    run.Foreground = blue
    return run

def get_run(text, foreground):
    run = Run()
    run.Text = text
    if foreground is not None:
        run.Foreground = foreground
    return run

def runs_from_lines(text, ps2, foreground=None):
    lines = text.split('\n')
    runs = []

    if lines[0]:
        runs.append(get_run(lines[0], foreground))
    for line in lines[1:]:
        runs.append(get_run('\n' + ps2, blue))
        if line:
            runs.append(get_run(line, foreground))
    
    return runs
                

def get_source_unit(code):
    return context.CreateSnippet(code, SourceCodeKind.InteractiveCode)

def tokenize(code):
    tokenizer = Tokenizer()
    tokenizer.Initialize(get_source_unit(code))
    return list(tokenizer.ReadTokens(len(code)))

def create_text_run(code, token, ps2):
    start = token.SourceSpan.Start.Index
    end = start + token.SourceSpan.Length
    text = code[start:end]
    if not text:
        return []
    
    style = styles.get(token.Category, default_style)
    return runs_from_lines(text, ps2, style)


def create_leading_whitespace_run(code, position, token, ps2):
    length = token.SourceSpan.Start.Index - position
    whitespace = code[position:position + length]
    if not whitespace:
        return []
    return runs_from_lines(whitespace, ps2)

def colorize(code, ps1, ps2):
    results = [get_prompt(ps1)]
    position = 0
    for token in tokenize(code):
        results.extend(create_leading_whitespace_run(code, position, token, ps2))
        position = token.SourceSpan.Start.Index + token.SourceSpan.Length
        if token.Category == TokenCategory.WhiteSpace:
            continue
        results.extend(create_text_run(code, token, ps2))
    return results


if __name__ == '__main__':
    print tokenize('print foo')