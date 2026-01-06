"""
FlowLayout - 流式布局，支持自适应排列
"""
from PyQt6.QtWidgets import QLayout, QWidgetItem
from PyQt6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """流式布局类，根据窗口宽度自动排列子部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_list = []
        self._h_spacing = -1
        self._v_spacing = -1
        
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        """添加项目"""
        self._item_list.append(item)
    
    def horizontalSpacing(self):
        """获取水平间距"""
        if self._h_spacing >= 0:
            return self._h_spacing
        else:
            return self.smartSpacing(Qt.Orientation.Horizontal)
    
    def verticalSpacing(self):
        """获取垂直间距"""
        if self._v_spacing >= 0:
            return self._v_spacing
        else:
            return self.smartSpacing(Qt.Orientation.Vertical)
    
    def setSpacing(self, spacing):
        """设置间距"""
        self._h_spacing = spacing
        self._v_spacing = spacing
    
    def count(self):
        """返回项目数量"""
        return len(self._item_list)
    
    def itemAt(self, index):
        """获取指定索引的项目"""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None
    
    def takeAt(self, index):
        """移除并返回指定索引的项目"""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None
    
    def expandingDirections(self):
        """返回扩展方向"""
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        """是否有高度随宽度变化"""
        return True
    
    def heightForWidth(self, width):
        """根据宽度计算高度"""
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        """设置几何形状"""
        super().setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        """返回建议大小"""
        return self.minimumSize()
    
    def minimumSize(self):
        """返回最小大小"""
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), 
                     margins.top() + margins.bottom())
        return size
    
    def doLayout(self, rect, test_only):
        """执行布局"""
        x = rect.x()
        y = rect.y()
        line_height = 0
        
        h_spacing = self.horizontalSpacing()
        v_spacing = self.verticalSpacing()
        
        for item in self._item_list:
            widget = item.widget()
            space_x = h_spacing
            if space_x == -1:
                space_x = widget.style().layoutSpacing(
                    widget.sizePolicy().controlType(),
                    widget.sizePolicy().controlType(),
                    Qt.Orientation.Horizontal
                )
            
            space_y = v_spacing
            if space_y == -1:
                space_y = widget.style().layoutSpacing(
                    widget.sizePolicy().controlType(),
                    widget.sizePolicy().controlType(),
                    Qt.Orientation.Vertical
                )
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()
    
    def smartSpacing(self, orientation):
        """智能间距"""
        parent = self.parent()
        if not parent:
            return -1
        
        if parent.isWidgetType():
            return parent.style().pixelMetric(
                parent.style().PixelMetric.PM_LayoutHorizontalSpacing
                if orientation == Qt.Orientation.Horizontal
                else parent.style().PixelMetric.PM_LayoutVerticalSpacing,
                None,
                parent
            )
        else:
            return parent.spacing()
