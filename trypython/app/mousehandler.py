
class MouseHandler(object):
    def __init__(self, scrollers):
        self.position = None
        self.scrollers = scrollers
    
    def on_mouse_move(self, sender, event):
        self.position = event.GetPosition(None)
    
    def on_mouse_wheel(self, sender, event):
        delta = 0
        e = event.EventObject
        if e.GetProperty("detail"):
            delta = e.GetProperty("detail")
        elif e.GetProperty("wheelDelta"):
            delta = -e.GetProperty("wheelDelta")
        delta = Math.Sign(delta) * 40
        
        for scroller in self.scrollers:
            if self.mouse_over(scroller):
                e.SetProperty('cancel', True)
                e.SetProperty('cancelBubble', True)
                e.SetProperty('returnValue', False)
                if e.GetProperty('preventDefault'):
                    e.Invoke('preventDefault')
                elif e.GetProperty('stopPropagation'):
                    e.Invoke('stopPropagation')
                scroller.ScrollToVerticalOffset(scroller.VerticalOffset + delta)
                return


    def mouse_over(self, scroller):
        minX, maxX, minY, maxY = self.get_element_coords(scroller)
        return ((minX <= self.position.X <= maxX) and
                (minY <= self.position.Y <= maxY))


    def get_element_coords(self, element):
        transform = element.TransformToVisual(root)
        topleft = transform.Transform(Point(0, 0))
        minX = topleft.X
        minY = topleft.Y
        maxX = minX + element.RenderSize.Width
        maxY = minY + element.RenderSize.Height
        return minX, maxX, minY, maxY
