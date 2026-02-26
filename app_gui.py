import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageTk = None

try:
    import ttkbootstrap as tb
except Exception:  # pragma: no cover
    tb = None

from label_qr_pdf import LabelRow, default_output_pdf, generate_labels_pdf, generate_qr_list_pdf
from label_qr_pdf import read_labels_from_csv, read_labels_from_txt
from label_qr_pdf import _make_qr_image_with_logo


TRANSLATIONS = {
    "tr": {
        "app_title": "QR Kod Etiket",
        "subtitle": "TXT / CSV -> Etiket PDF",
        "about": "Hakkında",
        "dev_by": "Developed by İlyas YEŞİL",
        "tab_manual": "  Manuel Giriş  ",
        "tab_txt": "  TXT Dosyası Yükle  ",
        "tab_csv": "  CSV Dosyası Yükle  ",
        "manual_example": "Örnek: HALI:buhari-bhr-03-red",
        "txt_file_lbl": "TXT dosyası:",
        "csv_file_lbl": "CSV dosyası:",
        "pick": "Seç",
        "settings": "Ayarlar",
        "save_loc": "Kayıt Yeri (PDF):",
        "browse": "Gözat",
        "save": "Kaydet",
        "label_size": "Etiket Boyutu (mm):",
        "encoding": "Encoding:",
        "logo_lbl": "Logo (opsiyonel):",
        "clear": "Temizle",
        "logo_size_pct": "Logo Boyutu (%):",
        "logo_suggest": "(öneri: 18-26)",
        "list_layout": "Liste Dizilimi:",
        "cols": "Sütun",
        "rows": "Satır",
        "btn_generate_label": "QR KODLARI OLUŞTUR (PDF)",
        "btn_generate_list": "PDF Liste Olarak Kaydet",
        "status_records": "{} kayıt",
        "preview_title": "Önizleme (ilk 6 kayıt)",
        "about_text": (
            "Bu uygulama TXT/CSV girdisinden QR etiket PDF'i üretir.\n"
            "- Etiket PDF: her etiket 1 sayfa\n"
            "- Liste PDF: A4 üzerinde 5 sütun x 12 satır\n\n"
            "Telif Hakkı © 2026 İlyas YEŞİL. Tüm hakları saklıdır.\n"
            "Bu yazılım olduğu gibi sunulur; veri kaybı vb. durumlarda sorumluluk kabul edilmez."
        ),
        "close": "Kapat",
        "pillow_req": "Önizleme için Pillow gerekli",
        "refresh_preview": "Önizlemeyi Yenile",
        "error": "Hata",
        "success": "Başarılı",
        "label_size_numeric_error": "Etiket ölçüsü sayı olmalı.",
        "no_label_data_found": "Etiket verisi bulunamadı.",
        "list_layout_numeric_error": "Liste düzeni için sütun/satır sayıları pozitif tam sayı olmalı.",
        "pdf_create_success": "PDF başarıyla oluşturuldu: {out}",
        "list_pdf_create_success": "Liste PDF başarıyla oluşturuldu: {out}",
        "lang_btn": "[ EN ]",
    },
    "en": {
        "app_title": "QR Code Label",
        "subtitle": "TXT / CSV -> Label PDF",
        "about": "About",
        "dev_by": "Developed by İlyas YEŞİL",
        "tab_manual": "  Manual Entry  ",
        "tab_txt": "  Load TXT File  ",
        "tab_csv": "  Load CSV File  ",
        "manual_example": "Example: CARPET:buhari-bhr-03-red",
        "txt_file_lbl": "TXT file:",
        "csv_file_lbl": "CSV file:",
        "pick": "Pick",
        "settings": "Settings",
        "save_loc": "Save Location (PDF):",
        "browse": "Browse",
        "save": "Save",
        "label_size": "Label Size (mm):",
        "encoding": "Encoding:",
        "logo_lbl": "Logo (optional):",
        "clear": "Clear",
        "logo_size_pct": "Logo Size (%):",
        "logo_suggest": "(suggest: 18-26)",
        "list_layout": "List Layout:",
        "cols": "Cols",
        "rows": "Rows",
        "btn_generate_label": "GENERATE QR CODES (PDF)",
        "btn_generate_list": "Save as PDF List",
        "status_records": "{} records",
        "preview_title": "Preview (first 6 records)",
        "about_text": (
            "This application generates QR label PDFs from TXT/CSV input.\n"
            "- Label PDF: each label on 1 page\n"
            "- List PDF: 5 cols x 12 rows on A4\n\n"
            "Copyright © 2026 İlyas YEŞİL. All rights reserved.\n"
            "This software is provided as is; no responsibility is accepted for data loss etc."
        ),
        "close": "Close",
        "pillow_req": "Pillow required for preview",
        "refresh_preview": "Refresh Preview",
        "error": "Error",
        "success": "Success",
        "label_size_numeric_error": "Label dimensions must be numeric.",
        "no_label_data_found": "No label data found.",
        "list_layout_numeric_error": "Columns/rows must be positive integers for list layout.",
        "pdf_create_success": "PDF created successfully: {out}",
        "list_pdf_create_success": "List PDF created successfully: {out}",
        "lang_btn": "[ TR ]",
    }
}


_BaseWindow = tb.Window if tb is not None else tk.Tk


class App(_BaseWindow):
    def __init__(self) -> None:
        if tb is not None:
            super().__init__(themename="flatly")
        else:
            super().__init__()
        self.title("QR Kod Etiket")
        self.geometry("1360x800")
        self.minsize(1320, 770)

        self._apply_app_icon()

        self._use_bootstrap = tb is not None
        self._colors = {
            "header_bg": "#1f5fa8",
            "header_fg": "#ffffff",
            "sub_fg": "#d7e7ff",
        }

        self.txt_path = tk.StringVar(value="")
        self.csv_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="")
        self.width_mm = tk.StringVar(value="80")
        self.height_mm = tk.StringVar(value="50")
        self.encoding = tk.StringVar(value="utf-8")
        self.logo_path = tk.StringVar(value="")
        self.logo_scale = tk.StringVar(value="20")
        self.list_cols = tk.StringVar(value="5")
        self.list_rows = tk.StringVar(value="12")
        self.current_lang = "tr"

        self._labels: list[LabelRow] = []
        self._preview_imgs: list[ImageTk.PhotoImage] = []
        self._preview_h: int = 170

        root = ttk.Frame(self, padding=0)
        root.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(root, bg=self._colors["header_bg"], padx=14, pady=12)
        header.pack(fill=tk.X)
        title = tk.Label(
            header,
            text="QR Kod Etiket",
            bg=self._colors["header_bg"],
            fg=self._colors["header_fg"],
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(side=tk.LEFT)
        subtitle = tk.Label(
            header,
            text="TXT / CSV -> Etiket PDF",
            bg=self._colors["header_bg"],
            fg=self._colors["sub_fg"],
            font=("Segoe UI", 10),
        )
        subtitle.pack(side=tk.LEFT, padx=(14, 0), pady=(6, 0))

        right_header = tk.Frame(header, bg=self._colors["header_bg"])
        right_header.pack(side=tk.RIGHT)
        self.about_btn = tk.Label(
            right_header,
            text="Hakkında",
            bg=self._colors["header_bg"],
            fg=self._colors["sub_fg"],
            cursor="hand2",
            font=("Segoe UI", 10, "underline"),
        )
        self.about_btn.pack(side=tk.RIGHT, padx=(10, 0), pady=(6, 0))
        self.about_btn.bind("<Button-1>", lambda _e: self.show_about())

        dev = tk.Label(
            right_header,
            text="Developed by İlyas YEŞİL",
            bg=self._colors["header_bg"],
            fg=self._colors["sub_fg"],
            font=("Segoe UI", 8),
        )
        dev.pack(side=tk.RIGHT, pady=(6, 0))
        self.btn_lang = tk.Label(
            right_header,
            text="[ EN ]",
            bg=self._colors["header_bg"],
            fg="#ffff00",  # Sarı yaparak dikkat çekelim
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=10
        )
        self.btn_lang.pack(side=tk.RIGHT, padx=(10, 0), pady=(6, 0))
        self.btn_lang.bind("<Button-1>", lambda _e: self._toggle_lang())

        self.lbl_title_header = title
        self.lbl_subtitle_header = subtitle
        self.btn_about_header = self.about_btn
        self.lbl_dev_header = dev

        content = ttk.Frame(root, padding=12)
        content.pack(fill=tk.BOTH, expand=True)

        body = ttk.Frame(content)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=0)

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_input_tabs(left)
        self._build_settings(left)
        self._build_preview(right)

        self._refresh_labels()
        self._update_all_texts()

        try:
            self.after_idle(lambda: self._render_preview())
        except Exception:
            pass

    def _resource_path(self, relative_path: str) -> str:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def _apply_app_icon(self) -> None:
        try:
            icon_path = self._resource_path("QrCode.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def _update_all_texts(self) -> None:
        tr = TRANSLATIONS[self.current_lang]
        self.title(tr["app_title"])
        self.lbl_title_header.config(text=tr["app_title"])
        self.lbl_subtitle_header.config(text=tr["subtitle"])
        self.btn_about_header.config(text=tr["about"])
        self.lbl_dev_header.config(text=tr["dev_by"])
        
        self.tabs.tab(0, text=tr["tab_manual"])
        self.tabs.tab(1, text=tr["tab_txt"])
        self.tabs.tab(2, text=tr["tab_csv"])
        
        self.lbl_manual_hint.config(text=tr["manual_example"])
        self.lbl_txt_path.config(text=tr["txt_file_lbl"])
        self.btn_pick_txt.config(text=tr["pick"])
        self.lbl_csv_path.config(text=tr["csv_file_lbl"])
        self.btn_pick_csv.config(text=tr["pick"])
        
        self.box_settings.config(text=tr["settings"])
        self.lbl_save_loc.config(text=tr["save_loc"])
        self.btn_pick_output.config(text=tr["browse"] if self._use_bootstrap else tr["save"])
        self.lbl_label_size.config(text=tr["label_size"])
        self.lbl_encoding.config(text=tr["encoding"])
        self.lbl_logo_opt.config(text=tr["logo_lbl"])
        self.btn_pick_logo.config(text=tr["pick"])
        self.btn_clear_logo.config(text=tr["clear"])
        self.lbl_logo_size_pct.config(text=tr["logo_size_pct"])
        self.lbl_logo_suggest.config(text=tr["logo_suggest"])
        self.lbl_list_layout.config(text=tr["list_layout"])
        self.lbl_cols.config(text=tr["cols"])
        self.lbl_rows.config(text=tr["rows"])
        
        self.btn_generate.config(text=tr["btn_generate_label"])
        self.btn_generate_list_pdf.config(text=tr["btn_generate_list"])
        self.lbl_status.config(text=tr["status_records"].format(len(self._labels)))
        self.box_preview.config(text=tr["preview_title"])
        self.btn_lang.config(text=tr["lang_btn"])

    def _toggle_lang(self) -> None:
        self.current_lang = "en" if self.current_lang == "tr" else "tr"
        self._update_all_texts()
        self._render_preview()

    def _center_window(self, child: tk.Toplevel) -> None:
        try:
            child.update_idletasks()
            self.update_idletasks()

            w = child.winfo_width() or child.winfo_reqwidth()
            h = child.winfo_height() or child.winfo_reqheight()

            parent_x = self.winfo_rootx()
            parent_y = self.winfo_rooty()
            parent_w = self.winfo_width()
            parent_h = self.winfo_height()

            x = parent_x + max(0, (parent_w - w) // 2)
            y = parent_y + max(0, (parent_h - h) // 2)
            child.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def show_about(self) -> None:
        tr = TRANSLATIONS[self.current_lang]
        w = tk.Toplevel(self)
        w.title(tr["about"])
        w.resizable(False, False)
        try:
            w.withdraw()
        except Exception:
            pass
        try:
            icon_path = self._resource_path("QrCode.ico")
            if os.path.exists(icon_path):
                w.iconbitmap(icon_path)
        except Exception:
            pass
        try:
            w.transient(self)
            w.grab_set()
        except Exception:
            pass

        frm = ttk.Frame(w, padding=14)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text=tr["app_title"], font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(frm, text=tr["dev_by"], foreground="#555").pack(anchor="w", pady=(4, 0))
        ttk.Separator(frm).pack(fill=tk.X, pady=10)

        msg = ttk.Label(frm, text=tr["about_text"], justify="left", wraplength=460)
        msg.pack(anchor="w")

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btns, text=tr["close"], command=w.destroy).pack(side=tk.RIGHT)

        def _finalize_position() -> None:
            try:
                # Pencere boyutu
                win_w, win_h = 520, 320
                w.geometry(f"{win_w}x{win_h}")
                w.minsize(win_w, win_h)
                
                # Butonun ekran koordinatlarını al
                bx = self.about_btn.winfo_rootx()
                by = self.about_btn.winfo_rooty()
                bw = self.about_btn.winfo_width()
                bh = self.about_btn.winfo_height()
                
                # Pencerenin sağ üst köşesi butonun altına gelsin
                # window_x + window_w = bx + bw  =>  window_x = (bx + bw) - window_w
                # window_y = by + bh
                x = (bx + bw) - win_w
                y = by + bh + 5  # 5px boşluk
                
                # Ekran sınırlarını kontrol et (taşma olmasın)
                screen_w = self.winfo_screenwidth()
                if x + win_w > screen_w: x = screen_w - win_w
                if x < 0: x = 0
                
                w.geometry(f"{win_w}x{win_h}+{x}+{y}")
            except Exception:
                self._center_window(w)
            try:
                w.deiconify()
                w.lift()
                w.focus_force()
            except Exception:
                pass

        try:
            w.after_idle(_finalize_position)
        except Exception:
            _finalize_position()

    def _build_input_tabs(self, parent: ttk.Frame) -> None:
        if self._use_bootstrap:
            tabs = tb.Notebook(parent, bootstyle="primary")
        else:
            tabs = ttk.Notebook(parent)
        tabs.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self.tabs = tabs

        tab_manual = ttk.Frame(tabs, padding=12)
        tab_txt = ttk.Frame(tabs, padding=12)
        tab_csv = ttk.Frame(tabs, padding=12)
        tabs.add(tab_manual, text="  Manuel Giriş  ")
        tabs.add(tab_txt, text="  TXT Dosyası Yükle  ")
        tabs.add(tab_csv, text="  CSV Dosyası Yükle  ")

        self.manual_text = tk.Text(tab_manual, height=8, wrap="word", font=("Segoe UI", 10))
        self.manual_text.pack(fill=tk.BOTH, expand=True)
        self.lbl_manual_hint = ttk.Label(tab_manual, text="Örnek: HALI:buhari-bhr-03-red", foreground="#666")
        self.lbl_manual_hint.pack(anchor="w", pady=(6, 0))

        row = ttk.Frame(tab_txt)
        row.pack(fill=tk.X)
        self.lbl_txt_path = ttk.Label(row, text="TXT dosyası:")
        self.lbl_txt_path.pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.txt_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        if self._use_bootstrap:
            self.btn_pick_txt = tb.Button(row, text="Seç", command=self._pick_txt, bootstyle="secondary")
        else:
            self.btn_pick_txt = ttk.Button(row, text="Seç", command=self._pick_txt)
        self.btn_pick_txt.pack(side=tk.LEFT)

        row2 = ttk.Frame(tab_csv)
        row2.pack(fill=tk.X)
        self.lbl_csv_path = ttk.Label(row2, text="CSV dosyası:")
        self.lbl_csv_path.pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.csv_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        if self._use_bootstrap:
            self.btn_pick_csv = tb.Button(row2, text="Seç", command=self._pick_csv, bootstyle="secondary")
        else:
            self.btn_pick_csv = ttk.Button(row2, text="Seç", command=self._pick_csv)
        self.btn_pick_csv.pack(side=tk.LEFT)

        tabs.bind("<<NotebookTabChanged>>", lambda _e: self._refresh_labels())
        self.manual_text.bind("<KeyRelease>", lambda _e: self._refresh_labels())

    def _build_settings(self, parent: ttk.Frame) -> None:
        box = ttk.LabelFrame(parent, text="Ayarlar", padding=10)
        box.grid(row=1, column=0, sticky="ew")
        box.columnconfigure(1, weight=1)

        lbl_save_loc = ttk.Label(box, text="Kayıt Yeri (PDF):")
        lbl_save_loc.grid(row=0, column=0, sticky="w")
        ttk.Entry(box, textvariable=self.output_path).grid(row=0, column=1, sticky="we", padx=(8, 0))
        if self._use_bootstrap:
            btn_pick_output = tb.Button(box, text="Gözat", command=self._pick_output, bootstyle="secondary")
        else:
            btn_pick_output = ttk.Button(box, text="Kaydet", command=self._pick_output)
        btn_pick_output.grid(row=0, column=2, padx=(8, 0))

        size = ttk.Frame(box)
        size.grid(row=1, column=0, columnspan=3, sticky="we", pady=(10, 0))
        lbl_label_size = ttk.Label(size, text="Etiket Boyutu (mm):")
        lbl_label_size.pack(side=tk.LEFT)
        ttk.Entry(size, textvariable=self.width_mm, width=6).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(size, text="x").pack(side=tk.LEFT, padx=6)
        ttk.Entry(size, textvariable=self.height_mm, width=6).pack(side=tk.LEFT)

        enc = ttk.Frame(box)
        enc.grid(row=2, column=0, columnspan=3, sticky="we", pady=(10, 0))
        lbl_encoding = ttk.Label(enc, text="Encoding:")
        lbl_encoding.pack(side=tk.LEFT)
        ttk.Entry(enc, textvariable=self.encoding, width=12).pack(side=tk.LEFT, padx=(8, 0))

        logo = ttk.Frame(box)
        logo.grid(row=3, column=0, columnspan=3, sticky="we", pady=(10, 0))
        logo.columnconfigure(1, weight=1)
        lbl_logo_opt = ttk.Label(logo, text="Logo (opsiyonel):")
        lbl_logo_opt.grid(row=0, column=0, sticky="w")
        ttk.Entry(logo, textvariable=self.logo_path).grid(row=0, column=1, sticky="we", padx=(8, 0))
        if self._use_bootstrap:
            btn_pick_logo = tb.Button(logo, text="Seç", command=self._pick_logo, bootstyle="secondary")
            btn_clear_logo = tb.Button(logo, text="Temizle", command=self._clear_logo, bootstyle="secondary")
        else:
            btn_pick_logo = ttk.Button(logo, text="Seç", command=self._pick_logo)
            btn_clear_logo = ttk.Button(logo, text="Temizle", command=self._clear_logo)
        btn_pick_logo.grid(row=0, column=2, padx=(8, 0))
        btn_clear_logo.grid(row=0, column=3, padx=(8, 0))

        logo2 = ttk.Frame(box)
        logo2.grid(row=4, column=0, columnspan=3, sticky="we", pady=(8, 0))
        lbl_logo_size_pct = ttk.Label(logo2, text="Logo Boyutu (%):")
        lbl_logo_size_pct.pack(side=tk.LEFT)
        ttk.Entry(logo2, textvariable=self.logo_scale, width=6).pack(side=tk.LEFT, padx=(8, 0))
        lbl_logo_suggest = ttk.Label(logo2, text="(öneri: 18-26)", foreground="#666")
        lbl_logo_suggest.pack(side=tk.LEFT, padx=(10, 0))

        grid_cfg = ttk.Frame(box)
        grid_cfg.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 0))
        lbl_list_layout = ttk.Label(grid_cfg, text="Liste Dizilimi:")
        lbl_list_layout.pack(side=tk.LEFT)
        lbl_cols = ttk.Label(grid_cfg, text="Sütun")
        lbl_cols.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(grid_cfg, textvariable=self.list_cols, width=5).pack(side=tk.LEFT, padx=(6, 0))
        lbl_rows = ttk.Label(grid_cfg, text="Satır")
        lbl_rows.pack(side=tk.LEFT, padx=(12, 0))
        ttk.Entry(grid_cfg, textvariable=self.list_rows, width=5).pack(side=tk.LEFT, padx=(6, 0))

        actions = ttk.Frame(box)
        actions.grid(row=6, column=0, columnspan=3, sticky="we", pady=(14, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        if self._use_bootstrap:
            self.btn_generate = tb.Button(actions, text="QR KODLARI OLUŞTUR (PDF)", command=self.generate, bootstyle="success")
            self.btn_generate.grid(row=0, column=0, sticky="we", padx=(0, 8), ipady=8)
            self.btn_generate_list_pdf = tb.Button(actions, text="PDF Liste Olarak Kaydet", command=self.generate_list_pdf, bootstyle="primary")
            self.btn_generate_list_pdf.grid(row=0, column=1, sticky="we", ipady=8)
        else:
            self.btn_generate = ttk.Button(actions, text="PDF OLUŞTUR", command=self.generate)
            self.btn_generate.grid(row=0, column=0, sticky="we", padx=(0, 8), ipady=8)
            self.btn_generate_list_pdf = ttk.Button(actions, text="PDF Liste Olarak Kaydet", command=self.generate_list_pdf)
            self.btn_generate_list_pdf.grid(row=0, column=1, sticky="we", ipady=8)

        self.lbl_status = ttk.Label(box, text="0 kayıt", foreground="#666")
        self.lbl_status.grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.box_settings = box
        self.lbl_save_loc = lbl_save_loc
        self.btn_pick_output = btn_pick_output
        self.lbl_label_size = lbl_label_size
        self.lbl_encoding = lbl_encoding
        self.lbl_logo_opt = lbl_logo_opt
        self.btn_pick_logo = btn_pick_logo
        self.btn_clear_logo = btn_clear_logo
        self.lbl_logo_size_pct = lbl_logo_size_pct
        self.lbl_logo_suggest = lbl_logo_suggest
        self.lbl_list_layout = lbl_list_layout
        self.lbl_cols = lbl_cols
        self.lbl_rows = lbl_rows

    def _pick_logo(self) -> None:
        p = filedialog.askopenfilename(filetypes=[("Image", "*.png *.jpg *.jpeg"), ("All", "*.*")])
        if not p:
            return
        self.logo_path.set(p)
        self._render_preview()

    def _clear_logo(self) -> None:
        self.logo_path.set("")
        self._render_preview()

    def _build_preview(self, parent: ttk.Frame) -> None:
        box = ttk.LabelFrame(parent, text="Önizleme (ilk 6 kayıt)", padding=10)
        box.grid(row=0, column=0, sticky="nsew")
        self.box_preview = box
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)

        self.preview = ttk.Frame(box)
        self.preview.grid(row=0, column=0, sticky="nsew")
        self.preview.columnconfigure(0, weight=1)
        self.preview.columnconfigure(1, weight=1)
        self.preview.rowconfigure(0, weight=1)
        self.preview.rowconfigure(1, weight=1)
        self.preview.rowconfigure(2, weight=1)

        self.preview_cards: list[ttk.Label] = []
        for idx in range(6):
            r = idx // 2
            c = idx % 2
            card = ttk.Label(self.preview, text="", anchor="center", relief="groove")
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=6, ipadx=6, ipady=6)
            self.preview_cards.append(card)

        def _on_preview_resize(e):
            try:
                w = max(10, int(e.width))
                h = max(10, int(e.height))
                cell_w = (w - 3 * 12) // 2
                cell_h = (h - 4 * 12) // 3
                ratio = 80 / 50
                max_w = max(10, cell_w - 34)
                max_h = max(10, cell_h - 34)
                target_h = int(min(max_h, max_w / ratio))
                target_h = max(90, target_h)
                if abs(target_h - self._preview_h) >= 8:
                    self._preview_h = target_h
                    self._render_preview()
            except Exception:
                pass

        self.preview.bind("<Configure>", _on_preview_resize)

    def _pick_txt(self) -> None:
        p = filedialog.askopenfilename(filetypes=[("TXT", "*.txt"), ("All", "*.*")])
        if not p:
            return
        self.txt_path.set(p)
        if not self.output_path.get().strip():
            self.output_path.set(default_output_pdf(p))
        self._refresh_labels()

    def _pick_csv(self) -> None:
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if not p:
            return
        self.csv_path.set(p)
        if not self.output_path.get().strip():
            self.output_path.set(default_output_pdf(p))
        self._refresh_labels()

    def _pick_output(self) -> None:
        p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not p:
            return
        self.output_path.set(p)

    def _current_input_mode(self) -> str:
        tab = self.tabs.index(self.tabs.select())
        if tab == 0:
            return "manual"
        if tab == 1:
            return "txt"
        return "csv"

    def _refresh_labels(self) -> None:
        try:
            mode = self._current_input_mode()
            enc = self.encoding.get().strip() or "utf-8"
            if mode == "manual":
                raw = self.manual_text.get("1.0", "end").splitlines()
                lines = [ln.strip() for ln in raw if ln.strip()]
                tmp_path = None
                self._labels = []
                for ln in lines:
                    if ":" not in ln:
                        continue
                    cins, rest = ln.split(":", 1)
                    cins = cins.strip()
                    rest = rest.strip()
                    carpet_name = rest.replace("-", " ")
                    self._labels.append(LabelRow(cins=cins, carpet_name=carpet_name, qr_text=ln))
            elif mode == "txt":
                p = self.txt_path.get().strip()
                self._labels = read_labels_from_txt(p, encoding=enc) if p and os.path.exists(p) else []
            else:
                p = self.csv_path.get().strip()
                self._labels = read_labels_from_csv(p, encoding=enc) if p and os.path.exists(p) else []

            self.lbl_status.config(text=TRANSLATIONS[self.current_lang]["status_records"].format(len(self._labels)))
            self._render_preview()
        except Exception as e:
            self._labels = []
            self.lbl_status.config(text="0 kayıt")
            self._render_preview(clear=True)

    def _render_preview(self, clear: bool = False) -> None:
        if ImageTk is None:
            for card in self.preview_cards:
                card.config(text=TRANSLATIONS[self.current_lang]["pillow_req"], image="")
            return
        self._preview_imgs = []
        if clear or not self._labels:
            for card in self.preview_cards:
                card.config(text="", image="")
            return

        def _truncate_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> str:
            t = (text or "").strip()
            if not t:
                return ""
            if draw.textlength(t, font=font) <= max_w:
                return t
            while t and draw.textlength(t + "…", font=font) > max_w:
                t = t[:-1]
            return (t + "…") if t else ""

        def _wrap_ellipsis(
            draw: ImageDraw.ImageDraw,
            text: str,
            font: ImageFont.ImageFont,
            x: int,
            y0: int,
            max_w: int,
            line_gap: int,
            max_lines: int,
        ) -> int:
            s = (text or "").strip()
            if not s or max_lines <= 0:
                return y0
            words = s.split()
            if not words:
                return y0

            lines_out: list[str] = []
            current = ""

            def _push_line(line: str) -> None:
                if line.strip():
                    lines_out.append(line.strip())

            for w in words:
                cand = (current + " " + w).strip()
                if not current:
                    current = w
                    continue
                if draw.textlength(cand, font=font) <= max_w:
                    current = cand
                else:
                    _push_line(current)
                    current = w
                    if len(lines_out) >= max_lines:
                        current = ""
                        break

            if current and len(lines_out) < max_lines:
                _push_line(current)

            overflow = False
            if len(lines_out) > max_lines:
                lines_out = lines_out[:max_lines]
                overflow = True
            elif len(lines_out) == max_lines:
                # If there are still words left unrendered, mark overflow.
                rendered = " ".join(lines_out).split()
                overflow = len(rendered) < len(words)

            if overflow and lines_out:
                lines_out[-1] = _truncate_to_width(draw, lines_out[-1], font, max_w)

            y = y0
            for i, line in enumerate(lines_out[:max_lines]):
                if i == max_lines - 1 and overflow:
                    line = _truncate_to_width(draw, line, font, max_w)
                draw.text((x, y), line, fill=(0, 0, 0), font=font)
                y += line_gap
            return y

        def _make_label_preview(row: LabelRow, target_w: int, target_h: int, current_idx: int, total_count: int) -> Image.Image:
            label_w_mm = 80.0
            label_h_mm = 50.0
            qr_mm = 32.0
            margin_mm = 5.0
            qr_y_offset_mm = 6.0

            w_px = max(220, int(target_w))
            h_px = max(140, int(target_h))
            img = Image.new("RGB", (w_px, h_px), (255, 255, 255))
            dr = ImageDraw.Draw(img)

            px_per_mm = w_px / label_w_mm
            margin = int(margin_mm * px_per_mm)
            qr_side = int(qr_mm * px_per_mm)
            qr_side = max(int(18 * px_per_mm), min(qr_side, h_px - margin * 2))

            qr_x = w_px - margin - qr_side
            qr_y = int((margin_mm + qr_y_offset_mm) * px_per_mm)

            logo = self.logo_path.get().strip() or None
            try:
                scale = float((self.logo_scale.get().strip() or "22")) / 100.0
            except ValueError:
                scale = 0.20

            qr_img = _make_qr_image_with_logo(
                qr_text=row.qr_text,
                box_size=6,
                border=1,
                logo_path=logo,
                logo_scale=scale,
            ).resize((qr_side, qr_side))
            img.paste(qr_img, (qr_x, qr_y))

            text_x = margin
            text_max_w = max(10, (qr_x - margin) - text_x)

            try:
                f1 = ImageFont.truetype("arial.ttf", size=max(14, int(h_px * 0.12)))
                f2 = ImageFont.truetype("arial.ttf", size=max(12, int(h_px * 0.10)))
                f3 = ImageFont.truetype("arial.ttf", size=max(10, int(h_px * 0.085)))
            except Exception:
                f1 = ImageFont.load_default()
                f2 = ImageFont.load_default()
                f3 = ImageFont.load_default()

            text_y_top_mm = label_h_mm - margin_mm - 2.8
            y_top_px = int((label_h_mm - text_y_top_mm) * px_per_mm)
            dr.text((text_x, y_top_px), (row.cins or "").strip(), fill=(0, 0, 0), font=f1)

            name_y_mm = text_y_top_mm - 5.6
            name_y_px = int((label_h_mm - name_y_mm) * px_per_mm)
            _wrap_ellipsis(dr, (row.carpet_name or "").strip().upper(), f2, text_x, name_y_px, text_max_w, int(4.4 * px_per_mm), 4)


            bottom_y_mm = margin_mm + 3.5
            bottom_y_px = int((label_h_mm - bottom_y_mm) * px_per_mm)
            # _wrap_ellipsis(dr, (row.qr_text or "").strip(), f3, text_x, bottom_y_px, text_max_w, int(3.2 * px_per_mm), 1)

            # Numaralandırma
            num_txt = f"{current_idx} / {total_count}"
            dr.text((margin, h_px - margin - int(2.5 * px_per_mm)), num_txt, fill=(0, 0, 0), font=f3)


            dr.rectangle([0, 0, w_px - 1, h_px - 1], outline=(140, 140, 140), width=1)
            return img

        ratio = 80 / 50
        sample = self._labels[:6]
        for i in range(6):
            card = self.preview_cards[i]
            if i >= len(sample):
                card.config(text="", image="")
                continue

            row = sample[i]
            h = max(120, int(self._preview_h))
            w = max(190, int(h * ratio))
            label_img = _make_label_preview(row, w, h, i + 1, len(self._labels))
            photo = ImageTk.PhotoImage(label_img)
            self._preview_imgs.append(photo)
            card.config(image=photo, text="")
            card.configure(compound="center")

    def generate(self) -> None:
        out = self.output_path.get().strip()
        if not out:
            mode = self._current_input_mode()
            if mode == "txt" and self.txt_path.get().strip():
                out = default_output_pdf(self.txt_path.get().strip())
            elif mode == "csv" and self.csv_path.get().strip():
                out = default_output_pdf(self.csv_path.get().strip())
            else:
                out = "etiketler.pdf"
            self.output_path.set(out)

        try:
            w = float(self.width_mm.get().strip())
            h = float(self.height_mm.get().strip())
        except ValueError:
            messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], TRANSLATIONS[self.current_lang]["label_size_numeric_error"])
            return

        logo = self.logo_path.get().strip() or None
        try:
            logo_scale = float((self.logo_scale.get().strip() or "22")) / 100.0
        except ValueError:
            logo_scale = 0.20

        try:
            self._refresh_labels()
            labels = self._labels
            if not labels:
                messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], TRANSLATIONS[self.current_lang]["no_label_data_found"])
                return
            generate_labels_pdf(labels, out, width_mm=w, height_mm=h, logo_path=logo, logo_scale=logo_scale)
            messagebox.showinfo(TRANSLATIONS[self.current_lang]["success"], TRANSLATIONS[self.current_lang]["pdf_create_success"].format(out=out))
        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], str(e))
            return

    def generate_list_pdf(self) -> None:
        out = self.output_path.get().strip()
        if not out:
            mode = self._current_input_mode()
            src = ""
            if mode == "txt":
                src = self.txt_path.get().strip()
            elif mode == "csv":
                src = self.csv_path.get().strip()
            if src:
                out = default_output_pdf(src)
            else:
                out = "etiketler.pdf"
            self.output_path.set(out)

        base, ext = os.path.splitext(out)
        if ext.lower() != ".pdf":
            out = out + ".pdf"

        list_out = base + "_liste.pdf"

        logo = self.logo_path.get().strip() or None
        try:
            logo_scale = float((self.logo_scale.get().strip() or "22")) / 100.0
        except ValueError:
            logo_scale = 0.20

        try:
            cols = int(self.list_cols.get().strip() or "5")
            rows = int(self.list_rows.get().strip() or "12")
            if cols <= 0 or rows <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], TRANSLATIONS[self.current_lang]["list_layout_numeric_error"])
            return

        try:
            self._refresh_labels()
            labels = self._labels
            if not labels:
                messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], TRANSLATIONS[self.current_lang]["no_label_data_found"])
                return
            generate_qr_list_pdf(labels, list_out, cols=cols, rows=rows, logo_path=logo, logo_scale=logo_scale)
            messagebox.showinfo(TRANSLATIONS[self.current_lang]["success"], TRANSLATIONS[self.current_lang]["list_pdf_create_success"].format(out=list_out))
        except Exception as e:
            messagebox.showerror(TRANSLATIONS[self.current_lang]["error"], str(e))
            return


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
