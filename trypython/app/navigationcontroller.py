from __future__ import with_statement

from System.Windows.Browser import HtmlPage
from System.Windows.Controls import StackPanel, ComboBoxItem
from System.Windows.Markup import XamlReader

from utils import _debug


_xaml_cache = {}


class NavigationController(object):
    
    def __init__(self, root, focus_text_box):
        self.focus_text_box = focus_text_box
        self.root = root
        
        self.topComboBoxPage = root.topComboBoxPage
        self.bottomComboBoxPage = root.bottomComboBoxPage
        self.topComboBoxPart = root.topComboBoxPart
        self.bottomComboBoxPart = root.bottomComboBoxPart
        self.documentContainer = root.document.Child
        
        root.topFirst.Click += self.first
        root.bottomFirst.Click += self.first
        root.topLast.Click += self.last
        root.bottomLast.Click += self.last
        root.topNext.Click += self.next
        root.bottomNext.Click += self.next
        root.topPrev.Click += self.prev
        root.bottomPrev.Click += self.prev
    
        self.event_pairs = [
            (self.bottomComboBoxPart.SelectionChanged, self.on_change_bottom_part),
            (self.topComboBoxPart.SelectionChanged, self.on_change_top_part),
            (self.topComboBoxPage.SelectionChanged, self.on_change_top_page),
            (self.bottomComboBoxPage.SelectionChanged, self.on_change_bottom_page)
        ]
    
    
    def invoke(self, function):
        self.root.Dispatcher.BeginInvoke(function)


    def setup_parts(self):
        with open('docs/list.txt') as handle:
            items = handle.readlines()

        topCombobox = self.topComboBoxPart
        bottomComboBox = self.bottomComboBoxPart
        
        items = ['Index'] + items
        for combobox in topCombobox, bottomComboBox:
            for item in items:
                boxitem = ComboBoxItem()
                boxitem.Content = item
                boxitem.Height = 25
                combobox.Items.Add(boxitem)
        
        topCombobox.SelectionChanged += self.on_change_top_part
        bottomComboBox.SelectionChanged += self.on_change_bottom_part
        
        topCombobox.SelectedIndex = bottomComboBox.SelectedIndex = 0
        
    
    def unhook_events(self):
        for event, method in self.event_pairs:
            event += method
        
            
    def hook_events(self):
        for event, method in self.event_pairs:
            event -= method
        
    
    def change_document(self, part, page):
        if page == -1:
            return
        fragment = ''
        item = 'index.xaml'
        loc = 'docs/'
        if part > 0:
            # page can be -1
            if page > 0:
                item = 'item%s.xaml' % page
            loc += 'part%s/' % part
            fragment = 'part%s-page%s' % (part, page)
        
        path = loc + item
        HtmlPage.Window.CurrentBookmark = fragment
        
        if path in _xaml_cache:
            document = _xaml_cache[path]
        else:
            with open(path) as handle:
                xaml = handle.read().decode('utf-8')
            document = XamlReader.Load(xaml)
            _xaml_cache[path] = document
        
        self.documentContainer.Content = document
        self.documentContainer.ScrollToVerticalOffset(0)
        self.focus_text_box()

    
    def on_change_top_part(self, sender, event):
        index = self.topComboBoxPart.SelectedIndex
        self.unhook_events()
        self.bottomComboBoxPart.SelectedIndex = index
        self.change_pages()
        self.change_document(index, 0)
        self.hook_events()
        
        
    def on_change_bottom_part(self, sender, event):
        index = self.bottomComboBoxPart.SelectedIndex
        self.unhook_events()
        self.topComboBoxPart.SelectedIndex = index
        self.change_pages()
        self.change_document(index, 0)
        self.hook_events()
    
    
    def change_pages(self):
        self.unhook_events()
        part = self.topComboBoxPart.SelectedIndex
        
        self.unhook_events()
        self.topComboBoxPage.Items.Clear()
        self.bottomComboBoxPage.Items.Clear()
        if part == 0:
            return
        
        with open('docs/part%s/list.txt' % part) as handle:
            items = handle.readlines()

        topCombobox = self.topComboBoxPage
        bottomComboBox = self.bottomComboBoxPage
        
        items = ['Index'] + items
        for combobox in topCombobox, bottomComboBox:
            for item in items:
                boxitem = ComboBoxItem()
                boxitem.Content = item
                boxitem.Height = 25
                combobox.Items.Add(boxitem)
        
        self.topComboBoxPage.SelectedIndex = 0
        self.bottomComboBoxPage.SelectedIndex = 0
        self.hook_events()
        
    
    def on_change_top_page(self, sender, event):
        _debug('change_top')
        part = self.topComboBoxPart.SelectedIndex
        page = self.topComboBoxPage.SelectedIndex
        
        self.unhook_events()
        self.bottomComboBoxPage.SelectedIndex = page
        self.change_document(part, page)
        self.hook_events()

    
    def on_change_bottom_page(self, sender, event):
        _debug('change_bottom')
        part = self.bottomComboBoxPart.SelectedIndex
        page = self.bottomComboBoxPage.SelectedIndex
        
        self.unhook_events()
        self.topComboBoxPage.SelectedIndex = page
        self.change_document(part, page)
        self.hook_events()
    
    
    def next(self, sender, event):
        part = self.topComboBoxPart.SelectedIndex
        page = self.topComboBoxPage.SelectedIndex
        
        if page < len(self.topComboBoxPage.Items) - 1:
            self.topComboBoxPage.SelectedIndex += 1
        elif part < len(self.topComboBoxPart.Items) - 1:
            self.topComboBoxPart.SelectedIndex += 1
    
    
    def prev(self, sender, event):
        part = self.topComboBoxPart.SelectedIndex
        page = self.topComboBoxPage.SelectedIndex
        
        if page > 0:
            self.topComboBoxPage.SelectedIndex -= 1
        elif part > 0:
            self.topComboBoxPart.SelectedIndex -= 1
            if part > 1:
                with open('docs/part%s/list.txt' % part) as handle:
                    index = len(handle.readlines()) - 1
                self.topComboBoxPage.SelectedIndex = index
    
    
    def first(self, sender, event):
        if self.topComboBoxPart.SelectedIndex > 0:
            self.topComboBoxPage.SelectedIndex = 0
    
    
    def last(self, sender, event):
        if self.topComboBoxPart.SelectedIndex > 0:
            self.topComboBoxPage.SelectedIndex = len(self.topComboBoxPage.Items) - 1


"""
page = 0
bookmark = HtmlPage.Window.CurrentBookmark.lower()
if bookmark.startswith('page'):
    try:
        page = int(bookmark[4:])
    except ValueError:
        pass
    else:
        page = min((page - 1), len(combobox.Items) - 1)
        page = max(page, 0)
        
topCombobox.SelectedIndex = page
"""