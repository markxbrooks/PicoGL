RamachandranPlotWidget refactoring


I think this class is an excellent candidate for decomposition. At ~450 lines, RamachandranPlotWidget is simultaneously acting as:
View (Qt widgets)
Controller/Presenter (responding to user actions)
Plot renderer (Matplotlib)
Data model
Interaction manager
Export service
Statistics calculator
UI state manager
It violates the Single Responsibility Principle in several places. I'd recommend separating what is being displayed from how it is is displayed and how the user interacts with it.
Overall architecture
I would lean toward MVP rather than classical MVC.
Qt widgets already are the View, and Matplotlib is effectively another view component. A Presenter fits naturally between the calculation/model and the widgets.
                  Gemmi Structure
                         │
                         ▼
              RamachandranCalculator
                         │
                         ▼
                 RamachandranModel
                         │
                 (observable model)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
RamachandranPresenter          PlotRenderer
        │                                 │
        │                         Matplotlib Axes
        ▼                                 │
 RamachandranWidget ◄──────── PlotInteraction
         (Qt View)
The widget becomes almost entirely wiring.
1. Model
The current current_data dictionary should disappear.
Instead:
@dataclass
class RamachandranModel:
    phi: np.ndarray
    psi: np.ndarray
    chain_ids: list[str]
    residue_numbers: list[int]
    residue_names: list[str]
Now you have
model.phi
model.psi
instead of
current_data["phi"]
throughout the code.
I'd also move
selected_points
into the model.
@dataclass
class SelectionState:
    selected: list[int]
2. Presenter
The Presenter becomes the brains.
Instead of
load_structure()

_update_plot()

_refresh_plot()

_on_click()

_on_hover()
living inside the widget, they become
Presenter
    load_structure()
    refresh()
    select_residue()
    hover()
The presenter knows
model
calculator
renderer
widget
The widget knows none of these.
3. View (Qt)
Then the widget becomes very small.
class RamachandranWidget(QWidget):

    def __init__(...):

        self.controls = PlotControls()

        self.canvas = PlotCanvas()

        self.presenter = RamachandranPresenter(...)
Almost every slot becomes
slider.valueChanged.connect(
    self.presenter.update_point_size
)
rather than
self._update_plot()
4. Plot Renderer
This is where most of the drawing code belongs.
Currently
_setup_plot()

_draw_allowed_regions()

_draw_molprobity_general_background()

_add_allowed_regions_legend()

_add_ramachandran_percentages_box()

_redraw_selected_points()

_update_plot()
are all about rendering.
I'd move them into
RamachandranRenderer
Example
renderer.draw_axes()

renderer.draw_points()

renderer.draw_background()

renderer.draw_statistics()

renderer.draw_selection()
Notice there is no widget logic here.
It receives
Axes

Model

PlotSettings
and draws.
5. Plot Interaction
This class currently mixes together
hover
selection
tooltip
nearest-point search
I'd isolate it.
RamachandranInteraction
Responsibilities
mpl_connect()

closest_point()

show_tooltip()

highlight()

clear_selection()
The widget doesn't know how hovering works.
6. Reusable Matplotlib widget
This is probably the biggest architectural improvement.
Currently your widget is
RamachandranWidget
but 70% of it is actually generic plotting.
I'd instead have
MatplotlibPlotWidget
containing
Figure

Canvas

Axes

Toolbar

Export

Save

Refresh
Generic features
export
canvas
figure
axes
dpi
refresh
toolbar
resize
Then
RamachandranWidget
inherits
MatplotlibPlotWidget
and only provides
draw_plot()
This immediately becomes reusable for
Ramachandran
B-factor plots
Distance plots
RMSD plots
PCA plots
Electron-density profiles
7. Controls widget
The control panel is already self-contained.
_create_control_panel()
should become
RamachandranControlPanel(QWidget)
containing
Show reference

Tooltips

Point size

Export

Refresh
The widget simply exposes signals.
pointSizeChanged

exportRequested

refreshRequested

tooltipsChanged
8. Plot Settings
Instead of querying UI widgets during drawing
self.show_allowed_checkbox.isChecked()

slider.value()
I'd create
@dataclass
class RamachandranPlotSettings:

    point_size: int

    show_reference: bool

    show_tooltips: bool
Now rendering becomes
renderer.render(
    model,
    settings
)
which is deterministic and testable.
9. Statistics service
This code
_add_ramachandran_percentages_box()
actually performs calculations before rendering.
I'd split that.
RamachandranStatistics

    calculate()

    percentages()

    summary_text()
Renderer only draws
renderer.draw_statistics(statistics)
10. Nearest-point search
Currently
_closest_residue_index()
performs a linear search every mouse movement.
That is
O(n)
per hover.
For proteins with thousands of residues this becomes noticeable.
I'd replace it with
scipy.spatial.KDTree
or
cKDTree
built once
tree = KDTree(
    np.column_stack((phi, psi))
)
Then hover becomes
distance, index = tree.query(...)
which is
O(log n)
instead of
O(n)
11. File structure
A possible organization is:
ramachandran/
│
├── model.py
│   ├── RamachandranModel
│   ├── SelectionState
│   └── PlotSettings
│
├── presenter.py
│   └── RamachandranPresenter
│
├── renderer.py
│   └── RamachandranRenderer
│
├── interaction.py
│   └── RamachandranInteraction
│
├── statistics.py
│   └── RamachandranStatistics
│
├── controls.py
│   └── RamachandranControlPanel
│
├── widget.py
│   └── RamachandranWidget
│
└── calculator.py
12. What RamachandranWidget should look like
After refactoring, I'd expect the main widget to be around 80–120 lines:
class RamachandranWidget(MatplotlibPlotWidget):

    residue_selected = Signal(str, int, str)

    def __init__(self):
        super().__init__()

        self.model = RamachandranModel()
        self.settings = RamachandranPlotSettings()

        self.controls = RamachandranControlPanel()

        self.renderer = RamachandranRenderer(self.axes)

        self.interaction = RamachandranInteraction(
            self.canvas,
            self.axes,
            self.model,
        )

        self.presenter = RamachandranPresenter(
            self.model,
            self.renderer,
            self.controls,
            self.interaction,
        )
There is almost no application logic left in the widget itself.
Refactoring order
To minimize risk, I'd proceed incrementally:
Extract RamachandranPlotSettings and eliminate direct reads from checkboxes/sliders inside rendering.
Replace current_data with a typed RamachandranModel dataclass.
Extract RamachandranRenderer, moving all Matplotlib drawing code into it while keeping the widget as coordinator.
Extract RamachandranControlPanel so UI controls become an independent widget emitting signals.
Extract RamachandranInteraction for hover, selection, tooltips, and nearest-point logic.
Introduce RamachandranPresenter to mediate between the model, controls, renderer, and interaction, leaving the widget responsible only for composition.
Generalize MatplotlibPlotWidget once the Ramachandran-specific code is isolated, making it reusable across other scientific plots in ElMo.
This sequence preserves functionality after each step while steadily improving cohesion, testability, and reuse. I suspect you'll also find that the same MatplotlibPlotWidget and MVP pattern can be applied to your B-factor, RMSD, contact map, and other analysis views, giving ElMo a consistent plotting architecture rather than a collection of specialized widgets.