I agree. It's significantly better than the original, but it still has too many reasons to change. The widget is still acting as a composition root, a view implementation, a Qt adapter, and part of the application API.
I'd try to get it down to one responsibility:
Host the Qt widgets and delegate everything else.
The rest should move elsewhere.
1. The widget is still constructing the object graph
This is the first thing I'd remove.
Currently it knows about
RamachandranColorManager
RamachandranCalculator
RamachandranRenderer
RamachandranInteraction
RamachandranPresenter
That means every time you change your implementation, this widget changes.
Instead, introduce a factory/builder.
class RamachandranWidgetFactory:

    @staticmethod
    def create(parent=None):
        widget = RamachandranPlotWidget(parent)

        renderer = RamachandranRenderer(widget.ax)
        interaction = RamachandranInteraction(widget.canvas, widget.ax)
        calculator = RamachandranCalculator(...)
        presenter = RamachandranPresenter(...)

        widget.attach_presenter(presenter)

        return widget
Now the widget no longer knows what a renderer is.
2. UI creation belongs in its own class
Even this
self.progress_bar
self.status_label
self.controls
is UI composition.
I'd move it into
RamachandranPlotView
or
RamachandranLayout
whose only responsibility is
Build widgets
Create layouts
Expose references
For example
view = RamachandranView()

view.canvas
view.status
view.progress
view.controls
Then
class RamachandranPlotWidget(MatplotlibPlotWidget):

    def __init__(...):
        super().__init__()

        self.view = RamachandranView(self.canvas)
3. Message boxes shouldn't live here
These
show_error()

show_warning()

show_info()
are generic Qt utilities.
I'd move them into
QtDialogService
or
MessageService
Example
dialog_service.error(...)
Now the presenter depends on
DialogService
instead of QWidget.
4. Export dialog is another service
Likewise
ask_export_path()
is not Ramachandran-specific.
It belongs in
FileDialogService
or
ExportService
Then the presenter simply does
filename = dialogs.ask_save_plot_filename()
5. Progress/status can be grouped
Instead of
set_status()

set_busy()

set_progress()
create
StatusPanel
+------------------------+
 Loading...

 ████████████ 55%

--------------------------
The widget exposes
self.status_panel
and the presenter calls
status_panel.show_busy()

status_panel.show_ready()

status_panel.set_progress()
Three methods disappear.
6. The widget shouldn't expose the presenter
This
@property
def structure(self):
    return self.presenter.structure
and
@property
def model(self):
    return self.presenter.model
are a smell.
The outside world shouldn't know there is a presenter.
Instead
widget.select_residue(...)
widget.load_structure(...)
widget.export()
Everything else is internal.
7. Even load_structure() could disappear
Depending on your architecture, the widget shouldn't even know about structures.
Instead
presenter.load_structure(...)
or
controller.open_structure(...)
The window owns the presenter.
The presenter owns the widget.
This is classic MVP.
MainWindow
      │
      ▼
Presenter
      │
      ▼
Widget
instead of
MainWindow
      │
      ▼
Widget
      │
      ▼
Presenter
That inversion removes a surprising amount of coupling.
I'd actually split it further
Instead of
RamachandranPlotWidget
I'd have
RamachandranView
whose entire job is
Canvas

Status

Progress

Controls
No logic whatsoever.
Then
RamachandranPresenter
owns
Renderer

Interaction

Calculator

Model
The presenter connects everything together.
The view literally becomes
class RamachandranView(MatplotlibPlotWidget):

    residue_selected = Signal(...)

    def __init__(self):
        super().__init__()

        self.controls = RamachandranControlPanel()
        self.status = StatusPanel()
That's almost all the code.
My preferred dependency graph
               MainWindow
                    │
                    ▼
          RamachandranPresenter
          ├──────────────┐
          │              │
          ▼              ▼
 RamachandranModel   RamachandranRenderer
          │              │
          └──────┬───────┘
                 ▼
      RamachandranInteraction
                 │
                 ▼
         RamachandranView
Notice something important:
The view doesn't know about the presenter.
The view doesn't know about the renderer.
The view doesn't know about the calculator.
The view doesn't know about the model.
It is just a passive collection of Qt widgets.
One caveat
I would not extract everything into services just for the sake of reducing line count. A widget with 100–150 lines that simply instantiates a few child widgets and exposes a small view interface is perfectly reasonable. The more significant architectural improvement is reversing the ownership so that the presenter owns the renderer, interaction, calculator, and model, while the view remains passive. That eliminates the remaining coupling without introducing unnecessary abstraction.