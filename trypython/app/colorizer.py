
from IronPython.Hosting import Python
from IronPython.Compiler import Tokenizer
from Microsoft.Scripting.Hosting.Providers import HostingHelpers
from Microsoft.Scripting import SourceCodeKind, TokenCategory

from System.Windows.Documents import Run
from System.Windows.Media import Color, SolidColorBrush

from utils import _debug


styles = {
    TokenCategory.NumericLiteral: SolidColorBrush(Color.FromArgb(255, 102, 102, 102)), 
    TokenCategory.Operator: SolidColorBrush(Color.FromArgb(255, 102, 102, 102)), 
    TokenCategory.Keyword: SolidColorBrush(Color.FromArgb(255, 0, 128, 0)), 
    TokenCategory.Identifier: SolidColorBrush(Color.FromArgb(255, 25, 23, 124)), 
    TokenCategory.StringLiteral: SolidColorBrush(Color.FromArgb(255, 186, 33, 33)),
    TokenCategory.Comment: SolidColorBrush(Color.FromArgb(255, 64, 128, 128)),
    TokenCategory.Error: SolidColorBrush(Color.FromArgb(255, 255, 0, 0)), 
    TokenCategory.None: SolidColorBrush(Color.FromArgb(255, 255, 255, 255)), 
}

default_style = SolidColorBrush(Color.FromArgb(255, 0, 0, 0))
blue = SolidColorBrush(Color.FromArgb(255, 0, 0, 128))

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


def text_from_token(code, token):
    start = token.SourceSpan.Start.Index
    end = start + token.SourceSpan.Length
    return code[start:end]


def create_text_run(code, token, ps2):
    text = text_from_token(code, token)
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


def extra_newline(token, previous_token, code):
    # should only be true at the end of a class definition
    # HACK!!
    if previous_token is None:
        return False
    if (token.Category != TokenCategory.Operator) or (previous_token.Category != TokenCategory.Operator):
        return False
    current = text_from_token(code, token).rstrip(' ')
    previous = text_from_token(code, previous_token).rstrip(' ')
    if (current, previous) == ('\n', '\n'):
        return True
    return False


def colorize(code, ps1, ps2):
    results = [get_prompt(ps1)]
    position = 0
    count_newlines = 0
    previous_token = None
    for token in tokenize(code):
        _debug(token.Category)
        if extra_newline(token, previous_token, code):
            position = token.SourceSpan.Start.Index + token.SourceSpan.Length
            continue
                
        results.extend(create_leading_whitespace_run(code, position, token, ps2))
        if token.Category == TokenCategory.WhiteSpace:
            continue
        position = token.SourceSpan.Start.Index + token.SourceSpan.Length
        results.extend(create_text_run(code, token, ps2))
        previous_token = token
    return results

