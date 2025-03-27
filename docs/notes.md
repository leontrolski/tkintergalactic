# Notes

Notes from [Tcl and the Tk Toolkit (Addison-Wesley)](https://theswissbay.ch/pdf/Gentoomen%20Library/Programming/C%2B%2B/Addison%20Wesley%20-%20Tcl%20and%20the%20Tk%20Toolkit%5B1993%5D.pdf).

# Chapter 14 - An Introduction to Tk

The basic user interface elements in Tk are called widgets.

In Tk the term application refers to a single widget hierarchy (one main window and any number of internal and top-level windows descended from it), a single Tcl interpreter associated with the widget hierarchy, plus all the commands provided by that interpreter.

Each application is usually a separate process, but Tk also allows a single process to manage several applications, each with its own widget hierarchy and Tcl interpreter.

Tk applications are controlled by two kinds of Tcl scripts: an initialization script and event handlers. The initialization script is executed when the application starts up. It creates the application’s user interface etc. Once initialization is complete the application enters an event loop to wait for user interactions. Whenever an interesting event occurs, a Tcl script is invoked to process that event. These scripts are called event handlers.

Widgets don’t determine their own sizes and locations on the screen. This function is carried out by geometry managers. Each geometry manager implements a particular style of layout. Given a collection of widgets to manage and some controlling information about how to arrange them, a geometry manager assigns a size and location to each widget. For example, you might tell a geometry manager to arrange a set of widgets in a vertical column. It would then position the widgets so that they are adjacent but don’t overlap. If one widget should suddenly need more space (e.g. its font is changed to a larger one) it will notify the geometry manager and the geometry manager will move other widgets down to preserve the proper column structure.

Tk currently contains four geometry managers. The placer is a simple fixed-placement geometry manager. You give it instructions like “place window .x at location (10,100) in its parent and make it 2 cm wide and 1 cm high.” The placer is simple to understand but limited in applicability because it doesn’t consider interactions between widgets.

The second geometry manager is called the packer. It is constraint-based and allows you to implement arrangements like the column example from above. It is more complex than the placer but much more powerful and hence more widely used. The packer is the subject of Chapter 18.

Two other geometry managers are implemented as part of the canvas and text widgets.

Tk supports five other forms of interconnection in addition to event handlers: the selection, the input focus, the window manager, the send command, and grabs.

The selection is a distinguished piece of information on the screen, such as a range of text or a graphic. The X window system provides a protocol for applications to claim ownership of the selection and retrieve the contents of the selection from whichever application owns it. Chapter 20 discusses the selection in more detail and describes Tk’s select command, which is used to manipulate it. At any given time, keystrokes typed for an application are directed to a particular widget, regardless of the mouse cursor’s location. This widget is referred to as the focus widget or input focus. Chapter 21 describes the focus command, which is used to move the focus among the widgets of an application.

# Chapter 15 - Tour Of The Tk Widgets

Frames are like `<div>`s, most of the non-leaf widgets are Frames. Toplevel widgets are the outermost.
Labels contain text strings or bitmaps.
A hovered Button is active.

Menubuttons
Command: similar to a button widget.
Checkbutton: similar to a checkbutton widget. Has an “on” or “off” state.
Radiobutton: similar to a radiobutton widget.
Cascade: similar to a menubutton widget. Posts a cascaded sub-menu when the mouse passes over it.
Separator: Displays a horizontal line for decoration.

Menus spend most of their time in an invisible state called unposted. When a user wants to invoke a menu entry, he or she posts the menu, which makes it appear on the screen.

Menus are most commonly used in a pull-down style. In this style the application displays a menu bar near the top of its main window. The second common style of menu usage is called pop-up menus. In this approach, pressing one of the mouse buttons in a particular widget causes a menu to post next to the mouse cursor. The third commonly used approach to posting menus is called cascaded menus. Cascaded menus are implemented using cascade menu entries in other menus.

Listbox - `<ul>`
Entry - `<input>`
Scrollbar
Text - `<p>`
Canvases - `<canvas>`
Scale - `<input type="range">`
Message - dumb `<p>`


# Chapter 16 - Configuration Options

Colors, Fonts, Reliefs, Bitmaps, Cursors, etc.

A distance is specified as an integer or floating-point value followed optionally by a single character giving the units. If no unit specifier is given then the units are pixels.

c centimeters
i inches
m millimeters
p printer’s points (1/72 inch)

An anchor position indicates how to attach one object to another. For example, if the window for a button widget is larger than needed for the widget’s text, a -anchor option may be specified to indicate where the text should be positioned in the window. Anchor positions are also used for other purposes, such as telling a canvas widget where to position a bitmap relative to a point or telling the packer geometry manager where to position a window in its frame.

Anchor positions are specified using one of the following points of the compass:

n Center of object’s top side.
ne Top right corner of object.
e Center of object’s right side.
se Lower right corner of object.
s Center of object’s bottom side.
sw Lower left corner of object.
w Center of object’s left side.
nw Top left corner of object.
center Center of object.

The anchor position specifies the point on the object by which it is to be attached, as if a push-pin were stuck through the object at that point and then used to pin the object someplace. For example, if a -anchor option of w is specified for a button, it means that the button’s text or bitmap is to be attached by the center of its left side, and that point will be positioned over the corresponding point in the window. Thus w means that the text or bitmap will be centered vertically and aligned with the left edge of the window. For bitmap items in canvas widgets, the -anchor option indicates where the bitmap should be positioned relative to a point associated with the item; in this case, w means that the center of the bitmap’s left side should be positioned over the point, so that the bitmap actually lies to the east of the point.

Scrolling...

Another common form for options is variable names. These options are used to associate one or more Tcl global variables with a widget so that the widget can set the variable under certain conditions or monitor its value and react to changes in the variable. For example, many of the widgets that display text, such as labels and buttons and messages and entries, support a -textvariable option. The value of the option is the name of a global variable that contains the text to display in the widget. The widget monitors the value of the variable and updates the display whenever the variable changes value.

In addition, for widgets like entries that can modify their text, the widget updates the variable to track changes made by the user.

Checkbuttons and radiobuttons also support a -variable option, which contains the name of a global variable. For checkbuttons there are two additional options (-onvalue and -offvalue) that specify values to store in the variable when the checkbutton is “on” and “off.” As the user clicks on the checkbutton with the mouse, it updates the variable to reflect the checkbutton’s state. The checkbutton also monitors the value of the variable and changes its on/off state if the variable’s value is changed externally. Each checkbutton typically has its own variable.

Every widget class supports a configure widget command. This command comes in three forms, which can be used both to change the values of options and also to retrieve information about the widget’s options.


# Chapter 17 - Geometry Managers: The Placer

A geometry manager’s job is to arrange one or more slave windows relative to a master window. For example, it might arrange three slaves in a row from left to right across the area of the master, or it might arrange two slaves so that they split the space of the master with one slave occupying the top half and the other occupying the bottom half.

A geometry manager receives three kinds of inputs: a requested size for each slave (which usually reflects the information to be displayed in the slave), commands from the application designer (such as “arrange these three windows in a row”), and the actual geometry of the master window. The geometry manager then assigns a size and location to each slave. It may also set the requested size for the master window, which can be used by a higher-level geometry manager to manager the master.

Geometry Manager = f(
    Requested size from slave,
    Parameters from application designer,
    Geometry of master,
) -> Size and location of slave, Requested size for master

A geometry manager receives three sorts of information for its use in computing a layout (see Figure 17.1 ). First, each slave widget requests a particular width and height. These are usually the minimum dimensions needed by the widget to display its information. For example, a button widget requests a size just large enough to display its text or bitmap along with the border specified for the widget. Although geometry managers aren’t obliged to satisfy the requests made by their slave widgets, they usually do.

```
place .x -x 0 -y 0
```

This command positions window .x so that its upper-left corner appears at the upper-left corner of its master, which defaults to its parent. The placer supports about a dozen configuration options in all; Table 17.2 summarizes the options and Figure 17.2 shows some examples of using the placer.


`-x distance` - Specifies the horizontal distance of the slave’s anchor point from the left edge of its master.
`-y distance` - Specifies the vertical distance of the slave’s anchor point from the top edge of its master.
`-relx fraction` - Specifies the horizontal position of the slave’s anchor point in a relative fashion as a floating-point number. If fraction is 0.0 it refers to the master’s left edge, and 1.0 refers to the right edge. Fraction need not lie between 0.0 and 1.0.
`-rely fraction` - Specifies the vertical position of the slave’s anchor point...
`-anchor anchor` - Specifies which point on the slave window is to be positioned over the anchor point.
`-width distance` - Specifies the width of the slave.
`-height distance` - Specifies the height of the slave.
`-relwidth fraction` - Specifies the slave’s width as a fraction of the width of its master.
`-relheight fraction` - Specifies the slave’s height as a fraction of the height of its master.
`-in window` - Specifies the master window for the slave. Must be the slave’s parent or a descendant of the parent.
`-bordermode mode` - Specifies how the master’s borders are to be used in placing the slave. Mode must be inside, outside, or ignore.

By default, a slave window managed by the placer is given the size it requests. However, the `-width`, `-height`, `-relwidth`, and `-relheight` options may be used to override either or both of the slave’s requested dimensions. The `-width` and `-height` options specify the dimensions in absolute terms, and `-relwidth` and `-relheight` specify the dimensions as a fraction of the size of the master. For example, the following command sets the width of .x to 50 pixels and the height to half the height of its master:

```
place .x -width 50 -relheight 0.5
```

In most cases the master window for a given slave will be its parent in the window hierarchy. If no master is specified, the placer uses the parent by default. However, it is sometimes useful to use a different window as the master for a slave. For example, it might be useful to attach one window to a sibling so that whenever the sibling is moved the window will follow. This can be accomplished using the -in configuration option.
