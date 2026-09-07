import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import datetime

# ==============================================================================
# DATA STRUCTURE 1: TUPLES (Required Assignment Concept)
# WHERE: Defined at module scope for immutable application constants, column
#        definitions, predefined categories, and stock status thresholds.
# WHY:   Tuples are immutable sequences in Python. Using tuples guarantees that
#        schema definitions, category lists, and system thresholds remain read-only
#        and cannot be altered or corrupted during runtime.
# ==============================================================================
COLUMN_DEFINITIONS: tuple = (
    ("id", "Item ID", 100, "center"),
    ("name", "Item Name", 230, "w"),
    ("category", "Category", 130, "center"),
    ("quantity", "Qty", 75, "center"),
    ("price", "Unit Price ($)", 100, "e"),
    ("total", "Total Value ($)", 110, "e"),
    ("status", "Stock Status", 110, "center"),
    ("supplier", "Supplier / Vendor", 150, "w"),
    ("date_added", "Date Added", 100, "center")
)

CATEGORIES: tuple = (
    "Electronics",
    "Hardware",
    "Peripherals",
    "Networking",
    "Accessories",
    "Software"
)

STATUS_THRESHOLDS: tuple = (
    ("Out of Stock", 0),
    ("Low Stock", 5),
    ("In Stock", 6)
)

# Color Palette: Eye-Catching Obsidian Black & Crimson Red Theme
COLOR_BG_DARK = "#060609"          # Pure deep pitch-black main canvas
COLOR_SURFACE = "#0D0D14"          # Sleek card and container panel background
COLOR_SURFACE_LIGHT = "#14141E"    # Raised card / input field background
COLOR_INPUT_BG = "#09090E"         # Pure black input field background
COLOR_BORDER = "#251218"           # Subtle crimson-tinted border
COLOR_BORDER_GLOW = "#FF2A55"      # Bright neon crimson red highlight
COLOR_ACCENT = "#E50914"           # Primary vibrant crimson red
COLOR_ACCENT_BRIGHT = "#FF2A55"    # Bright neon crimson red for highlights/hover
COLOR_ACCENT_MUTED = "#8A101D"     # Secondary deep crimson
COLOR_TEXT_PRIMARY = "#FFFFFF"     # Crisp white for headings and values
COLOR_TEXT_SECONDARY = "#94A3B8"   # Modern slate grey for labels and subtitles
COLOR_TEXT_ACCENT = "#FF4D6D"      # Glowing red text
COLOR_SUCCESS = "#10B981"          # Emerald green badge (In Stock)
COLOR_WARNING = "#F59E0B"          # Amber yellow badge (Low Stock)
COLOR_DANGER = "#EF4444"           # Red badge (Out of Stock / Critical)

# High-Impact Modern Typography (Inspired by reference UI design)
FONT_HERO = ("Segoe UI Black", 14)
FONT_TITLE = ("Segoe UI Black", 12)
FONT_SECTION = ("Segoe UI Black", 10)
FONT_CARD_TAG = ("Segoe UI Semibold", 8)
FONT_CARD_TITLE = ("Segoe UI Semibold", 8)
FONT_BODY = ("Segoe UI", 9)
FONT_BODY_BOLD = ("Segoe UI Semibold", 9)
FONT_BTN = ("Segoe UI Black", 8)
FONT_MONO = ("Consolas", 9, "bold")


# ==============================================================================
# USER-DEFINED FUNCTION 1: calculate_item_valuation
# PURPOSE: Computes total inventory value for an item given quantity and unit price.
# USES: Variables, type casting, mathematical evaluation.
# ==============================================================================
def calculate_item_valuation(quantity: int, unit_price: float) -> float:
    """Calculates total valuation rounded to two decimal places."""
    return round(float(quantity) * float(unit_price), 2)


# ==============================================================================
# USER-DEFINED FUNCTION 2: determine_stock_status
# PURPOSE: Evaluates stock status category using conditional branching logic.
# USES: Tuple data structure, if-elif-else statements, comparison operators.
# ==============================================================================
def determine_stock_status(quantity: int) -> str:
    """
    Returns string classification tag based on STATUS_THRESHOLDS tuple.
    USES: if-elif-else control flow structure.
    """
    if quantity <= 0:
        return "Out of Stock"
    elif quantity <= 5:
        return "Low Stock"
    else:
        return "In Stock"


# ==============================================================================
# USER-DEFINED FUNCTION 3: format_currency
# PURPOSE: Converts numeric price/valuation to standardized USD string.
# USES: String formatting, standard output representation.
# ==============================================================================
def format_currency(amount: float) -> str:
    """Formats numeric amounts into USD currency strings."""
    return f"${amount:,.2f}"


class CrimsonInventoryApp:
    """
    Main Application Class for Crimson Inventory Pro.
    Manages GUI state, Data Structures, CSV File Handling, and Business Logic.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Crimson Inventory Pro - Enterprise Stock Management System")

        # Responsive Desktop Window Geometry:
        # Dynamically calculates screen size and centers the window with ample desktop margins.
        # On standard 1366x768 screens, opens at ~1060x615 (not fullscreen), leaving visible
        # desktop margins on all sides and sitting cleanly above the Windows taskbar.
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        win_w = min(1080, max(920, int(screen_w * 0.78)))
        win_h = min(625, max(500, int((screen_h - 48) * 0.85)))

        pos_x = max(10, (screen_w - win_w) // 2)
        pos_y = max(10, (screen_h - 48 - win_h) // 2)

        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(860, 480)
        self.root.configure(bg=COLOR_BG_DARK)

        # File path for persistent data storage
        self.data_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_data.csv")

        # ==============================================================================
        # DATA STRUCTURE 2: LIST (Required Assignment Concept)
        # WHERE: self.inventory_records = []
        # WHY:   A dynamic, ordered, and mutable sequence that holds all inventory items.
        #        Enables iterating through rows, sorting, filtering search results, and
        #        efficiently populating the Tkinter Treeview widget.
        # ==============================================================================
        self.inventory_records = []

        # ==============================================================================
        # DATA STRUCTURE 3: SET (Required Assignment Concept)
        # WHERE: self.unique_ids = set()
        # WHY:   Maintains a collection of distinct Item IDs / SKUs. Checking
        #        `if new_id in self.unique_ids` provides average O(1) time complexity,
        #        instantly catching duplicate IDs and guaranteeing primary key integrity.
        # ==============================================================================
        self.unique_ids = set()

        # Selection state tracking variable
        self.selected_item_id = None

        # Creative Animation States
        self.cached_kpis = {"items": 0, "units": 0, "value": 0.0, "alerts": 0}
        self.beacon_state = 0
        self.scanner_pos = -160
        self.toast_frame = None
        self.toast_hide_job = None
        self.alert_pulse_state = 0

        # Interactive Graph State
        self.current_view = "table"
        self.graph_mode = "units"
        self.chart_anim_job = None

        # Initialize TTK custom theme and styles
        self._setup_ttk_styles()

        # Build GUI Components
        self._build_header_banner()
        self._build_kpi_cards()
        self._build_main_workspace()
        self._build_status_bar()

        # Start Creative Background Animations
        self._animate_laser_scanner()
        self._animate_heartbeat()
        self._animate_alert_pulse()

        # File Handling: Auto-load records when application initializes
        self.load_data_from_csv()

    def _setup_ttk_styles(self):
        """
        Configures modern ttk styles to create an eye-catching Black & Crimson theme.
        (Bonus Requirement: TTK Styling)
        """
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure Treeview table styling
        self.style.configure(
            "Treeview",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_SURFACE,
            borderwidth=0,
            rowheight=27,
            font=("Segoe UI", 9)
        )
        self.style.map(
            "Treeview",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "#FFFFFF")]
        )

        # Configure Treeview Header styling
        self.style.configure(
            "Treeview.Heading",
            background="#201217",
            foreground=COLOR_ACCENT_BRIGHT,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padding=(4, 5)
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", "#33151D")],
            foreground=[("active", "#FFFFFF")]
        )

        # Configure Combobox styling (Pure Black & Crimson Red)
        COLOR_COMBO_BG = "#121218"
        self.style.configure(
            "Crimson.TCombobox",
            fieldbackground=COLOR_COMBO_BG,
            background=COLOR_COMBO_BG,
            foreground="#FFFFFF",
            arrowcolor=COLOR_ACCENT_BRIGHT,
            bordercolor=COLOR_BORDER,
            darkcolor=COLOR_COMBO_BG,
            lightcolor=COLOR_COMBO_BG,
            padding=3
        )
        self.style.map(
            "Crimson.TCombobox",
            fieldbackground=[
                ("readonly", COLOR_COMBO_BG),
                ("readonly", "focus", COLOR_COMBO_BG),
                ("focus", COLOR_COMBO_BG),
                ("active", COLOR_COMBO_BG),
                ("disabled", "#0E0E12"),
            ],
            background=[
                ("readonly", COLOR_COMBO_BG),
                ("active", "#221118"),
                ("pressed", COLOR_ACCENT),
            ],
            foreground=[
                ("readonly", "#FFFFFF"),
                ("disabled", "#777788"),
            ],
            selectbackground=[
                ("readonly", COLOR_COMBO_BG),
            ],
            selectforeground=[
                ("readonly", "#FFFFFF"),
            ],
            bordercolor=[
                ("focus", COLOR_ACCENT_BRIGHT),
                ("!focus", COLOR_BORDER),
            ],
            arrowcolor=[
                ("active", "#FFFFFF"),
                ("!disabled", COLOR_ACCENT_BRIGHT),
            ]
        )

        # Configure popdown listbox options so dropdown menu is also pure black
        self.root.option_add("*TCombobox*Listbox.background", COLOR_COMBO_BG)
        self.root.option_add("*TCombobox*Listbox.foreground", "#FFFFFF")
        self.root.option_add("*TCombobox*Listbox.selectBackground", COLOR_ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        self.root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))

        # Configure Scrollbar styling
        self.style.configure(
            "Crimson.Vertical.TScrollbar",
            background=COLOR_SURFACE_LIGHT,
            troughcolor=COLOR_BG_DARK,
            bordercolor=COLOR_BG_DARK,
            arrowcolor=COLOR_ACCENT_BRIGHT
        )

    def _build_header_banner(self):
        """Builds the top header banner with cyber laser scanner and live heartbeat."""
        header_frame = tk.Frame(self.root, bg=COLOR_SURFACE, height=72)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # Creative Animation 1: Animated Cyber Laser Scanner Bar
        self.scanner_canvas = tk.Canvas(header_frame, height=3, bg="#14060B", highlightthickness=0, bd=0)
        self.scanner_canvas.pack(fill=tk.X, side=tk.TOP)
        self.scanner_canvas.create_line(0, 1, 2600, 1, fill="#240A12", width=3)
        self.laser_beam = self.scanner_canvas.create_line(0, 1, 160, 1, fill=COLOR_ACCENT_BRIGHT, width=3)
        self.laser_core = self.scanner_canvas.create_line(40, 1, 120, 1, fill="#FFA3BA", width=2)

        content_container = tk.Frame(header_frame, bg=COLOR_SURFACE)
        content_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 4))

        # Top line: Brand on left, Pill badges on right
        top_line = tk.Frame(content_container, bg=COLOR_SURFACE)
        top_line.pack(fill=tk.X, side=tk.TOP)

        # Brand Icon and Title (Left)
        brand_frame = tk.Frame(top_line, bg=COLOR_SURFACE)
        brand_frame.pack(side=tk.LEFT, fill=tk.Y)

        title_label = tk.Label(
            brand_frame,
            text="⚡ CRIMSON INVENTORY PRO",
            font=FONT_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SURFACE
        )
        title_label.pack(side=tk.LEFT)

        subtitle_badge = tk.Label(
            brand_frame,
            text="  SLTC CCS1300  ",
            font=FONT_CARD_TAG,
            fg=COLOR_ACCENT_BRIGHT,
            bg="#221016",
            padx=6,
            pady=1
        )
        subtitle_badge.pack(side=tk.LEFT, padx=(8, 0))

        # Right Action Info / Pill Badges (Pill style like reference image)
        info_frame = tk.Frame(top_line, bg=COLOR_SURFACE)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Creative Animation 2: Heartbeat status beacon
        self.sys_pill = tk.Label(
            info_frame,
            text="  ● SYSTEM ACTIVE  ",
            font=FONT_CARD_TAG,
            fg=COLOR_SUCCESS,
            bg="#0D2218",
            padx=7,
            pady=2
        )
        self.sys_pill.pack(side=tk.RIGHT, padx=3)

        tech_badge = tk.Label(
            info_frame,
            text="ENTERPRISE CORE",
            font=FONT_CARD_TAG,
            fg="#94A3B8",
            bg="#161622",
            padx=7,
            pady=2
        )
        tech_badge.pack(side=tk.RIGHT, padx=3)

        # Hero headline line (compact for desktop window)
        hero_line = tk.Frame(content_container, bg=COLOR_SURFACE)
        hero_line.pack(fill=tk.X, side=tk.TOP, pady=(2, 0))

        hero_headline = tk.Label(
            hero_line,
            text="SYSTEMS BUILT FOR INVENTORY MOMENTUM",
            font=("Segoe UI Black", 10),
            fg="#FFFFFF",
            bg=COLOR_SURFACE
        )
        hero_headline.pack(side=tk.LEFT, anchor="w")

        hero_sub = tk.Label(
            hero_line,
            text=" — Real-time warehouse intelligence & algorithmic valuation.",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SURFACE
        )
        hero_sub.pack(side=tk.LEFT, anchor="w")

    def _build_kpi_cards(self):
        """
        Creates 4 eye-catching KPI Summary Cards matching the reference card design:
        - Sleek dark container with glowing top colored edge
        - Subtitle tags: METRIC 01, METRIC 02, METRIC 03, METRIC 04
        - High-impact bold value in FONT_HERO
        - Descriptive caption
        """
        kpi_container = tk.Frame(self.root, bg=COLOR_BG_DARK)
        kpi_container.pack(fill=tk.X, side=tk.TOP, padx=16, pady=(4, 4))

        cards_meta = (
            ("kpi_items", "METRIC 01", "TOTAL PRODUCTS", "0", COLOR_ACCENT_BRIGHT, "Active catalog SKUs"),
            ("kpi_units", "METRIC 02", "STOCK UNITS", "0", "#38BDF8", "Total physical units"),
            ("kpi_value", "METRIC 03", "TOTAL VALUATION", "$0.00", "#34D399", "Gross inventory value"),
            ("kpi_alerts", "METRIC 04", "LOW STOCK ALERTS", "0", COLOR_WARNING, "Requires replenishment"),
        )

        self.kpi_labels = {}
        self.kpi_card_glows = {}
        self.kpi_card_frames = {}

        for index, (key, tag, title, default_val, accent_color, desc) in enumerate(cards_meta):
            card_frame = tk.Frame(
                kpi_container,
                bg=COLOR_SURFACE,
                highlightbackground="#221217",
                highlightthickness=1,
                padx=12,
                pady=5
            )
            card_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

            # Glowing top accent line for the card
            card_glow = tk.Frame(card_frame, bg=accent_color, height=2)
            card_glow.pack(fill=tk.X, side=tk.TOP, pady=(0, 4))

            # Header row inside card: Tag on left, Title on right
            tag_row = tk.Frame(card_frame, bg=COLOR_SURFACE)
            tag_row.pack(fill=tk.X)

            tag_lbl = tk.Label(
                tag_row,
                text=tag,
                font=FONT_CARD_TAG,
                fg=accent_color,
                bg=COLOR_SURFACE
            )
            tag_lbl.pack(side=tk.LEFT)

            t_lbl = tk.Label(
                tag_row,
                text=title,
                font=FONT_CARD_TAG,
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_SURFACE
            )
            t_lbl.pack(side=tk.RIGHT)

            # Big Bold Value
            v_lbl = tk.Label(
                card_frame,
                text=default_val,
                font=FONT_HERO,
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_SURFACE
            )
            v_lbl.pack(anchor="w", pady=(1, 0))

            # Subtitle description
            desc_lbl = tk.Label(
                card_frame,
                text=desc,
                font=("Segoe UI", 7),
                fg="#64748B",
                bg=COLOR_SURFACE
            )
            desc_lbl.pack(anchor="w")

            self.kpi_labels[key] = v_lbl
            self.kpi_card_glows[key] = card_glow
            self.kpi_card_frames[key] = card_frame

    def _build_main_workspace(self):
        """
        Constructs the central workspace, splitting screen into:
        1. Left Panel: Item Management Input Form & Action Buttons
        2. Right Panel: Search Bar, Treeview Table, and Data Operations Toolbar
        """
        workspace_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        workspace_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=3)

        # ======================================================================
        # LEFT PANEL: FORM & RECORD ENTRY
        # ======================================================================
        left_panel = tk.Frame(
            workspace_frame,
            bg=COLOR_SURFACE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            width=320
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_panel.pack_propagate(False)

        # Form Section Header
        form_header = tk.Frame(left_panel, bg=COLOR_SURFACE_LIGHT, height=34)
        form_header.pack(fill=tk.X, side=tk.TOP)
        form_header.pack_propagate(False)

        fh_label = tk.Label(
            form_header,
            text="✦ ITEM SPECIFICATIONS",
            font=FONT_SECTION,
            fg=COLOR_ACCENT_BRIGHT,
            bg=COLOR_SURFACE_LIGHT
        )
        fh_label.pack(side=tk.LEFT, padx=12, pady=5)

        # Form Input Fields Container
        form_body = tk.Frame(left_panel, bg=COLOR_SURFACE, padx=12, pady=6)
        form_body.pack(fill=tk.BOTH, expand=True)

        # 1. Item ID + Auto-Generate Button
        self._create_field_label(form_body, "ITEM ID / SKU *")
        id_row = tk.Frame(form_body, bg=COLOR_SURFACE)
        id_row.pack(fill=tk.X, pady=(1, 5))

        self.entry_id = self._create_entry_field(id_row)
        self.entry_id.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_autogen = tk.Button(
            id_row,
            text="⚡ AUTO",
            font=FONT_CARD_TAG,
            bg="#201017",
            fg=COLOR_ACCENT_BRIGHT,
            activebackground=COLOR_ACCENT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=7,
            cursor="hand2",
            command=self.auto_generate_sku
        )
        btn_autogen.pack(side=tk.RIGHT, padx=(5, 0))

        # 2. Item Name
        self._create_field_label(form_body, "ITEM NAME *")
        self.entry_name = self._create_entry_field(form_body)
        self.entry_name.pack(fill=tk.X, pady=(1, 5))

        # 3. Category Dropdown
        self._create_field_label(form_body, "CATEGORY *")
        self.combo_category = ttk.Combobox(
            form_body,
            values=CATEGORIES,
            state="readonly",
            style="Crimson.TCombobox",
            font=("Segoe UI", 9)
        )
        if CATEGORIES:
            self.combo_category.current(0)
        self.combo_category.pack(fill=tk.X, pady=(1, 5))

        # 4. Quantity & Unit Price (Side by side)
        qty_price_frame = tk.Frame(form_body, bg=COLOR_SURFACE)
        qty_price_frame.pack(fill=tk.X, pady=(1, 5))

        # Quantity Sub-column
        qty_col = tk.Frame(qty_price_frame, bg=COLOR_SURFACE)
        qty_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self._create_field_label(qty_col, "QUANTITY *")
        self.entry_qty = self._create_entry_field(qty_col)
        self.entry_qty.pack(fill=tk.X, pady=(1, 0))

        # Price Sub-column
        price_col = tk.Frame(qty_price_frame, bg=COLOR_SURFACE)
        price_col.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        self._create_field_label(price_col, "UNIT PRICE ($) *")
        self.entry_price = self._create_entry_field(price_col)
        self.entry_price.pack(fill=tk.X, pady=(1, 0))

        # 5. Supplier / Vendor
        self._create_field_label(form_body, "SUPPLIER / VENDOR")
        self.entry_supplier = self._create_entry_field(form_body)
        self.entry_supplier.pack(fill=tk.X, pady=(1, 6))

        # Action Buttons Container (CRUD Controls)
        crud_frame = tk.Frame(form_body, bg=COLOR_SURFACE)
        crud_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 2))

        # Add Item Button (Primary Crimson Button)
        self.btn_add = self._create_action_button(
            crud_frame,
            text="✚  ADD PRODUCT",
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            hover_bg=COLOR_ACCENT_BRIGHT,
            command=self.add_item
        )
        self.btn_add.pack(fill=tk.X, pady=2)

        # Update Item Button
        self.btn_update = self._create_action_button(
            crud_frame,
            text="✎  UPDATE PRODUCT",
            bg="#7F1D1D",
            fg="#FFFFFF",
            hover_bg="#991B1B",
            command=self.update_item
        )
        self.btn_update.pack(fill=tk.X, pady=2)

        # Delete & Clear in one row
        del_clr_row = tk.Frame(crud_frame, bg=COLOR_SURFACE)
        del_clr_row.pack(fill=tk.X, pady=2)

        self.btn_delete = self._create_action_button(
            del_clr_row,
            text="🗑  DELETE",
            bg="#26151B",
            fg="#EF4444",
            hover_bg="#3B1822",
            command=self.delete_item
        )
        self.btn_delete.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.btn_clear = self._create_action_button(
            del_clr_row,
            text="↺  CLEAR",
            bg=COLOR_SURFACE_LIGHT,
            fg=COLOR_TEXT_SECONDARY,
            hover_bg="#2D2D3E",
            command=self.clear_form
        )
        self.btn_clear.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        # ======================================================================
        # RIGHT PANEL: SEARCH & TREEVIEW TABLE
        # ======================================================================
        self.right_panel = tk.Frame(
            workspace_frame,
            bg=COLOR_SURFACE,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search and Filter Toolbar (Top of Right Panel) - Sleek Pure Black
        COLOR_TOOLBAR_BG = "#0D0D12"
        search_toolbar = tk.Frame(
            self.right_panel,
            bg=COLOR_TOOLBAR_BG,
            height=42,
            padx=8,
            pady=5,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        search_toolbar.pack(fill=tk.X, side=tk.TOP)
        search_toolbar.pack_propagate(False)

        search_icon_lbl = tk.Label(
            search_toolbar,
            text="🔍",
            font=("Segoe UI", 10),
            fg=COLOR_ACCENT_BRIGHT,
            bg=COLOR_TOOLBAR_BG
        )
        search_icon_lbl.pack(side=tk.LEFT, padx=(3, 4))

        # Search Query Entry
        self.entry_search = tk.Entry(
            search_toolbar,
            font=FONT_BODY_BOLD,
            bg="#0A0A10",
            fg="#FFFFFF",
            insertbackground=COLOR_ACCENT_BRIGHT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#2A1218",
            highlightcolor=COLOR_ACCENT_BRIGHT,
            width=18
        )
        self.entry_search.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        self.entry_search.bind("<Return>", lambda event: self.search_records())

        # Category Filter Dropdown
        filter_lbl = tk.Label(
            search_toolbar,
            text="FILTER:",
            font=FONT_CARD_TAG,
            fg="#94A3B8",
            bg=COLOR_TOOLBAR_BG
        )
        filter_lbl.pack(side=tk.LEFT, padx=(3, 3))

        filter_options = ("All Categories",) + CATEGORIES
        self.combo_filter = ttk.Combobox(
            search_toolbar,
            values=filter_options,
            state="readonly",
            style="Crimson.TCombobox",
            width=13,
            font=("Segoe UI", 9)
        )
        self.combo_filter.current(0)
        self.combo_filter.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda event: self.search_records())

        # Search Button
        btn_search = tk.Button(
            search_toolbar,
            text="SEARCH",
            font=FONT_BTN,
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_BRIGHT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self.search_records
        )
        btn_search.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))

        # Reset Filter Button
        btn_reset = tk.Button(
            search_toolbar,
            text="RESET",
            font=FONT_BTN,
            bg="#151520",
            fg=COLOR_TEXT_SECONDARY,
            activebackground="#252535",
            activeforeground="#FFFFFF",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self.reset_search
        )
        btn_reset.pack(side=tk.LEFT, fill=tk.Y)

        # View Switcher Button in Toolbar
        self.btn_toggle_view = tk.Button(
            search_toolbar,
            text="📊 LIVE GRAPH",
            font=FONT_BTN,
            bg="#181124",
            fg="#C084FC",
            activebackground="#2E1A47",
            activeforeground="#FFFFFF",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self.toggle_view_mode
        )
        self.btn_toggle_view.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))

        # Quick Restock Helper Button on far right of toolbar
        btn_restock = tk.Button(
            search_toolbar,
            text="⚡ QUICK +5 STOCK",
            font=FONT_BTN,
            bg="#101827",
            fg="#38BDF8",
            activebackground="#1E293B",
            activeforeground="#FFFFFF",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self.quick_restock
        )
        btn_restock.pack(side=tk.RIGHT, fill=tk.Y)

        # Content View Container (Switches between Table View and Live Animated Graph)
        self.view_container = tk.Frame(self.right_panel, bg=COLOR_SURFACE)
        self.view_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # ----------------------------------------------------------------------
        # VIEW 1: Treeview Table Frame
        # ----------------------------------------------------------------------
        self.table_frame = tk.Frame(self.view_container, bg=COLOR_SURFACE)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", style="Crimson.Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal")

        # Treeview Widget
        column_ids = [col[0] for col in COLUMN_DEFINITIONS]
        self.tree = ttk.Treeview(
            self.table_frame,
            columns=column_ids,
            show="headings",
            selectmode="browse",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Setup Table Columns and Headings using Tuple definitions
        for col_id, col_name, width, alignment in COLUMN_DEFINITIONS:
            self.tree.heading(col_id, text=col_name, anchor=alignment)
            self.tree.column(col_id, width=width, minwidth=60, anchor=alignment)

        # Configure visual row tags for stock levels
        self.tree.tag_configure("row_even", background=COLOR_SURFACE)
        self.tree.tag_configure("row_odd", background="#191924")
        self.tree.tag_configure("status_out", foreground=COLOR_DANGER)
        self.tree.tag_configure("status_low", foreground=COLOR_WARNING)
        self.tree.tag_configure("status_normal", foreground=COLOR_SUCCESS)

        # Bind row selection to form autofill
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_row_selected)

        # ----------------------------------------------------------------------
        # VIEW 2: Animated Live Graph Frame
        # ----------------------------------------------------------------------
        self.chart_frame = tk.Frame(self.view_container, bg=COLOR_SURFACE)

        # Chart Controls Header Bar
        chart_top_bar = tk.Frame(self.chart_frame, bg="#0C0C14", height=42, padx=12, pady=6)
        chart_top_bar.pack(fill=tk.X, side=tk.TOP)
        chart_top_bar.pack_propagate(False)

        chart_title_lbl = tk.Label(
            chart_top_bar,
            text="📊 CATEGORY STOCK DISTRIBUTION & FINANCIAL VALUATION",
            font=FONT_SECTION,
            fg=COLOR_ACCENT_BRIGHT,
            bg="#0C0C14"
        )
        chart_title_lbl.pack(side=tk.LEFT)

        btn_reanim = tk.Button(
            chart_top_bar,
            text="↺ RE-ANIMATE",
            font=FONT_CARD_TAG,
            bg="#201017",
            fg=COLOR_ACCENT_BRIGHT,
            activebackground=COLOR_ACCENT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=10,
            cursor="hand2",
            command=self.animate_chart
        )
        btn_reanim.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_mode_val = tk.Button(
            chart_top_bar,
            text="VALUATION ($)",
            font=FONT_CARD_TAG,
            bg="#14141F",
            fg=COLOR_TEXT_SECONDARY,
            activebackground="#202030",
            activeforeground="#FFFFFF",
            bd=0,
            padx=10,
            cursor="hand2",
            command=lambda: self.set_chart_mode("valuation")
        )
        self.btn_mode_val.pack(side=tk.RIGHT, padx=4)

        self.btn_mode_units = tk.Button(
            chart_top_bar,
            text="STOCK UNITS",
            font=FONT_CARD_TAG,
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_BRIGHT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=10,
            cursor="hand2",
            command=lambda: self.set_chart_mode("units")
        )
        self.btn_mode_units.pack(side=tk.RIGHT, padx=4)

        # High-Performance Custom Canvas for 60 FPS Animated Chart
        self.chart_canvas = tk.Canvas(
            self.chart_frame,
            bg="#07070B",
            highlightbackground="#221217",
            highlightthickness=1
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        self.chart_canvas.bind("<Configure>", lambda e: self.animate_chart() if self.current_view == "graph" else None)

        # Table Footer / Action Bar
        table_footer = tk.Frame(self.right_panel, bg=COLOR_SURFACE_LIGHT, height=34, padx=8, pady=3)
        table_footer.pack(fill=tk.X, side=tk.BOTTOM)
        table_footer.pack_propagate(False)

        # Data Persistence and File Operation Buttons
        btn_save_csv = tk.Button(
            table_footer,
            text="💾  SAVE TO CSV",
            font=FONT_BTN,
            bg=COLOR_ACCENT,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_BRIGHT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=9,
            cursor="hand2",
            command=self.save_data_to_csv
        )
        btn_save_csv.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        btn_reload = tk.Button(
            table_footer,
            text="📂  RELOAD DISK DATA",
            font=FONT_BTN,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_PRIMARY,
            activebackground=COLOR_SURFACE_LIGHT,
            activeforeground="#FFFFFF",
            bd=0,
            padx=9,
            cursor="hand2",
            command=self.load_data_from_csv
        )
        btn_reload.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        btn_export = tk.Button(
            table_footer,
            text="📄  EXPORT AUDIT REPORT",
            font=FONT_BTN,
            bg="#0D2218",
            fg=COLOR_SUCCESS,
            activebackground="#14382A",
            activeforeground="#FFFFFF",
            bd=0,
            padx=9,
            cursor="hand2",
            command=self.export_audit_report
        )
        btn_export.pack(side=tk.LEFT, fill=tk.Y)

        btn_footer_graph = tk.Button(
            table_footer,
            text="📊  TOGGLE GRAPH",
            font=FONT_BTN,
            bg="#181124",
            fg="#C084FC",
            activebackground="#2E1A47",
            activeforeground="#FFFFFF",
            bd=0,
            padx=9,
            cursor="hand2",
            command=self.toggle_view_mode
        )
        btn_footer_graph.pack(side=tk.LEFT, fill=tk.Y, padx=(6, 0))

        self.table_count_lbl = tk.Label(
            table_footer,
            text="Showing 0 records",
            font=FONT_CARD_TAG,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SURFACE_LIGHT
        )
        self.table_count_lbl.pack(side=tk.RIGHT, pady=2)

    def _build_status_bar(self):
        """Creates bottom status bar giving real-time feedback to the user."""
        self.status_bar = tk.Frame(self.root, bg="#08080B", height=24, padx=12)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_message = tk.Label(
            self.status_bar,
            text="Ready. Crimson Inventory Pro initialized.",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_SECONDARY,
            bg="#08080B"
        )
        self.status_message.pack(side=tk.LEFT)

        self.status_time = tk.Label(
            self.status_bar,
            text="",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_SECONDARY,
            bg="#08080B"
        )
        self.status_time.pack(side=tk.RIGHT)
        self._update_clock()

    def _update_clock(self):
        """Updates real-time clock in status bar."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.status_time.config(text=now_str)
        self.root.after(1000, self._update_clock)

    def _set_status(self, message: str, is_error: bool = False):
        """Helper to display informative status messages."""
        fg_color = COLOR_DANGER if is_error else COLOR_TEXT_SECONDARY
        self.status_message.config(text=f"● {message}", fg=fg_color)

    # --------------------------------------------------------------------------
    # UI Component Helper Methods
    # --------------------------------------------------------------------------
    def _create_field_label(self, parent: tk.Widget, text: str) -> tk.Label:
        """Creates standard form field label."""
        lbl = tk.Label(
            parent,
            text=text,
            font=FONT_CARD_TAG,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_SURFACE
        )
        lbl.pack(anchor="w")
        return lbl

    def _create_entry_field(self, parent: tk.Widget) -> tk.Entry:
        """Creates a styled entry field with pure black background and red focus border."""
        entry = tk.Entry(
            parent,
            font=FONT_BODY_BOLD,
            bg=COLOR_INPUT_BG,
            fg="#FFFFFF",
            insertbackground=COLOR_ACCENT_BRIGHT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_BORDER_GLOW
        )
        return entry

    def _create_action_button(self, parent: tk.Widget, text: str, bg: str, fg: str, hover_bg: str, command) -> tk.Button:
        """Creates a styled flat button with dynamic mouse hover animations."""
        btn = tk.Button(
            parent,
            text=text,
            font=FONT_BTN,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground="#FFFFFF",
            bd=0,
            pady=5,
            cursor="hand2",
            command=command
        )
        # Bind hover events for interactive feel
        btn.bind("<Enter>", lambda event: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda event: btn.configure(bg=bg))
        return btn

    # ==========================================================================
    # BUSINESS LOGIC & DATA MANIPULATION
    # ==========================================================================

    def auto_generate_sku(self):
        """
        Generates the next available sequential SKU using a while loop and Set membership.
        USES: Control Structure (while loop) + Set membership check.
        """
        prefix = "SKU-"
        num = 1001
        # WHILE LOOP: Iterates until finding an ID not present in the unique_ids Set
        while f"{prefix}{num}" in self.unique_ids:
            num += 1

        new_sku = f"{prefix}{num}"
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, new_sku)
        self._set_status(f"Auto-generated next available SKU: {new_sku}")

    def _validate_inputs(self, is_update: bool = False) -> tuple:
        """
        Performs thorough input validation on all form fields.
        USES: Control structures (if-elif-else), exception handling (try-except).
        RETURNS: (is_valid: bool, validated_data_dict_or_error_message)
        """
        item_id = self.entry_id.get().strip().upper()
        name = self.entry_name.get().strip()
        category = self.combo_category.get().strip()
        qty_raw = self.entry_qty.get().strip()
        price_raw = self.entry_price.get().strip()
        supplier = self.entry_supplier.get().strip()

        # Validation Rule 1: Required non-empty fields
        if not item_id:
            return False, "Item ID cannot be blank. Please enter a valid SKU (e.g., SKU-1001)."
        if not name:
            return False, "Item Name cannot be blank. Please provide a descriptive title."
        if not category or category not in CATEGORIES:
            return False, f"Please select a valid Category from the dropdown list."

        # Validation Rule 2: Set-based Duplicate ID Check
        if not is_update:
            if item_id in self.unique_ids:
                return False, f"Item ID '{item_id}' already exists in inventory! IDs must be unique."
        else:
            # During update, if ID changed to an existing ID belonging to someone else
            if self.selected_item_id and item_id != self.selected_item_id and item_id in self.unique_ids:
                return False, f"Cannot rename to '{item_id}' because that ID already belongs to another item!"

        # Validation Rule 3: Quantity numeric validation (Integer >= 0)
        try:
            quantity = int(qty_raw)
            if quantity < 0:
                return False, "Quantity cannot be negative. Please enter 0 or a positive whole number."
        except ValueError:
            return False, f"Invalid Quantity '{qty_raw}'. Quantity must be a valid integer number."

        # Validation Rule 4: Price numeric validation (Float >= 0)
        try:
            price = float(price_raw)
            if price < 0.0:
                return False, "Unit Price cannot be negative. Please enter a positive decimal value."
        except ValueError:
            return False, f"Invalid Unit Price '{price_raw}'. Price must be a numeric value (e.g. 29.99)."

        # Fallback supplier
        if not supplier:
            supplier = "General Warehouse"

        # Compute derived values
        total_value = calculate_item_valuation(quantity, price)
        status = determine_stock_status(quantity)
        date_added = datetime.date.today().strftime("%Y-%m-%d")

        # ==============================================================================
        # DATA STRUCTURE 4: DICTIONARY (Required Assignment Concept)
        # WHERE: item_record = {...}
        # WHY:   Stores structured key-value attributes for an individual entity.
        #        Provides semantic access by key name (e.g. record['price']) instead of
        #        fragile positional index offsets.
        # ==============================================================================
        item_record = {
            "id": item_id,
            "name": name,
            "category": category,
            "quantity": quantity,
            "price": round(price, 2),
            "total": total_value,
            "status": status,
            "supplier": supplier,
            "date_added": date_added
        }

        return True, item_record

    def add_item(self):
        """
        Adds a new item to the inventory system.
        Demonstrates: List append, Set add, Input Validation, Messageboxes.
        """
        is_valid, result = self._validate_inputs(is_update=False)
        if not is_valid:
            messagebox.showerror("Validation Error", result)
            self._set_status(result, is_error=True)
            return

        new_item = result

        # DATA STRUCTURE USAGE:
        # 1. Add to List
        self.inventory_records.append(new_item)
        # 2. Add to Set for duplicate prevention
        self.unique_ids.add(new_item["id"])

        # Refresh interface
        self.refresh_table(self.inventory_records)
        self.update_kpis()
        self.clear_form()

        self._set_status(f"Successfully added item '{new_item['name']}' ({new_item['id']}).")
        self.show_toast(f"✔ Product '{new_item['name']}' added to inventory!", kind="success")
        messagebox.showinfo("Success", f"Product '{new_item['name']}' has been added successfully!")

    def update_item(self):
        """
        Updates an existing inventory record.
        Demonstrates: Selection handling, searching list, updating dictionary, Set sync.
        """
        if not self.selected_item_id:
            messagebox.showwarning("Selection Required", "Please select a row from the table to update.")
            return

        is_valid, updated_data = self._validate_inputs(is_update=True)
        if not is_valid:
            messagebox.showerror("Validation Error", updated_data)
            self._set_status(updated_data, is_error=True)
            return

        # FOR LOOP: Find and update the record in the list
        record_found = False
        old_id = self.selected_item_id

        for index, item in enumerate(self.inventory_records):
            if item["id"] == old_id:
                # Keep original creation date if already present
                updated_data["date_added"] = item.get("date_added", updated_data["date_added"])
                self.inventory_records[index] = updated_data
                record_found = True
                break

        if record_found:
            # Sync Set if ID changed
            if old_id != updated_data["id"]:
                self.unique_ids.remove(old_id)
                self.unique_ids.add(updated_data["id"])

            self.selected_item_id = updated_data["id"]
            self.refresh_table(self.inventory_records)
            self.update_kpis()
            self._set_status(f"Updated record for '{updated_data['id']}'.")
            self.show_toast(f"✎ Product '{updated_data['id']}' updated successfully!", kind="info")
            messagebox.showinfo("Record Updated", f"Product '{updated_data['id']}' successfully updated!")
        else:
            messagebox.showerror("Error", f"Record '{old_id}' was not found in active dataset.")

    def delete_item(self):
        """
        Deletes a selected record after user confirmation dialog.
        Demonstrates: messagebox.askyesno, List removal, Set removal.
        """
        if not self.selected_item_id:
            messagebox.showwarning("Selection Required", "Please select an item from the table to delete.")
            return

        # Confirmation Dialog
        confirmed = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete record '{self.selected_item_id}'?\nThis action cannot be undone."
        )
        if not confirmed:
            return

        target_id = self.selected_item_id

        # FOR LOOP: Locate and remove item from list
        for index, item in enumerate(self.inventory_records):
            if item["id"] == target_id:
                del self.inventory_records[index]
                break

        # Remove from Set
        if target_id in self.unique_ids:
            self.unique_ids.remove(target_id)

        self.selected_item_id = None
        self.clear_form()
        self.refresh_table(self.inventory_records)
        self.update_kpis()

        self._set_status(f"Deleted record '{target_id}' from inventory.")
        self.show_toast(f"🗑 Record '{target_id}' permanently deleted.", kind="danger")
        messagebox.showinfo("Deleted", f"Record '{target_id}' has been removed from inventory.")

    def quick_restock(self):
        """Quickly adds +5 units to the currently selected item."""
        if not self.selected_item_id:
            messagebox.showwarning("Selection Required", "Please select a row in the table to quick-restock.")
            return

        target_id = self.selected_item_id
        for item in self.inventory_records:
            if item["id"] == target_id:
                item["quantity"] += 5
                item["total"] = calculate_item_valuation(item["quantity"], item["price"])
                item["status"] = determine_stock_status(item["quantity"])
                self.refresh_table(self.inventory_records)
                self.update_kpis()
                self._populate_form_with_item(item)
                self._set_status(f"Restocked +5 units for '{item['name']}'. New Qty: {item['quantity']}")
                self.show_toast(f"⚡ Restocked +5 units for '{item['name']}' (Qty: {item['quantity']})", kind="info")
                return

    def clear_form(self):
        """Resets all input fields and clears table selection."""
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        if CATEGORIES:
            self.combo_category.current(0)
        self.entry_qty.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_supplier.delete(0, tk.END)

        self.selected_item_id = None
        self.tree.selection_remove(self.tree.selection())
        self._set_status("Form fields cleared.")

    def on_tree_row_selected(self, event):
        """
        Event handler triggered when a user clicks any row in the Treeview.
        Automatically populates the left input form with the selected record's data.
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item_row = self.tree.item(selected_items[0])
        values = item_row.get("values", [])
        if not values:
            return

        item_id = str(values[0])
        self.selected_item_id = item_id

        # Look up record in list
        for item in self.inventory_records:
            if item["id"] == item_id:
                self._populate_form_with_item(item)
                self._set_status(f"Selected item: {item['name']} ({item['id']})")
                break

    def _populate_form_with_item(self, item: dict):
        """Fills the form widgets with item dictionary values."""
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, item["id"])

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, item["name"])

        cat_val = item.get("category", "")
        if cat_val in CATEGORIES:
            self.combo_category.set(cat_val)

        self.entry_qty.delete(0, tk.END)
        self.entry_qty.insert(0, str(item["quantity"]))

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, str(item["price"]))

        self.entry_supplier.delete(0, tk.END)
        self.entry_supplier.insert(0, item.get("supplier", ""))

    # ==========================================================================
    # SEARCH & FILTERING (Bonus Requirement)
    # ==========================================================================

    def search_records(self):
        """
        Performs multi-criteria filtering across Item ID, Name, Supplier, and Category.
        USES: Control structures (if conditions inside for loop).
        """
        query = self.entry_search.get().strip().lower()
        selected_category = self.combo_filter.get().strip()

        # Filter records
        filtered_list = []
        for item in self.inventory_records:
            # Check Category filter
            if selected_category != "All Categories" and item["category"] != selected_category:
                continue

            # Check Search Query match
            if query:
                id_match = query in item["id"].lower()
                name_match = query in item["name"].lower()
                supplier_match = query in item.get("supplier", "").lower()
                if not (id_match or name_match or supplier_match):
                    continue

            filtered_list.append(item)

        self.refresh_table(filtered_list)
        self._set_status(f"Search completed. Found {len(filtered_list)} matching items.")

    def reset_search(self):
        """Resets search query and category filters back to full dataset."""
        self.entry_search.delete(0, tk.END)
        self.combo_filter.current(0)
        self.refresh_table(self.inventory_records)
        self._set_status("Filters reset. Showing all inventory items.")

    # ==========================================================================
    # TABLE RENDERING & KPI CALCULATION
    # ==========================================================================

    def refresh_table(self, records_to_show: list):
        """
        Clears and repopulates the Treeview table with records.
        Applies alternating row striping and stock status badges.
        USES: for loop with enumerate.
        """
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate rows
        for index, item in enumerate(records_to_show):
            row_tag = "row_even" if index % 2 == 0 else "row_odd"

            # Determine status tag
            status = item.get("status", "")
            if status == "Out of Stock":
                status_tag = "status_out"
            elif status == "Low Stock":
                status_tag = "status_low"
            else:
                status_tag = "status_normal"

            row_values = (
                item["id"],
                item["name"],
                item["category"],
                item["quantity"],
                f"{item['price']:.2f}",
                f"{item['total']:.2f}",
                item["status"],
                item.get("supplier", ""),
                item.get("date_added", "")
            )

            self.tree.insert(
                "",
                tk.END,
                values=row_values,
                tags=(row_tag, status_tag)
            )

        self.table_count_lbl.config(text=f"Showing {len(records_to_show)} of {len(self.inventory_records)} records")

        # If currently in Live Graph mode, re-render animated chart with updated dataset
        if self.current_view == "graph":
            self.animate_chart()

    # ==========================================================================
    # INTERACTIVE DATA VISUALIZER & GRAPH ANIMATIONS
    # ==========================================================================

    def toggle_view_mode(self):
        """Switches between Treeview table mode and Canvas animated graph mode."""
        if self.current_view == "table":
            self.show_graph_view()
        else:
            self.show_table_view()

    def show_table_view(self):
        """Displays the Treeview data table and hides the canvas chart."""
        self.current_view = "table"
        if self.chart_anim_job:
            try:
                self.root.after_cancel(self.chart_anim_job)
            except Exception:
                pass
            self.chart_anim_job = None
        self.chart_frame.pack_forget()
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self.btn_toggle_view.config(text="📊 LIVE GRAPH", bg="#181124", fg="#C084FC")
        self._set_status("Switched to Inventory Table View.")

    def show_graph_view(self):
        """Displays the interactive animated canvas chart and hides the table."""
        self.current_view = "graph"
        self.table_frame.pack_forget()
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        self.btn_toggle_view.config(text="📋 TABLE VIEW", bg="#1A1528", fg="#38BDF8")
        self._set_status("Switched to Live Animated Inventory Graph Visualizer.")
        self.root.after(30, lambda: self.animate_chart(step=0))

    def set_chart_mode(self, mode: str):
        """Switches graph visualization between units and dollar valuation."""
        self.graph_mode = mode
        if mode == "units":
            self.btn_mode_units.config(bg=COLOR_ACCENT, fg="#FFFFFF")
            self.btn_mode_val.config(bg="#14141F", fg=COLOR_TEXT_SECONDARY)
            self.show_toast("📊 Switched graph to Stock Units mode", kind="info")
        else:
            self.btn_mode_units.config(bg="#14141F", fg=COLOR_TEXT_SECONDARY)
            self.btn_mode_val.config(bg=COLOR_ACCENT, fg="#FFFFFF")
            self.show_toast("💰 Switched graph to Valuation ($) mode", kind="info")
        self.animate_chart(step=0)

    def animate_chart(self, step: int = 0, max_steps: int = 24):
        """
        Creative Animation 6: High-performance 60 FPS animated bar visualizer.
        Renders live distribution of stock units or capital valuation across categories.
        Uses cubic ease-out curve for smooth deceleration.
        """
        if self.chart_anim_job:
            try:
                self.root.after_cancel(self.chart_anim_job)
            except Exception:
                pass
            self.chart_anim_job = None

        if self.current_view != "graph":
            return

        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()

        if w < 120 or h < 120:
            self.chart_anim_job = self.root.after(40, lambda: self.animate_chart(step, max_steps))
            return

        self.chart_canvas.delete("all")

        cat_colors = {
            "Peripherals": {"bar": "#FF2A55", "cap": "#FFA3BA", "track": "#1F0A12"},
            "Hardware":    {"bar": "#38BDF8", "cap": "#BAE6FD", "track": "#081822"},
            "Electronics": {"bar": "#A855F7", "cap": "#E9D5FF", "track": "#170A24"},
            "Networking":  {"bar": "#34D399", "cap": "#A7F3D0", "track": "#091F14"},
            "Accessories": {"bar": "#F59E0B", "cap": "#FDE68A", "track": "#221808"},
            "Software":    {"bar": "#EC4899", "cap": "#FBCFE8", "track": "#220817"}
        }
        default_color = {"bar": "#FF2A55", "cap": "#FFA3BA", "track": "#1F0A12"}

        cat_data = {cat: {"units": 0, "val": 0.0, "skus": 0} for cat in CATEGORIES}
        total_units = 0
        total_val = 0.0

        for item in self.inventory_records:
            cat = item.get("category", "")
            qty = item.get("quantity", 0)
            val = item.get("total", 0.0)
            total_units += qty
            total_val += val
            if cat in cat_data:
                cat_data[cat]["units"] += qty
                cat_data[cat]["val"] += val
                cat_data[cat]["skus"] += 1

        is_units = (self.graph_mode == "units")
        vals = [cat_data[cat]["units"] if is_units else cat_data[cat]["val"] for cat in CATEGORIES]
        max_val = max(vals) if vals else 1
        if max_val <= 0:
            max_val = 1

        grid_max = max_val * 1.18

        ratio = min(1.0, (step + 1) / max_steps)
        ease = 1.0 - (1.0 - ratio) ** 3

        margin_left = 90
        margin_right = 40
        margin_top = 55
        margin_bottom = 60

        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom
        base_y = margin_top + plot_h

        # 1. Background gridlines and Y-axis scale markings
        num_gridlines = 4
        for g in range(num_gridlines + 1):
            gy = base_y - (g / num_gridlines) * plot_h
            g_val = (g / num_gridlines) * grid_max

            self.chart_canvas.create_line(
                margin_left - 8, gy, w - margin_right, gy,
                fill="#161420" if g > 0 else "#2C1B24",
                width=1 if g > 0 else 2,
                dash=(3, 3) if g > 0 else ()
            )

            if is_units:
                label_txt = f"{int(round(g_val)):,} u"
            else:
                label_txt = f"${g_val:,.0f}" if g_val >= 1000 else f"${g_val:.0f}"

            self.chart_canvas.create_text(
                margin_left - 14, gy,
                text=label_txt,
                anchor="e",
                fill="#64748B",
                font=("Segoe UI", 8)
            )

        # 2. Header Status Badge inside Canvas
        top_cat = max(CATEGORIES, key=lambda c: cat_data[c]["units"] if is_units else cat_data[c]["val"])
        top_cat_val = cat_data[top_cat]["units"] if is_units else cat_data[top_cat]["val"]
        top_metric_str = f"{top_cat_val:,} units" if is_units else f"${top_cat_val:,.2f}"

        mode_badge = "MODE: STOCK UNITS" if is_units else "MODE: VALUATION ($)"
        summary_txt = f"TOTAL: {total_units:,} units" if is_units else f"TOTAL ASSETS: ${total_val:,.2f}"

        self.chart_canvas.create_text(
            margin_left, 24,
            text=f"✦ {mode_badge}  |  {summary_txt}  |  LEADER: {top_cat.upper()} ({top_metric_str})",
            anchor="w",
            fill=COLOR_ACCENT_BRIGHT,
            font=("Segoe UI Semibold", 9)
        )

        # 3. Render animated category columns
        num_bars = len(CATEGORIES)
        slot_w = plot_w / max(1, num_bars)
        bar_w = max(24, min(68, slot_w * 0.62))

        for idx, cat in enumerate(CATEGORIES):
            c_info = cat_colors.get(cat, default_color)
            val = cat_data[cat]["units"] if is_units else cat_data[cat]["val"]

            center_x = margin_left + idx * slot_w + (slot_w / 2)
            x0 = center_x - (bar_w / 2)
            x1 = center_x + (bar_w / 2)

            self.chart_canvas.create_rectangle(
                x0, margin_top, x1, base_y,
                fill=c_info["track"],
                outline="#121019",
                width=1
            )

            target_bar_h = (val / grid_max) * plot_h
            current_bar_h = target_bar_h * ease
            top_y = base_y - current_bar_h

            if current_bar_h > 1:
                self.chart_canvas.create_rectangle(
                    x0 + 1, top_y, x1 - 1, base_y,
                    fill=c_info["bar"],
                    outline=""
                )
                cap_h = min(4, current_bar_h)
                self.chart_canvas.create_rectangle(
                    x0 + 1, top_y, x1 - 1, top_y + cap_h,
                    fill=c_info["cap"],
                    outline=""
                )

            animated_disp_val = val * ease
            if is_units:
                val_text = f"{int(round(animated_disp_val)):,}"
            else:
                val_text = f"${animated_disp_val:,.0f}"

            val_y = max(margin_top - 16, top_y - 10)
            self.chart_canvas.create_text(
                center_x, val_y,
                text=val_text,
                anchor="s",
                fill="#FFFFFF",
                font=("Segoe UI Bold", 9)
            )

            self.chart_canvas.create_text(
                center_x, base_y + 14,
                text=cat,
                anchor="n",
                fill=c_info["bar"],
                font=("Segoe UI Bold", 8)
            )

            sku_count = cat_data[cat]["skus"]
            self.chart_canvas.create_text(
                center_x, base_y + 30,
                text=f"{sku_count} SKUs",
                anchor="n",
                fill="#64748B",
                font=("Segoe UI", 7)
            )

        if step < max_steps - 1:
            self.chart_anim_job = self.root.after(
                20, lambda: self.animate_chart(step + 1, max_steps)
            )
        else:
            self.chart_anim_job = None

    # ==========================================================================
    # CREATIVE ANIMATIONS ENGINE
    # ==========================================================================

    def _animate_laser_scanner(self):
        """Creative Animation 1: Sweeps glowing cyber laser beam across the top banner."""
        try:
            width = self.root.winfo_width()
            if width < 600:
                width = 1320
            self.scanner_pos += 9
            if self.scanner_pos > width + 180:
                self.scanner_pos = -160
            self.scanner_canvas.coords(self.laser_beam, self.scanner_pos, 1, self.scanner_pos + 160, 1)
            self.scanner_canvas.coords(self.laser_core, self.scanner_pos + 40, 1, self.scanner_pos + 120, 1)
            self.root.after(35, self._animate_laser_scanner)
        except Exception:
            pass

    def _animate_heartbeat(self):
        """Creative Animation 2: Pulses the status pill like a live system beacon."""
        try:
            self.beacon_state = 1 - self.beacon_state
            if self.beacon_state == 1:
                self.sys_pill.config(fg="#34D399", bg="#103322")
            else:
                self.sys_pill.config(fg="#059669", bg="#091E14")
            self.root.after(750, self._animate_heartbeat)
        except Exception:
            pass

    def _animate_alert_pulse(self):
        """Creative Animation 3: Subtle breathing glow on Low Stock Alert card when alerts exist."""
        try:
            low_count = 0
            for item in self.inventory_records:
                if item["quantity"] <= 5:
                    low_count += 1

            if low_count > 0 and "kpi_alerts" in self.kpi_card_glows:
                self.alert_pulse_state = 1 - self.alert_pulse_state
                glow_color = COLOR_ACCENT_BRIGHT if self.alert_pulse_state == 1 else "#6B141E"
                self.kpi_card_glows["kpi_alerts"].config(bg=glow_color)
            elif "kpi_alerts" in self.kpi_card_glows:
                self.kpi_card_glows["kpi_alerts"].config(bg=COLOR_SUCCESS)

            self.root.after(850, self._animate_alert_pulse)
        except Exception:
            pass

    def update_kpis(self, animated: bool = True):
        """
        Recalculates summary metrics using loops and conditional logic.
        Triggers Creative Animation 4: Smooth Number Ticker Roll-Up!
        """
        total_items = len(self.inventory_records)
        total_units = 0
        total_valuation = 0.0
        low_stock_count = 0

        # FOR LOOP: Compute aggregate metrics
        for item in self.inventory_records:
            qty = item["quantity"]
            total_units += qty
            total_valuation += item["total"]
            if qty <= 5:
                low_stock_count += 1

        target_kpis = {
            "items": total_items,
            "units": total_units,
            "value": total_valuation,
            "alerts": low_stock_count
        }

        if animated and self.cached_kpis:
            self._animate_kpi_roll(self.cached_kpis.copy(), target_kpis, step=0, max_steps=14)
        else:
            self.kpi_labels["kpi_items"].config(text=str(total_items))
            self.kpi_labels["kpi_units"].config(text=f"{total_units:,}")
            self.kpi_labels["kpi_value"].config(text=format_currency(total_valuation))
            self.kpi_labels["kpi_alerts"].config(
                text=str(low_stock_count),
                fg=COLOR_DANGER if low_stock_count > 0 else COLOR_SUCCESS
            )
            self.cached_kpis = target_kpis

    def _animate_kpi_roll(self, start_kpi: dict, target_kpi: dict, step: int = 0, max_steps: int = 14):
        """Smoothly interpolates numbers with an ease-out cubic curve."""
        try:
            ratio = min(1.0, step / max_steps)
            ease = 1.0 - (1.0 - ratio) ** 3

            cur_items = int(start_kpi["items"] + (target_kpi["items"] - start_kpi["items"]) * ease)
            cur_units = int(start_kpi["units"] + (target_kpi["units"] - start_kpi["units"]) * ease)
            cur_val = start_kpi["value"] + (target_kpi["value"] - start_kpi["value"]) * ease
            cur_alerts = int(start_kpi["alerts"] + (target_kpi["alerts"] - start_kpi["alerts"]) * ease)

            self.kpi_labels["kpi_items"].config(text=str(cur_items))
            self.kpi_labels["kpi_units"].config(text=f"{cur_units:,}")
            self.kpi_labels["kpi_value"].config(text=format_currency(cur_val))
            self.kpi_labels["kpi_alerts"].config(
                text=str(cur_alerts),
                fg=COLOR_DANGER if cur_alerts > 0 else COLOR_SUCCESS
            )

            if step < max_steps:
                self.root.after(25, lambda: self._animate_kpi_roll(start_kpi, target_kpi, step + 1, max_steps))
            else:
                self.cached_kpis = target_kpi
        except Exception:
            self.cached_kpis = target_kpi

    def show_toast(self, message: str, kind: str = "success"):
        """
        Creative Animation 5: Floating in-app pill toast with slide-in & auto-fade.
        Provides modern, delightful feedback without intrusive blocking dialogs.
        """
        try:
            if self.toast_frame:
                try:
                    self.toast_frame.destroy()
                except Exception:
                    pass
                self.toast_frame = None

            if self.toast_hide_job:
                try:
                    self.root.after_cancel(self.toast_hide_job)
                except Exception:
                    pass
                self.toast_hide_job = None

            border_colors = {
                "success": ("#10B981", "#091E14"),
                "info": ("#38BDF8", "#0B1D2A"),
                "danger": ("#EF4444", "#250B10"),
                "warning": ("#F59E0B", "#261708"),
            }
            border_color, bg_color = border_colors.get(kind, ("#FF2A55", "#1B0D13"))

            self.toast_frame = tk.Frame(
                self.right_panel,
                bg=bg_color,
                highlightbackground=border_color,
                highlightthickness=1,
                padx=16,
                pady=7
            )

            toast_lbl = tk.Label(
                self.toast_frame,
                text=message,
                font=FONT_BTN,
                fg="#FFFFFF",
                bg=bg_color
            )
            toast_lbl.pack(side=tk.LEFT)

            # Slide-in animation
            def _slide_in(step=0, max_step=8):
                if not self.toast_frame:
                    return
                ratio = step / max_step
                rely = 1.02 - (0.12 * ratio)
                self.toast_frame.place(relx=0.5, rely=rely, anchor="center")
                if step < max_step:
                    self.root.after(20, lambda: _slide_in(step + 1, max_step))

            _slide_in()

            def _fade_out():
                if self.toast_frame:
                    try:
                        self.toast_frame.destroy()
                    except Exception:
                        pass
                    self.toast_frame = None

            self.toast_hide_job = self.root.after(2400, _fade_out)
        except Exception as e:
            print(f"Toast notice: {e}")

    # ==========================================================================
    # FILE HANDLING: CSV IMPORT / EXPORT / RECOVERY
    # (Required Assignment Concept: File Handling with .csv or .txt)
    # ==========================================================================

    def load_data_from_csv(self):
        """
        Reads inventory data from CSV file on application startup.
        Demonstrates: File handling, try-except blocks, CSV reader, List and Set population.
        """
        self.inventory_records.clear()
        self.unique_ids.clear()

        # Check if file exists; if not, create seed sample data file
        if not os.path.exists(self.data_filepath):
            self._create_sample_csv_data()

        try:
            with open(self.data_filepath, mode="r", encoding="utf-8-sig", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        qty = int(row.get("quantity", 0))
                        price = float(row.get("price", 0.0))
                        item_id = row.get("id", "").strip()

                        if not item_id:
                            continue

                        # Construct clean record dictionary
                        record = {
                            "id": item_id,
                            "name": row.get("name", "").strip(),
                            "category": row.get("category", "General").strip(),
                            "quantity": qty,
                            "price": round(price, 2),
                            "total": calculate_item_valuation(qty, price),
                            "status": determine_stock_status(qty),
                            "supplier": row.get("supplier", "N/A").strip(),
                            "date_added": row.get("date_added", datetime.date.today().strftime("%Y-%m-%d")).strip()
                        }

                        # Append to List & Set
                        self.inventory_records.append(record)
                        self.unique_ids.add(item_id)

                    except (ValueError, TypeError) as parse_err:
                        print(f"Skipping invalid CSV record: {parse_err}")
                        continue

            self.refresh_table(self.inventory_records)
            self.update_kpis()
            self._set_status(f"Loaded {len(self.inventory_records)} records from {os.path.basename(self.data_filepath)}.")

        except Exception as file_err:
            messagebox.showerror("File Read Error", f"Failed to read database file:\n{file_err}")
            self._set_status(f"File read error: {file_err}", is_error=True)

    def save_data_to_csv(self):
        """
        Saves all inventory records from memory to persistent CSV file.
        Demonstrates: File writing, CSV DictWriter, error handling.
        """
        try:
            fieldnames = ["id", "name", "category", "quantity", "price", "supplier", "date_added"]
            with open(self.data_filepath, mode="w", encoding="utf-8", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.inventory_records:
                    writer.writerow({
                        "id": item["id"],
                        "name": item["name"],
                        "category": item["category"],
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "supplier": item.get("supplier", ""),
                        "date_added": item.get("date_added", "")
                    })

            self._set_status(f"Saved {len(self.inventory_records)} records to {os.path.basename(self.data_filepath)}.")
            self.show_toast(f"💾 Saved {len(self.inventory_records)} records to CSV!", kind="success")
            messagebox.showinfo("File Saved", f"Successfully saved {len(self.inventory_records)} records to {os.path.basename(self.data_filepath)}!")

        except Exception as file_err:
            messagebox.showerror("File Save Error", f"Failed to write database file:\n{file_err}")
            self._set_status(f"File write error: {file_err}", is_error=True)

    def export_audit_report(self):
        """
        Exports a formatted audit and summary report as a .txt file.
        Demonstrates: Text file handling, formatted reporting.
        """
        export_filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents (*.txt)", "*.txt"), ("All Files", "*.*" )],
            initialfile=f"Inventory_Audit_Report_{datetime.date.today().strftime('%Y%m%d')}.txt"
        )
        if not export_filename:
            return

        try:
            with open(export_filename, mode="w", encoding="utf-8") as f:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write("=" * 80 + "\n")
                f.write("CRIMSON INVENTORY PRO - OFFICIAL STOCK AUDIT REPORT\n")
                f.write(f"Generated on: {now}\n")
                f.write("=" * 80 + "\n\n")

                # Summary Section
                total_items = len(self.inventory_records)
                total_units = sum(i["quantity"] for i in self.inventory_records)
                total_val = sum(i["total"] for i in self.inventory_records)
                low_stock = sum(1 for i in self.inventory_records if i["quantity"] <= 5)

                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Unique Products (SKUs) : {total_items}\n")
                f.write(f"Total Physical Units in Stock: {total_units:,}\n")
                f.write(f"Total Gross Valuation        : {format_currency(total_val)}\n")
                f.write(f"Items Requiring Attention    : {low_stock}\n")
                f.write("-" * 40 + "\n\n")

                # Itemized Table
                f.write(f"{'ID':<10} {'NAME':<32} {'CATEGORY':<15} {'QTY':<8} {'PRICE':<10} {'STATUS':<12}\n")
                f.write("-" * 87 + "\n")
                for item in self.inventory_records:
                    f.write(f"{item['id']:<10} {item['name'][:30]:<32} {item['category']:<15} {item['quantity']:<8} ${item['price']:<9.2f} {item['status']:<12}\n")

                f.write("-" * 87 + "\n")
                f.write("*** END OF AUDIT REPORT ***\n")

            messagebox.showinfo("Report Exported", f"Audit report successfully generated:\n{export_filename}")
            self._set_status(f"Exported audit report to {os.path.basename(export_filename)}.")

        except Exception as err:
            messagebox.showerror("Export Error", f"Failed to export report: {err}")

    def _create_sample_csv_data(self):
        """Generates seed sample records if CSV file does not exist on disk."""
        sample_rows = [
            ("SKU-1001", "Crimson Pro Mechanical Keyboard", "Peripherals", 45, 89.99, "CyberGear Ltd", "2026-08-15"),
            ("SKU-1002", "Viper Elite Wireless Mouse", "Peripherals", 62, 49.50, "CyberGear Ltd", "2026-08-18"),
            ("SKU-1003", "HyperFlow 360 Liquid Cooler", "Hardware", 18, 139.00, "ThermalTech Inc", "2026-08-20"),
            ("SKU-1004", "Quantum Core i9 Processor 3.8GHz", "Hardware", 8, 429.99, "Apex Silicon", "2026-08-22"),
            ("SKU-1005", "Titanium RTX 4080 OC GPU", "Hardware", 3, 1199.00, "Apex Silicon", "2026-08-25"),
            ("SKU-1006", "UltraWide 34in Curved OLED Monitor", "Electronics", 12, 699.99, "VisionMatrix Co", "2026-08-27"),
            ("SKU-1007", "Phantom 7.1 Surround Headset", "Peripherals", 30, 79.99, "AudioWave Labs", "2026-08-30"),
            ("SKU-1008", "Gigabit Cat7 Shielded Cable 15m", "Networking", 110, 14.50, "NetLink Solutions", "2026-09-01"),
            ("SKU-1009", "AX3000 Wi-Fi 6 Gaming Router", "Networking", 15, 129.99, "NetLink Solutions", "2026-09-02"),
            ("SKU-1010", "Crimson Surge 850W Modular PSU", "Hardware", 4, 115.00, "PowerForce Corp", "2026-09-03"),
            ("SKU-1011", "CyberShield Security Suite", "Software", 85, 39.99, "Sentience Soft", "2026-09-03"),
            ("SKU-1012", "Braided USB-C Cable 2m", "Accessories", 150, 9.99, "HyperAccessories", "2026-09-04"),
            ("SKU-1013", "RGB Aluminum Headphone Stand", "Accessories", 22, 29.99, "HyperAccessories", "2026-09-04"),
            ("SKU-1014", "Studio Condenser USB Mic", "Electronics", 14, 84.50, "AudioWave Labs", "2026-09-05"),
            ("SKU-1015", "1TB NVMe PCIe 4.0 SSD", "Hardware", 2, 94.99, "Apex Silicon", "2026-09-05")
        ]
        with open(self.data_filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "category", "quantity", "price", "supplier", "date_added"])
            for row in sample_rows:
                writer.writerow(row)


def main():
    """Main entry point for Crimson Inventory Pro application."""
    root = tk.Tk()
    app = CrimsonInventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
