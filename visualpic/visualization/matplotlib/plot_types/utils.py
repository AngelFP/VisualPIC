import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from matplotlib import ticker
from matplotlib.colorbar import Colorbar


def add_projection(x, bins, main_ax, subplot_spec, fig,
                   orientation='horizontal'):
    """Add an axis projection to a particle plot."""
    x_proj, x_bins = np.histogram(x, bins=bins)
    x_pos = x_bins[1:] - (x_bins[1]-x_bins[0])

    if orientation == 'horizontal':
        gs_p = gs.GridSpecFromSubplotSpec(
            2, 1, subplot_spec, height_ratios=[1, 0.2])
        ax_p = fig.add_subplot(gs_p[-1])
    elif orientation == 'vertical':
        gs_p = gs.GridSpecFromSubplotSpec(
            1, 2, subplot_spec, width_ratios=[0.2, 1])
        ax_p = fig.add_subplot(gs_p[0])

    ax_p.patch.set_alpha(0)

    if orientation == 'horizontal':
        ax_p.plot(x_pos, x_proj, c='k', lw=0.5, alpha=0.5)
        ax_p.fill_between(x_pos, x_proj, facecolor='tab:gray',
                          alpha=0.3)
        xlim = main_ax.get_xlim()
        ax_p.set_xlim(xlim)
        ylim = list(ax_p.get_ylim())
        ylim[0] = 0
        ax_p.set_ylim(ylim)
    elif orientation == 'vertical':
        ax_p.plot(x_proj, x_pos, c='k', lw=0.5, alpha=0.5)
        ax_p.fill_betweenx(x_pos, x_proj, facecolor='tab:gray',
                           alpha=0.3)
        ylim = main_ax.get_ylim()
        ax_p.set_ylim(ylim)
        xlim = list(ax_p.get_xlim())
        xlim[0] = 0
        ax_p.set_xlim(xlim)
    ax_p.axis('off')
    # ax_p.spines['left'].set_position('zero')
    # ax_p.spines['left'].set_color('tab:grey')
    # ax_p.tick_params(axis='y', colors='tab:grey', labelsize=6,
    #                 direction="in", pad=-4)
    # ax_p.spines['right'].set_color('none')
    # ax_p.spines['top'].set_color('none')
    # ax_p.yaxis.set_ticks_position('left')
    # ax_p.xaxis.set_ticks_position('bottom')
    # ax_p.tick_params(axis='x', which='both', labelbottom=False)
    # for label in ax_p.yaxis.get_ticklabels():
    #     label.set_horizontalalignment('left')
    #     label.set_verticalalignment('bottom')


def create_vertical_colorbars(images, labels, subplot_spec, fig=None,
                              n_ticks=3, **kwargs):
    """Create vertical colorbars in existing subplot spec."""
    if not isinstance(images, list):
        images = [images]
    if not isinstance(labels, list):
        labels = [labels]
    n_cbars = len(images)
    cbar_gs = gs.GridSpecFromSubplotSpec(
        n_cbars, 1, subplot_spec=subplot_spec, **kwargs)
    if fig is None:
        fig = plt.gcf()
    for image, label, cbar_ss in zip(images, labels, cbar_gs):
        ax = fig.add_subplot(cbar_ss)
        tick_locator = ticker.MaxNLocator(nbins=n_ticks)
        Colorbar(ax, image, ticks=tick_locator, label=label)
