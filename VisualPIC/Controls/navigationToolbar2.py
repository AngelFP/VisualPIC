import os
import matplotlib
import matplotlib.cbook as cbook
import six
from matplotlib.widgets import SubplotTool
from matplotlib.backends.qt_editor.formsubplottool import UiSubplotTool
from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets, _getSaveFileName
import matplotlib.backends.qt_editor.figureoptions as figureoptions

class Cursors:
    # this class is only used as a simple namespace
    HAND, POINTER, SELECT_REGION, MOVE = list(range(4))
cursors = Cursors()

DEBUG = False

cursord = {
    cursors.MOVE: QtCore.Qt.SizeAllCursor,
    cursors.HAND: QtCore.Qt.PointingHandCursor,
    cursors.POINTER: QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION: QtCore.Qt.CrossCursor,
    }
    
class SubplotToolQt(SubplotTool, UiSubplotTool):
    def __init__(self, targetfig, parent):
        UiSubplotTool.__init__(self, None)

        self.targetfig = targetfig
        self.parent = parent
        self.donebutton.clicked.connect(self.close)
        self.resetbutton.clicked.connect(self.reset)
        self.tightlayout.clicked.connect(self.functight)

        # constraints
        self.sliderleft.valueChanged.connect(self.sliderright.setMinimum)
        self.sliderright.valueChanged.connect(self.sliderleft.setMaximum)
        self.sliderbottom.valueChanged.connect(self.slidertop.setMinimum)
        self.slidertop.valueChanged.connect(self.sliderbottom.setMaximum)

        self.defaults = {}
        for attr in ('left', 'bottom', 'right', 'top', 'wspace', 'hspace', ):
            self.defaults[attr] = getattr(self.targetfig.subplotpars, attr)
            slider = getattr(self, 'slider' + attr)
            slider.setMinimum(0)
            slider.setMaximum(1000)
            slider.setSingleStep(5)
            slider.valueChanged.connect(getattr(self, 'func' + attr))

        self._setSliderPositions()

    def _setSliderPositions(self):
        for attr in ('left', 'bottom', 'right', 'top', 'wspace', 'hspace', ):
            slider = getattr(self, 'slider' + attr)
            slider.setSliderPosition(int(self.defaults[attr] * 1000))

    def funcleft(self, val):
        if val == self.sliderright.value():
            val -= 1
        val /= 1000.
        self.targetfig.subplots_adjust(left=val)
        self.leftvalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def funcright(self, val):
        if val == self.sliderleft.value():
            val += 1
        val /= 1000.
        self.targetfig.subplots_adjust(right=val)
        self.rightvalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def funcbottom(self, val):
        if val == self.slidertop.value():
            val -= 1
        val /= 1000.
        self.targetfig.subplots_adjust(bottom=val)
        self.bottomvalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def functop(self, val):
        if val == self.sliderbottom.value():
            val += 1
        val /= 1000.
        self.targetfig.subplots_adjust(top=val)
        self.topvalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def funcwspace(self, val):
        val /= 1000.
        self.targetfig.subplots_adjust(wspace=val)
        self.wspacevalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def funchspace(self, val):
        val /= 1000.
        self.targetfig.subplots_adjust(hspace=val)
        self.hspacevalue.setText("%.2f" % val)
        if self.drawon:
            self.targetfig.canvas.draw()

    def functight(self):
        self.targetfig.tight_layout()
        self._setSliderPositions()
        self.targetfig.canvas.draw()

    def reset(self):
        self.targetfig.subplots_adjust(**self.defaults)
        self._setSliderPositions()
        self.targetfig.canvas.draw()

class NavigationToolbar2(object):
    """
    Base class for the navigation cursor, version 2
    backends must implement a canvas that handles connections for
    'button_press_event' and 'button_release_event'.  See
    :meth:`FigureCanvasBase.mpl_connect` for more information
    They must also define
      :meth:`save_figure`
         save the current figure
      :meth:`set_cursor`
         if you want the pointer icon to change
      :meth:`_init_toolbar`
         create your toolbar widget
      :meth:`draw_rubberband` (optional)
         draw the zoom to rect "rubberband" rectangle
      :meth:`press`  (optional)
         whenever a mouse button is pressed, you'll be notified with
         the event
      :meth:`release` (optional)
         whenever a mouse button is released, you'll be notified with
         the event
      :meth:`dynamic_update` (optional)
         dynamically update the window while navigating
      :meth:`set_message` (optional)
         display message
      :meth:`set_history_buttons` (optional)
         you can change the history back / forward buttons to
         indicate disabled / enabled state.
    That's it, we'll do the rest!
    """

    # list of toolitems to add to the toolbar, format is:
    # (
    #   text, # the text of the button (often not visible to users)
    #   tooltip_text, # the tooltip shown on hover (where possible)
    #   image_file, # name of the image for the button (without the extension)
    #   name_of_method, # name of the method in NavigationToolbar2 to call
    # )
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )

    def __init__(self, canvas):
        self.canvas = canvas
        canvas.toolbar = self
        # a dict from axes index to a list of view limits
        self._views = cbook.Stack()
        self._positions = cbook.Stack()  # stack of subplot positions
        self._xypress = None  # the location and axis info at the time
                              # of the press
        self._idPress = None
        self._idRelease = None
        self._active = None
        self._lastCursor = None
        self._init_toolbar()
        self._idDrag = self.canvas.mpl_connect(
            'motion_notify_event', self.mouse_move)

        self._ids_zoom = []
        self._zoom_mode = None

        self._button_pressed = None  # determined by the button pressed
                                     # at start

        self.mode = ''  # a mode string for the status bar
        self.set_history_buttons()

    def set_message(self, s):
        """Display a message on toolbar or in status bar"""
        pass

    def back(self, *args):
        """move back up the view lim stack"""
        self._views.back()
        self._positions.back()
        self.set_history_buttons()
        self._update_view()

    def dynamic_update(self):
        pass

    def draw_rubberband(self, event, x0, y0, x1, y1):
        """Draw a rectangle rubberband to indicate zoom limits"""
        pass

    def remove_rubberband(self):
        """Remove the rubberband"""
        pass

    def forward(self, *args):
        """Move forward in the view lim stack"""
        self._views.forward()
        self._positions.forward()
        self.set_history_buttons()
        self._update_view()

    def home(self, *args):
        """Restore the original view"""
        self._views.home()
        self._positions.home()
        self.set_history_buttons()
        self._update_view()

    def _init_toolbar(self):
        """
        This is where you actually build the GUI widgets (called by
        __init__).  The icons ``home.xpm``, ``back.xpm``, ``forward.xpm``,
        ``hand.xpm``, ``zoom_to_rect.xpm`` and ``filesave.xpm`` are standard
        across backends (there are ppm versions in CVS also).
        You just need to set the callbacks
        home         : self.home
        back         : self.back
        forward      : self.forward
        hand         : self.pan
        zoom_to_rect : self.zoom
        filesave     : self.save_figure
        You only need to define the last one - the others are in the base
        class implementation.
        """
        raise NotImplementedError

    def _set_cursor(self, event):
        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if self._active == 'ZOOM':
                if self._lastCursor != cursors.SELECT_REGION:
                    self.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION
            elif (self._active == 'PAN' and
                  self._lastCursor != cursors.MOVE):
                self.set_cursor(cursors.MOVE)

                self._lastCursor = cursors.MOVE

    def mouse_move(self, event):
        self._set_cursor(event)

        if event.inaxes and event.inaxes.get_navigate():

            try:
                s = event.inaxes.format_coord(event.xdata, event.ydata)
            except (ValueError, OverflowError):
                pass
            else:
                artists = [a for a in event.inaxes.mouseover_set
                           if a.contains(event)]

                if artists:

                    a = max(enumerate(artists), key=lambda x: x[1].zorder)[1]
                    if a is not event.inaxes.patch:
                        data = a.get_cursor_data(event)
                        if data is not None:
                            s += ' [%s]' % a.format_cursor_data(data)

                if len(self.mode):
                    self.set_message('%s, %s' % (self.mode, s))
                else:
                    self.set_message(s)
        else:
            self.set_message(self.mode)

    def pan(self, *args):
        """Activate the pan/zoom tool. pan with left button, zoom with right"""
        # set the pointer icon and button press funcs to the
        # appropriate callbacks

        if self._active == 'PAN':
            self._active = None
        else:
            self._active = 'PAN'
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.press_pan)
            self._idRelease = self.canvas.mpl_connect(
                'button_release_event', self.release_pan)
            self.mode = 'pan/zoom'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)

    def press(self, event):
        """Called whenver a mouse button is pressed."""
        pass

    def press_pan(self, event):
        """the press mouse button in pan/zoom mode callback"""

        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty():
            self.push_current()

        self._xypress = []
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                    a.get_navigate() and a.can_pan()):
                a.start_pan(x, y, event.button)
                self._xypress.append((a, i))
                self.canvas.mpl_disconnect(self._idDrag)
                self._idDrag = self.canvas.mpl_connect('motion_notify_event',
                                                       self.drag_pan)

        self.press(event)

    def press_zoom(self, event):
        """the press mouse button in zoom to rect mode callback"""
        # If we're already in the middle of a zoom, pressing another
        # button works to "cancel"
        if self._ids_zoom != []:
            for zoom_id in self._ids_zoom:
                self.canvas.mpl_disconnect(zoom_id)
            self.release(event)
            self.draw()
            self._xypress = None
            self._button_pressed = None
            self._ids_zoom = []
            return

        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty():
            self.push_current()

        self._xypress = []
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                    a.get_navigate() and a.can_zoom()):
                self._xypress.append((x, y, a, i, a._get_view()))

        id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_zoom)
        id2 = self.canvas.mpl_connect('key_press_event',
                                      self._switch_on_zoom_mode)
        id3 = self.canvas.mpl_connect('key_release_event',
                                      self._switch_off_zoom_mode)

        self._ids_zoom = id1, id2, id3
        self._zoom_mode = event.key

        self.press(event)

    def _switch_on_zoom_mode(self, event):
        self._zoom_mode = event.key
        self.mouse_move(event)

    def _switch_off_zoom_mode(self, event):
        self._zoom_mode = None
        self.mouse_move(event)

    def push_current(self):
        """push the current view limits and position onto the stack"""
        views = []
        pos = []
        for a in self.canvas.figure.get_axes():
            views.append(a._get_view())
            # Store both the original and modified positions
            pos.append((
                a.get_position(True).frozen(),
                a.get_position().frozen()))
        self._views.push(views)
        self._positions.push(pos)
        self.set_history_buttons()

    def release(self, event):
        """this will be called whenever mouse button is released"""
        pass

    def release_pan(self, event):
        """the release mouse button callback in pan/zoom mode"""

        if self._button_pressed is None:
            return
        self.canvas.mpl_disconnect(self._idDrag)
        self._idDrag = self.canvas.mpl_connect(
            'motion_notify_event', self.mouse_move)
        for a, ind in self._xypress:
            a.end_pan()
        if not self._xypress:
            return
        self._xypress = []
        self._button_pressed = None
        self.push_current()
        self.release(event)
        self.draw()

    def drag_pan(self, event):
        """the drag callback in pan/zoom mode"""

        for a, ind in self._xypress:
            #safer to use the recorded button at the press than current button:
            #multiple button can get pressed during motion...
            a.drag_pan(self._button_pressed, event.key, event.x, event.y)
        self.dynamic_update()

    def drag_zoom(self, event):
        """the drag callback in zoom mode"""

        if self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = self._xypress[0]

            # adjust x, last, y, last
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)

            if self._zoom_mode == "x":
                x1, y1, x2, y2 = a.bbox.extents
                y, lasty = y1, y2
            elif self._zoom_mode == "y":
                x1, y1, x2, y2 = a.bbox.extents
                x, lastx = x1, x2

            self.draw_rubberband(event, x, y, lastx, lasty)

    def release_zoom(self, event):
        """the release mouse button callback in zoom to rect mode"""
        for zoom_id in self._ids_zoom:
            self.canvas.mpl_disconnect(zoom_id)
        self._ids_zoom = []

        self.remove_rubberband()

        if not self._xypress:
            return

        last_a = []

        for cur_xypress in self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = cur_xypress
            # ignore singular clicks - 5 pixels is a threshold
            # allows the user to "cancel" a zoom action
            # by zooming by less than 5 pixels
            if ((abs(x - lastx) < 5 and self._zoom_mode!="y") or
                    (abs(y - lasty) < 5 and self._zoom_mode!="x")):
                self._xypress = None
                self.release(event)
                self.draw()
                return

            # detect twinx,y axes and avoid double zooming
            twinx, twiny = False, False
            if last_a:
                for la in last_a:
                    if a.get_shared_x_axes().joined(a, la):
                        twinx = True
                    if a.get_shared_y_axes().joined(a, la):
                        twiny = True
            last_a.append(a)

            if self._button_pressed == 1:
                direction = 'in'
            elif self._button_pressed == 3:
                direction = 'out'
            else:
                continue

            a._set_view_from_bbox((lastx, lasty, x, y), direction,
                                  self._zoom_mode, twinx, twiny)

        self.draw()
        self._xypress = None
        self._button_pressed = None

        self._zoom_mode = None

        self.push_current()
        self.release(event)

    def draw(self):
        """Redraw the canvases, update the locators"""
        for a in self.canvas.figure.get_axes():
            xaxis = getattr(a, 'xaxis', None)
            yaxis = getattr(a, 'yaxis', None)
            locators = []
            if xaxis is not None:
                locators.append(xaxis.get_major_locator())
                locators.append(xaxis.get_minor_locator())
            if yaxis is not None:
                locators.append(yaxis.get_major_locator())
                locators.append(yaxis.get_minor_locator())

            for loc in locators:
                loc.refresh()
        self.canvas.draw_idle()

    def _update_view(self):
        """Update the viewlim and position from the view and
        position stack for each axes
        """

        views = self._views()
        if views is None:
            return
        pos = self._positions()
        if pos is None:
            return
        for i, a in enumerate(self.canvas.figure.get_axes()):
            a._set_view(views[i])
            # Restore both the original and modified positions
            a.set_position(pos[i][0], 'original')
            a.set_position(pos[i][1], 'active')

        self.canvas.draw_idle()

    def save_figure(self, *args):
        """Save the current figure"""
        raise NotImplementedError

    def set_cursor(self, cursor):
        """
        Set the current cursor to one of the :class:`Cursors`
        enums values
        """
        pass

    def update(self):
        """Reset the axes stack"""
        self._views.clear()
        self._positions.clear()
        self.set_history_buttons()

    def zoom(self, *args):
        """Activate zoom to rect mode"""
        if self._active == 'ZOOM':
            self._active = None
        else:
            self._active = 'ZOOM'

        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event',
                                                    self.press_zoom)
            self._idRelease = self.canvas.mpl_connect('button_release_event',
                                                      self.release_zoom)
            self.mode = 'zoom rect'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)

    def set_history_buttons(self):
        """Enable or disable back/forward button"""
        pass
    
    
class NavigationToolbar2QT(NavigationToolbar2, QtWidgets.QToolBar):
    message = QtCore.Signal(str)

    def __init__(self, canvas, parent, coordinates=True):
        """ coordinates: should we show the coordinates on the right? """
        self.canvas = canvas
        self.parent = parent
        self.coordinates = coordinates
        self._actions = {}
        """A mapping of toolitem method names to their QActions"""

        QtWidgets.QToolBar.__init__(self, parent)
        NavigationToolbar2.__init__(self, canvas)

    def _icon(self, name):
        return QtGui.QIcon(os.path.join(self.basedir, name))

    def _init_toolbar(self):
        self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        if figureoptions is not None:
            a = self.addAction(self._icon("qt4_editor_options.png"),
                               'Customize', self.edit_parameters)
            a.setToolTip('Edit axis, curve and image parameters')

        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.locLabel.setSizePolicy(
                QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None

    if figureoptions is not None:
        def edit_parameters(self):
            allaxes = self.canvas.figure.get_axes()
            if not allaxes:
                QtWidgets.QMessageBox.warning(
                    self.parent, "Error", "There are no axes to edit.")
                return
            if len(allaxes) == 1:
                axes = allaxes[0]
            else:
                titles = []
                for axes in allaxes:
                    name = (axes.get_title() or
                            " - ".join(filter(None, [axes.get_xlabel(),
                                                     axes.get_ylabel()])) or
                            "<anonymous {} (id: {:#x})>".format(
                                type(axes).__name__, id(axes)))
                    titles.append(name)
                item, ok = QtWidgets.QInputDialog.getItem(
                    self.parent, 'Customize', 'Select axes:', titles, 0, False)
                if ok:
                    axes = allaxes[titles.index(six.text_type(item))]
                else:
                    return

            figureoptions.figure_edit(axes, self)

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['zoom'].setChecked(self._active == 'ZOOM')

    def pan(self, *args):
        super(NavigationToolbar2QT, self).pan(*args)
        self._update_buttons_checked()

    def zoom(self, *args):
        super(NavigationToolbar2QT, self).zoom(*args)
        self._update_buttons_checked()

    def dynamic_update(self):
        self.canvas.draw_idle()

    def set_message(self, s):
        self.message.emit(s)
        if self.coordinates:
            self.locLabel.setText(s)

    def set_cursor(self, cursor):
        if DEBUG:
            print('Set cursor', cursor)
        self.canvas.setCursor(cursord[cursor])

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0

        w = abs(x1 - x0)
        h = abs(y1 - y0)

        rect = [int(val)for val in (min(x0, x1), min(y0, y1), w, h)]
        self.canvas.drawRectangle(rect)

    def remove_rubberband(self):
        self.canvas.drawRectangle(None)

    def configure_subplots(self):
        image = os.path.join(matplotlib.rcParams['datapath'],
                             'images', 'matplotlib.png')
        dia = SubplotToolQt(self.canvas.figure, self.parent)
        dia.setWindowIcon(QtGui.QIcon(image))
        dia.exec_()

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = list(six.iteritems(filetypes))
        sorted_filetypes.sort()
        default_filetype = self.canvas.get_default_filetype()

        startpath = matplotlib.rcParams.get('savefig.directory', '')
        startpath = os.path.expanduser(startpath)
        start = os.path.join(startpath, self.canvas.get_default_filename())
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)

        fname, filter = _getSaveFileName(self.parent,
                                         "Choose a filename to save to",
                                 start, filters, selectedFilter)
        if fname:
            if startpath == '':
                # explicitly missing key or empty str signals to use cwd
                matplotlib.rcParams['savefig.directory'] = startpath
            else:
                # save dir for next time
                savefig_dir = os.path.dirname(six.text_type(fname))
                matplotlib.rcParams['savefig.directory'] = savefig_dir
            try:
                self.canvas.print_figure(six.text_type(fname))
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error saving file", six.text_type(e),
                    QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)