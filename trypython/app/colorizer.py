
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

engine = Python.CreateEngine()
context = HostingHelpers.GetLanguageContext(engine)

def get_source_unit(code):
    return context.CreateSnippet(code, SourceCodeKind.InteractiveCode)

def tokenize(code):
    t = Tokenizer()
    t.Initialize(get_source_unit(code))
    return list(t.ReadTokens(len(code)))

def create_text_run(code, token):
    start = token.SourceSpan.Start.Index
    end = start + token.SourceSpan.Length
    text = code[start:end]
    if not text:
        return
    text = text.replace('\n', '\n... ')
    run = Run()
    run.Text = text
    style = styles.get(token.Category, default_style)
    run.Foreground = style
    #_debug('text run', repr(text), repr(style))
    
    return run

def create_leading_whitespace_run(code, position, token):
    length = token.SourceSpan.Start.Index - position
    whitespace = code[position:position + length] # may need escaping
    if not whitespace:
        return
    run = Run()
    run.Text = whitespace
    return run

def colorize(code):
    results = []
    position = 0
    for token in tokenize(code):
        _debug(token.Category)
        space = create_leading_whitespace_run(code, position, token)
        if space is not None:
            results.append(space)
        if token.Category == TokenCategory.WhiteSpace:
            continue
        text_run = create_text_run(code, token)
        if text_run is not None:
            results.append(text_run)
        position = token.SourceSpan.Start.Index + token.SourceSpan.Length
    return results


if __name__ == '__main__':
    print tokenize('print foo')