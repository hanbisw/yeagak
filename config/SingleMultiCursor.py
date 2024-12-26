class SingleMultiCursor():
    """
    一个用于多个子图（横排或者竖排）的十字星光标，可以在多个子图上同时出现
    single=0表示仅仅一个子图显示水平线，所有子图显示垂直线，用于竖排的子图
    single=1表示仅仅一个子图显示垂直线，所有子图显示水平线，用于横排的子图
    注意：为了能让光标响应事件处理，必须保持对它的引用（比如有个变量保存）
    用法::
        import matplotlib.pyplot as plt
        import numpy as np
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
        t = np.arange(0.0, 2.0, 0.01)
        ax1.plot(t, np.sin(2*np.pi*t))
        ax2.plot(t, np.sin(4*np.pi*t))
        cursor = SingleMultiCursor(fig.canvas, (ax1, ax2), single=0, color='w', lw=0.5)
        plt.show()
    """

    def __init__(self, canvas, axes, single=0, **lineprops):
        self.canvas = canvas
        self.axes = axes
        self.single = single
        if single not in [0, 1]:
            raise ValueError('Unrecognized single value: ' + str(single) + ', must be 0 or 1')

        xmin, xmax = axes[-1].get_xlim()
        ymin, ymax = axes[-1].get_ylim()
        xmid = 0.5 * (xmin + xmax)
        ymid = 0.5 * (ymin + ymax)

        self.background = None
        self.needclear = False

        lineprops['animated'] = True  # for blt

        self.lines = [
            [ax.axhline(ymid, visible=False, **lineprops) for ax in axes],
            [ax.axvline(xmid, visible=False, **lineprops) for ax in axes]
        ]

        self.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.canvas.mpl_connect('draw_event', self.clear)

    def clear(self, event):
        self.background = (self.canvas.copy_from_bbox(self.canvas.figure.bbox))
        for line in self.lines[0] + self.lines[1]:
            line.set_visible(False)

    def onmove(self, event):
        if event.inaxes is None: return
        if not self.canvas.widgetlock.available(self): return

        self.needclear = True

        for i in range(len(self.axes)):
            if event.inaxes == self.axes[i]:
                if self.single == 0:
                    for line in self.lines[1]:
                        line.set_xdata((event.xdata, event.xdata))
                        line.set_visible(True)

                    line = self.lines[0][i]
                    line.set_ydata((event.ydata, event.ydata))
                    line.set_visible(True)
                else:
                    for line in self.lines[0]:
                        line.set_ydata((event.ydata, event.ydata))
                        line.set_visible(True)

                    line = self.lines[1][i]
                    line.set_xdata((event.xdata, event.xdata))
                    line.set_visible(True)
            else:
                self.lines[self.single][i].set_visible(False)

        if self.background is not None:
            self.canvas.restore_region(self.background)

        for lines in self.lines:
            for line in lines:
                if line.get_visible():
                    line.axes.draw_artist(line)

        self.canvas.blit()
# class SingleMultiCursor():
#     """
#     A cross-hair cursor for multiple sub-pictures (horizontal or vertical), which can appear on multiple sub-pictures at the same time
#          single=0 means that only one sub-picture displays horizontal lines, all sub-pictures display vertical lines, used for vertical sub-pictures
#          single=1 means that only one sub-picture displays vertical lines, all sub-pictures display horizontal lines, which is used for horizontal sub-pictures
#          Note: In order for the cursor to respond to event processing, a reference to it must be maintained (for example, a variable is saved)
#          usage::
#         import matplotlib.pyplot as plt
#         import numpy as np
#         fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
#         t = np.arange(0.0, 2.0, 0.01)
#         ax1.plot(t, np.sin(2*np.pi*t))
#         ax2.plot(t, np.sin(4*np.pi*t))
#         cursor = SingleMultiCursor(fig.canvas, (ax1, ax2), single=0, color='w', lw=0.5)
#         plt.show()
#     """
#
#     def __init__(self, canvas, axes, single=0, **lineprops):
#         self.canvas = canvas
#         self.axes = axes
#         self.single = single
#         if single not in [0, 1]:
#             raise ValueError('Unrecognized single value: ' + str(single) + ', must be 0 or 1')
#
#         xmin, xmax = axes[-1].get_xlim()
#         # print(axes[-1].get_xlim())
#         ymin, ymax = axes[-1].get_ylim()
#
#         xmid = 0.5 * (xmin + xmax)
#         ymid = 0.5 * (ymin + ymax)
#
#         self.background = None
#         self.needclear = False
#
#         lineprops['animated'] = True  # for blt
#
#         self.lines = [
#             [ax.axhline(ymid, visible=False, **lineprops) for ax in axes],
#             [ax.axvline(xmid, visible=False, **lineprops) for ax in axes]
#         ]
#         #그래프가 사이
#         self.canvas.mpl_connect('motion_notify_event', self.onmove)
#         self.canvas.mpl_connect('draw_event', self.clear)
#
#     def clear(self, event):
#         self.background = (self.canvas.copy_from_bbox(self.canvas.figure.bbox))
#         for line in self.lines[0] + self.lines[1]:
#             line.set_visible(False)
#
#     def onmove(self, event):
#         if event.inaxes is None: return
#         if not self.canvas.widgetlock.available(self): return
#
#         self.needclear = True
#
#         for i in range(len(self.axes)):
#             if event.inaxes == self.axes[i]:
#                 if self.single == 0:
#                     for line in self.lines[1]:
#                         line.set_xdata((event.xdata, event.xdata))
#                         line.set_visible(True)
#
#                     line = self.lines[0][i]
#                     line.set_ydata((event.ydata, event.ydata))
#                     line.set_visible(True)
#                 else:
#                     for line in self.lines[0]:
#                         line.set_ydata((event.ydata, event.ydata))
#                         line.set_visible(True)
#
#                     line = self.lines[1][i]
#                     line.set_xdata((event.xdata, event.xdata))
#                     line.set_visible(True)
#             else:
#                 self.lines[self.single][i].set_visible(False)
#
#         if self.background is not None:
#             self.canvas.restore_region(self.background)
#
#         for lines in self.lines:
#             for line in lines:
#                 if line.get_visible():
#                     line.axes.draw_artist(line)
#
#         self.canvas.blit()