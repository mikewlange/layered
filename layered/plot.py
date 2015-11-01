import collections
import warnings
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook


warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)


class Plot:

    def __init__(self, refresh=0.1, width=1000):
        self.refresh = refresh
        self.width = width
        self.data = collections.deque([None] * self.width, maxlen=width)
        self.max = 0
        self._init_style()
        self._init_update()

    def __call__(self, cost):
        cost = cost.sum()
        self.max = max(self.max, cost)
        with self.lock:
            self.data.append(cost)
            self.li.set_ydata(self.data)

    def _init_plot(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, xlabel='Example',
            ylabel='Cost')
        self.li, = self.ax.plot(np.arange(self.width), self.data,
            **self.style)
        self.fig.canvas.draw()
        plt.show(block=False)
        self.ax.set_xlim(0, self.width)

    def _init_update(self):
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._update)
        self.thread.start()

    def _init_style(self):
        self.style = {
            'linestyle': '',
            'color': 'blue',
            'marker': '.',
            'markersize': 2
        }

    def _update(self):
        with self.lock:
            self._init_plot()
        while True:
            before = time.time()
            with self.lock:
                self.ax.set_ylim(0, self.max)
                self.fig.canvas.draw()
            duration = time.time() - before
            plt.pause(max(0, self.refresh - duration))
