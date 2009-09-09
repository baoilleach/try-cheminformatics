import clr
clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')

from IronPython.Hosting import Python
from IronPython.Compiler import Tokenizer
from Microsoft.Scripting.Hosting.Providers import HostingHelpers
from Microsoft.Scripting import SourceCodeKind, TokenCategory

styles = {
    TokenCategory.NumericLiteral: "#FFEE98",
    TokenCategory.Keyword: "#FF6600",
    TokenCategory.Identifier: "#FFCC00",
    TokenCategory.StringLiteral: "#66FF00",
    TokenCategory.Comment: "#9933CC",
    TokenCategory.Error: "#FF0000",
    TokenCategory.None: "#FFFFFF"
}

default_style = styles[TokenCategory.None]

engine = Python.CreateEngine()
context = HostingHelpers.GetLanguageContext(engine)

def get_source_unit(code):
    return context.CreateSnippet(code, SourceCodeKind.InteractiveCode)

def tokenize(code):
    t = Tokenizer()
    t.Initialize(get_source_unit(code))
    return list(t.ReadTokens(len(code)))

def create_text_run(code, token):
    run = Run()
    start = token.SourceSpan.Start.Index
    end = start + token.SourceSpan.Length
    text = code[start:end]
    run.Text = code
    style = styles.get(token.Category, default_style)

"""
        private static Run CreateTextRun(string code, TokenInfo token) {
            var text = code.Substring();
            
            var result = new Run(text);
            var style = _colorizationStyles.ContainsKey(token.Category) ? _colorizationStyles[token.Category] : _colorizationStyles[TokenCategory.None];
            result.Style = Application.Current.FindResource(style) as Style;
            return result;

        }

        private static Run CreateLeadingWhitespaceRun(string code, int position, TokenInfo token) {
            var text = code.Substring(position, token.SourceSpan.Start.Index - position);
            return new Run(text);
        }

        public static List<Run> Colorize(DlrEngine engine, string code, Action<Run, TokenInfo> proc) {
            var result = new List<Run>();
            int position = 0;
            foreach (TokenInfo token in engine.GetTokenInfos(code)) {
                result.Add(CreateLeadingWhitespaceRun(code, position, token));
                var run = CreateTextRun(code, token);
                if (proc != null)
                    proc(run, token);
                result.Add(run);
                position = token.SourceSpan.Start.Index + token.SourceSpan.Length;
            }
            return result;
        }

        public static List<Run> ColorizeErrors(string error) {
            var result = new List<Run>();
            var run = new Run(error);
            run.Style = Application.Current.FindResource("Error") as Style;
            result.Add(run);
            return result;
        }
    }
}
"""
if __name__ == '__main__':
    print tokenize('print foo')