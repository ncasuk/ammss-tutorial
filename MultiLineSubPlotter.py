import math
import datetime as dt
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from matplotlib.ticker import MultipleLocator

class MultiLineSubplotter:
    """
    Plot a number of subplots each able to contain a multiline timeseries plot.
    It is assumed that each subplot will only have a single unit in the y axis, e.g. only temperature in Kelvin.
    """

    def __init__(self, subplot_size, total_subplots, title, space_between=0.5, time=None, sharey=False, sharex=False):
        """
        Required input:
            subplot_size: tuple representing the size of each subplot
            total_subplots: total number of subplots to be added to figure
            probeid: ID of the station
        Optional Input:
            vertical: True implies vertically stacked subplots, False gives horizontal
            time: Time the data is to be plotted
        """
        
        self.subplot_size = subplot_size
        self.total_subplots = total_subplots
        self.num_subplots = 0
        self.space_between = space_between
        self.sharey = sharey
        
        if not time:
            time = dt.datetime.now(dt.timezone.utc)

        self.axis_num = 0
        self.time = time.strftime('%Y-%m-%d %H:%M UTC')
        self.title = title

    @property
    def figsize(self):
        """ Define in children """
        pass
   
    @property
    def _get_subplot_dims(self):
        """ Define in childen """
        pass
        
    @property
    def fig(self):
        if not hasattr(self, '_fig'):
            self._fig, self._ax = plt.subplots(*self._get_subplot_dims, figsize=self.figsize)
            self._fig.subplots_adjust(wspace=0, hspace=0)
        return self._fig

    @property
    def ax(self):
        if not hasattr(self, '_ax'):
            self._fig, self._ax = plt.subplots(*self._get_subplot_dims, figsize=self.figsize)
        return self._ax

        

        
        
    def add_plot(self, line_data, ylabel=None, xlabel=None, plot_range=None, ystep=None, timeseries=True, legend=False, time_bound=None):
        """
        Required input:
            line_data: list of dicts, each of which contains arguments for matplotlib plotting of a single line
            y_label: Label for shared y axis of each of the lines in line_data
            y_step: y axis label step
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step)), this is worked out programatically other wise
        """

        for line in line_data:
            if np.all(np.isnan(line['y'])):
                print(f"!!!!!!! {line['label']} has invalid data in {ylabel}!!!!!!!")
                line_data.remove(line)
		
            if time_bound:
                lower = np.argmin(np.abs(line['x'] - np.datetime64(time_bound[0])))
                upper = np.argmin(np.abs(line['x'] - np.datetime64(time_bound[1])))
                line['x'] = line['x'][lower:upper+1]
                line['y'] = line['y'][lower:upper+1]

        if plot_range:    
            ymin, ymax = plot_range
        else:
            ymin0 = min([np.nanmin(line['y']) for line in line_data])
            ymax0 = max([np.nanmax(line['y']) for line in line_data])
            ymin = ymin0 - 0.2 * abs(ymax0 - ymin0)
            ymax = ymax0 + 0.2 * abs(ymax0 - ymin0)

        min_time = min(line_data[0]['x']) 

        if not type(min_time) == np.datetime64 and not type(min_time) == dt.datetime:
            xmin0 = min([min(line['x']) for line in line_data])
            xmax0 = max([max(line['x']) for line in line_data])
            xmin = xmin0 - 0.2 * abs(xmin0)
            xmax = xmax0 + 0.2 * abs(xmax0)
        
        if ystep:
            pass
        else:
            logstep = math.log10(abs(ymax - ymin) * 1.1 / 11)
            pow = math.floor(logstep)
            res = logstep - pow
            all_step_res = [1,2,5]
            step_res = all_step_res[np.argmin([abs(10**res - g) for g in all_step_res])]
            ystep = step_res * 10 ** pow
        
        if ystep == 0:
            ystep = abs(ymax- ymin)/10
            
        if self.total_subplots == 1:
             axis_to_plot = self.ax
        else:
             axis_to_plot = self.ax[self.num_subplots]

        lines = [
            axis_to_plot.plot(line['x'],
            line['y'], line['color'],
            linestyle=line['linestyle'],
            marker=line['marker'],
            label=line['label'])[0]
            for line in line_data]

        # Format whole subplot
        
        axis_to_plot.set_ylabel(ylabel, multialignment='center')
        axis_to_plot.set_xlabel(xlabel, multialignment='center')
        axis_to_plot.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        axis_to_plot.grid(which='major', axis='x', color='k', linestyle='--', linewidth=0.5)
        if 'xmin' in locals() and 'xmax' in locals():
            axis_to_plot.set_xlim(xmin, xmax)
        axis_to_plot.set_ylim(ymin, ymax)
        axis_to_plot.yaxis.set_major_locator(MultipleLocator(ystep))
        ax_twin = axis_to_plot.twinx()
        ax_twin.set_ylim(ymin, ymax)
        ax_twin.yaxis.set_major_locator(MultipleLocator(ystep))
        labs = [line.get_label() for line in lines]
        if timeseries:
            ax_twin.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d %H:%M UTC'))
        #axis_to_plotxaxis.set_major_locator(mpl.dates.HourLocator(interval=1))
        
        if legend:
            axis_to_plot.legend(lines, labs, loc='upper center',
                bbox_to_anchor=(0.5, 1.0), ncol=6, prop={'size': 12})
        
        # Increment current subplot number
        self.num_subplots += 1
        self.fig.subplots_adjust(hspace=self.space_between, wspace=self.space_between)
        self._fig.suptitle(self.title, fontsize=16, x='0.5', y='0.95')


class VerticalPlotter(MultiLineSubplotter):

    @property
    def figsize(self):
        return (self.subplot_size[0], self.total_subplots * self.subplot_size[1] + 1)

    @property
    def _get_subplot_dims(self):
        return self.total_subplots, 1

class HorizontalPlotter(MultiLineSubplotter):

    @property
    def figsize(self):
        return (self.total_subplots * self.subplot_size[0], self.subplot_size[1] + 1)

    @property
    def _get_subplot_dims(self):
        return 1, self.total_subplots
