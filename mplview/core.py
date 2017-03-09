__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Nov 01, 2016 9:19$"


import matplotlib as mpl
import matplotlib.figure
import matplotlib.colors

from matplotlib.widgets import Slider, Button, SpanSelector

from npctypes.types import tinfo


class MatplotlibViewer(matplotlib.figure.Figure):
    """
        Provides a way to interact with numpy arrays pulled from neuron images.

        Wraps a Matplotlib figure instance.
    """


    def __init__(self, *args, **kwargs):
        """
            Initializes a MatplotlibViewer using the given figure to
            clone and image stack to view.

            After cloning, self will be the same as fig. Additional features
            will be attached to self.

            Args:
                args(list):         arguments to be passed to parent

            Keyword Args:
                kwargs(dict):       arguments to be passed to parent
        """

        super(MatplotlibViewer, self).__init__(*args, **kwargs)

        self.subplots_adjust(left=0.25, bottom=0.25)
        self.viewer = self.add_axes([0.25, 0.25, 0.7, 0.7])


    def set_images(self,
                   new_neuron_images,
                   cmap=mpl.cm.Greys_r,
                   use_matshow=False,
                   vmin=None,
                   vmax=None):
        """
            Sets the images to be viewed.

            Args:
                new_neuron_images(numpy.ndarray):     array of images (first
                                                      index is which image)
        """
        if (len(new_neuron_images.shape) > 3):
            raise ValueError(
                "Dimensions cannot be greater than 3. " +
                "Was provided new_neuron_images with \"" +
                str(len(new_neuron_images.shape)) + "\" dimensions."
            )

        self.neuron_images = new_neuron_images
        self.cmap = cmap
        self.vmin = vmin
        self.vmax = vmax

        type_info = tinfo(new_neuron_images.dtype)
        if self.vmin is None:
           self.vmin = type_info.min
        if self.vmax is None:
           self.vmax = type_info.max

        self.svmin = self.vmin
        self.svmax = self.vmax

        viewer_show_method = None
        if use_matshow:
            viewer_show_method = self.viewer.matshow
        else:
            viewer_show_method = self.viewer.imshow

        self.image_view = viewer_show_method(
            self.get_image(0),
            cmap=self.cmap,
            vmin=self.vmin,
            vmax=self.vmax
        )

        self.image_view_colorbar = self.colorbar(
            self.image_view, ax=self.viewer)

        self.image_view_colorbar_selector = SpanSelector(
            self.image_view_colorbar.ax,
            self.color_range_update, 'vertical',
            useblit=True,
            rectprops=dict(alpha=0.3, facecolor='yellow')
        )

        if (len(self.neuron_images.shape) == 3):
            self.time_nav = SequenceNavigator(self, len(self.neuron_images) - 1)

            self.time_nav_cid = self.time_nav.on_time_update(self.time_update)

        self.viewer.format_coord = self.format_coord


    def get_image(self, i=None):
        """
            Gets the current image or the image if it is a projection.

            Args:
                i(int):             image to retrieve (defaults to selection).

            Returns:
                numpy.ndarray:      the current image.
        """

        cur_img = self.neuron_images
        if (len(self.neuron_images.shape) == 3):
            i = self.time_nav.stime.val if i is None else i
            cur_img = cur_img[i]
        else:
            cur_img = cur_img[...]

        cur_img = cur_img[...]

        cur_img = cur_img.astype(float)

        return(cur_img)


    def color_range_update(self, vmin, vmax):
        """
            Handles an update to the vmin and vmax range based on the selection
            provided.

            Args:
                vmin         the min value selected
                vmax         the max value selected
        """
        if vmin != vmax:
            svdiff = self.svmax - self.svmin

            svmin = svdiff * vmin + self.svmin
            svmax = svdiff * vmax + self.svmin

            self.svmin = svmin
            self.svmax = svmax
        else:
            self.svmin = self.vmin
            self.svmax = self.vmax

        norm = matplotlib.colors.Normalize(self.svmin, self.svmax)
        self.image_view_colorbar.set_norm(norm)
        self.image_view.set_norm(norm)

        self.canvas.draw_idle()


    def time_update(self):
        """
            Method to be called by the SequenceNavigator when the time changes.
            Updates image displayed.
        """
        if (len(self.neuron_images.shape) == 3):
            self.image_view.set_array(self.get_image())
            self.canvas.draw_idle()


    def format_coord(self, x, y):
        """
            Include intensity when showing coordinates during mouseover.

            Args:
                x(float):    cursor's x position within the image.
                y(float):    cursor's y position within the image.

            Returns:
                str:         coordinates and intensity if it can be gotten.
        """
        try:
            xi = int(round(x))
            yi = int(round(y))

            z = self.get_image()[yi, xi]

            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
        except:
            return 'x=%1.4f, y=%1.4f'%(x, y)


class SequenceNavigator(object):
    def __init__(self,
                 fig,
                 max_time,
                 min_time=0,
                 time_step=1,
                 axcolor='lightgoldenrodyellow',
                 hovercolor='0.975'):
        """
            Initializes a SequenceNavigator using the given figure and a fixed
            number of steps.

            Provides a simple slider bar and buttons to navigate through time.

            Args:
                fig         should be a figure that has been initialized.
                max_time    maximum step for images.
                min_time    minimum step for images.
                time_step   how much to increase/decrease by for each step.
                axcolor     color to be used for all buttons and slider bar.
                hovercolor  color turned when mouse over occurs for any button.
        """

        self.min_time = min_time
        self.max_time = max_time
        self.time_step = time_step
        self.axcolor = axcolor
        self.hovercolor = hovercolor

        self.next_cid = 0

        self.axtime = fig.add_axes(
            [0.25, 0.1, 0.65, 0.03], axisbg=self.axcolor)
        self.stime = Slider(
            self.axtime,
            'Time',
            self.min_time,
            self.max_time,
            valinit=self.min_time,
            valfmt='%i'
        )

        self.stime.on_changed(self.time_update)

        self.beginax = fig.add_axes([0.2, 0.025, 0.1, 0.04])
        self.begin_button = Button(
            self.beginax,
            'Begin',
            color=self.axcolor,
            hovercolor=self.hovercolor
        )
        self.begin_button.on_clicked(self.begin_time)

        self.prevax = fig.add_axes([0.3, 0.025, 0.1, 0.04])
        self.prev_button = Button(
            self.prevax, 'Prev', color=self.axcolor, hovercolor=self.hovercolor
        )
        self.prev_button.on_clicked(self.prev_time)

        self.nextax = fig.add_axes([0.7, 0.025, 0.1, 0.04])
        self.next_button = Button(
            self.nextax, 'Next', color=self.axcolor, hovercolor=self.hovercolor
        )
        self.next_button.on_clicked(self.next_time)

        self.endax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
        self.end_button = Button(
            self.endax, 'End', color=self.axcolor, hovercolor=self.hovercolor
        )
        self.end_button.on_clicked(self.end_time)

        self.callbacks = {}


    def begin_time(self, event):
        """
            Sets time to min_time.

            Args:
                event   Matplotlib event that caused the call to this callback.
        """

        self.time_update(self.min_time)

        assert (self.min_time == self.stime.val)


    def prev_time(self, event):
        """
            Sets time to one time_step prior.

            Args:
                event   Matplotlib event that caused the call to this callback.
        """

        self.time_update(self.stime.val - self.time_step)


    def next_time(self, event):
        """
            Sets time to one time_step after.

            Args:
                event   Matplotlib event that caused the call to this callback.
        """

        self.time_update(self.stime.val + self.time_step)


    def end_time(self, event):
        """
            Sets time to max_time.

            Args:
                event   Matplotlib event that caused the call to this callback.
        """

        self.time_update(self.max_time)

        assert (self.max_time == self.stime.val)


    def normalize_val(self, val):
        """
            Takes the time value and normalizes it to fit within the range.
            Then, makes sure it is a discrete number of steps from the
            min_time.

            Args:
                val     float position from the slider bar to correct

            Returns:
                int:    the normalized value.
        """

        if val < self.min_time:
            return(self.min_time)
        elif val > self.max_time:
            return(self.max_time)
        else:
            return(int(round((val - self.min_time) / self.time_step)))


    def time_update(self, val):
        """
            Takes the time value and normalizes it within the range if it does
            not fit.

            Args:
                val     float position from slider bar to move to
        """

        val = self.normalize_val(val)

        if val != self.stime.val:
            self.stime.set_val(val)

            for each_cid, each_callback in self.callbacks.items():
                each_callback()


    def disconnect(self, cid):
        """
            Disconnects the given cid from being notified of time updates.

            Args:
                cid     ID of callback to pull
        """

        del self.callbacks[cid]


    def on_time_update(self, func):
        """
            Registers a callback function for notification when the time is
            updated.

            Args:
                func(callable):     function call when the time is updated

            Returns:
                int:                a callback ID or cid to allow pulling the
                                    callback when no longer necessary.
        """

        cid = self.next_cid
        self.next_cid += 1

        self.callbacks[cid] = func

        return(cid)
