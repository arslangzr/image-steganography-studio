"""Tkinter GUI for the image steganography application."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .exceptions import SteganographyError
from .models import EncodeRequest
from .services import SteganographyService, build_default_service


@dataclass(frozen=True)
class StatCard:
    """Describes a small summary card displayed in the interface."""

    title: str
    value_var: tk.StringVar


class ScrollableTab(ttk.Frame):
    """A notebook tab with vertical scrolling support."""

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0, background="#f4f7fb")
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.content = ttk.Frame(self, style="App.TFrame", padding=20)

        self.content_id = self._canvas.create_window((0, 0), window=self.content, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")

        self.content.bind("<Configure>", self._on_content_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")

    def _on_content_configure(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self.content_id, width=event.width)

    def _is_pointer_inside(self) -> bool:
        pointer_x, pointer_y = self.winfo_pointerxy()
        hovered_widget = self.winfo_containing(pointer_x, pointer_y)
        while hovered_widget is not None:
            if hovered_widget == self:
                return True
            hovered_widget = hovered_widget.master
        return False

    def _on_mousewheel(self, event: tk.Event) -> str | None:
        if not self._is_pointer_inside():
            return None

        delta = int(-1 * (event.delta / 120))
        if delta == 0:
            return None
        self._canvas.yview_scroll(delta, "units")
        return "break"

    def _on_mousewheel_linux(self, event: tk.Event) -> str | None:
        if not self._is_pointer_inside():
            return None

        delta = -1 if event.num == 4 else 1
        self._canvas.yview_scroll(delta, "units")
        return "break"


class SteganographyApp:
    """Desktop application for encoding and decoding hidden text in images."""

    def __init__(self, root: tk.Tk, service: SteganographyService) -> None:
        self.root = root
        self.service = service
        self.root.title("Image Steganography Studio")
        self.root.geometry("1120x760")
        self.root.minsize(920, 680)
        self.root.configure(background="#f4f7fb")

        self.status_var = tk.StringVar(value="Ready. Choose an action to begin.")
        self.capacity_var = tk.StringVar(value="Capacity: —")
        self.message_count_var = tk.StringVar(value="0 characters")
        self.output_hint_var = tk.StringVar(value="Suggested file name will appear here.")
        self.decode_status_var = tk.StringVar(value="Choose an image to reveal its hidden text.")
        self.encode_image_var = tk.StringVar()
        self.output_image_var = tk.StringVar()
        self.decode_image_var = tk.StringVar()
        self.notebook: ttk.Notebook | None = None

        self._configure_styles()
        self._build_layout()
        self._bind_events()
        self._maximize_window()

    def _maximize_window(self) -> None:
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                self.root.geometry(
                    f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
                )

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#f4f7fb")
        style.configure("Surface.TFrame", background="#ffffff")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("Hero.TFrame", background="#163b65")
        style.configure("Title.TLabel", background="#163b65", foreground="#ffffff", font=("Segoe UI", 22, "bold"))
        style.configure(
            "Subtitle.TLabel",
            background="#163b65",
            foreground="#d8e6f7",
            font=("Segoe UI", 10),
        )
        style.configure("HeroBadge.TLabel", background="#163b65", foreground="#8fd3ff", font=("Segoe UI", 9, "bold"))
        style.configure("Heading.TLabel", background="#ffffff", foreground="#163b65", font=("Segoe UI", 16, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#38506a", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#6a7f96", font=("Segoe UI", 9))
        style.configure("StatTitle.TLabel", background="#ffffff", foreground="#6a7f96", font=("Segoe UI", 9, "bold"))
        style.configure("StatValue.TLabel", background="#ffffff", foreground="#163b65", font=("Segoe UI", 14, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(18, 10))
        style.configure("Secondary.TButton", padding=(14, 9), font=("Segoe UI", 10))
        style.map("Primary.TButton", background=[("active", "#24527f")])
        style.configure("Section.TLabelframe", background="#ffffff", padding=18)
        style.configure("Section.TLabelframe.Label", background="#ffffff", foreground="#163b65", font=("Segoe UI", 11, "bold"))
        style.configure("TNotebook", background="#f4f7fb", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=(22, 12),
            font=("Segoe UI", 10, "bold"),
            background="#dfe7f2",
            foreground="#5a7189",
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#ffffff"), ("!selected", "#dfe7f2")],
            foreground=[("selected", "#163b65"), ("!selected", "#5a7189")],
            padding=[("selected", (30, 16)), ("!selected", (22, 12))],
        )

    def _bind_events(self) -> None:
        self.message_text.bind("<<Modified>>", self._on_message_modified)
        self.root.bind_all("<Control-o>", self._handle_open_shortcut, add="+")
        self.root.bind_all("<Control-O>", self._handle_open_shortcut, add="+")
        self.root.bind_all("<Control-Shift-S>", self._handle_save_shortcut, add="+")
        self.root.bind_all("<Control-Return>", self._handle_primary_action_shortcut, add="+")
        self.root.bind_all("<Escape>", self._handle_clear_shortcut, add="+")
        if self.notebook is not None:
            self.notebook.bind("<<NotebookTabChanged>>", self._handle_tab_changed)

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=20, style="App.TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container, style="Hero.TFrame", padding=24)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=3)
        header.columnconfigure(1, weight=2)

        ttk.Label(header, text="Image Steganography Studio", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Professionally package hidden messages inside images and recover them with a cleaner, guided workflow.",
            style="Subtitle.TLabel",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        ttk.Label(
            header,
            text="LOSSLESS OUTPUT • SMART PATH SUGGESTIONS • SCROLLABLE WORKSPACE",
            style="HeroBadge.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(14, 0))

        hero_side = ttk.Frame(header, style="Hero.TFrame")
        hero_side.grid(row=0, column=1, rowspan=3, sticky="e")
        hero_side.columnconfigure((0, 1), weight=1)
        for index, card in enumerate(
            [
                StatCard("Image capacity", self.capacity_var),
                StatCard("Message length", self.message_count_var),
            ]
        ):
            self._build_stat_card(hero_side, card, row=0, column=index)

        self.notebook = ttk.Notebook(container)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        encode_tab = ScrollableTab(self.notebook)
        decode_tab = ScrollableTab(self.notebook)
        self.notebook.add(encode_tab, text="Encode Message")
        self.notebook.add(decode_tab, text="Decode Message")

        self._build_encode_tab(encode_tab.content)
        self._build_decode_tab(decode_tab.content)

        footer = ttk.Label(
            container,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=(10, 8),
        )
        footer.grid(row=2, column=0, sticky="ew", pady=(14, 0))

    def _build_stat_card(self, parent: ttk.Frame, card: StatCard, row: int, column: int) -> None:
        frame = ttk.Frame(parent, style="Surface.TFrame", padding=(16, 14))
        frame.grid(row=row, column=column, sticky="nsew", padx=(10 if column else 0, 0))
        ttk.Label(frame, text=card.title, style="StatTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=card.value_var, style="StatValue.TLabel").grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )

    def _build_encode_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=3)
        parent.columnconfigure(1, weight=2)

        intro = ttk.Frame(parent, style="Surface.TFrame", padding=20)
        intro.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        intro.columnconfigure(0, weight=1)
        ttk.Label(intro, text="Encode a message into an image", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            intro,
            text="Select a source image, type your secret message, and save the encoded result. The suggested save path updates whenever you pick a different source file.",
            style="Body.TLabel",
            wraplength=980,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        frame = ttk.LabelFrame(parent, text="Encoding workspace", style="Section.TLabelframe")
        frame.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

        ttk.Label(frame, text="Source image", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.encode_image_entry = ttk.Entry(frame, textvariable=self.encode_image_var, font=("Segoe UI", 10))
        self.encode_image_entry.grid(
            row=0, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(
            frame,
            text="Browse",
            style="Secondary.TButton",
            command=self._browse_encode_image,
        ).grid(row=0, column=2, sticky="ew", pady=(0, 8))

        ttk.Label(frame, text="Estimated capacity", style="Body.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Label(frame, textvariable=self.capacity_var, style="Muted.TLabel").grid(
            row=1, column=1, columnspan=2, sticky="w", padx=(12, 0), pady=(0, 12)
        )

        ttk.Label(frame, text="Secret message", style="Body.TLabel").grid(row=2, column=0, sticky="nw")
        self.message_text = ScrolledText(
            frame,
            wrap="word",
            height=14,
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
        )
        self.message_text.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(12, 0), pady=(0, 8))
        ttk.Label(frame, textvariable=self.message_count_var, style="Muted.TLabel").grid(
            row=3, column=1, columnspan=2, sticky="w", padx=(12, 0), pady=(0, 12)
        )

        ttk.Label(frame, text="Output image", style="Body.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 8))
        self.output_image_entry = ttk.Entry(frame, textvariable=self.output_image_var, font=("Segoe UI", 10))
        self.output_image_entry.grid(
            row=4, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(
            frame,
            text="Save As",
            style="Secondary.TButton",
            command=self._browse_output_image,
        ).grid(row=4, column=2, sticky="ew", pady=(0, 8))
        ttk.Label(frame, textvariable=self.output_hint_var, style="Muted.TLabel").grid(
            row=5, column=1, columnspan=2, sticky="w", padx=(12, 0), pady=(0, 14)
        )

        actions = ttk.Frame(frame, style="Surface.TFrame")
        actions.grid(row=6, column=0, columnspan=3, sticky="e")
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self._clear_encode_form).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(
            actions,
            text="Encode and Save",
            style="Primary.TButton",
            command=self._handle_encode,
        ).grid(row=0, column=1)

        sidebar = ttk.Frame(parent, style="App.TFrame")
        sidebar.grid(row=1, column=1, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)

        tips_card = ttk.LabelFrame(sidebar, text="Best-practice guidance", style="Section.TLabelframe")
        tips_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        tips = (
            "• Prefer PNG, BMP, or TIFF for dependable decoding.\n\n"
            "• Larger images hold more text. Capacity is roughly one character per three pixels.\n\n"
            "• Keep the original source image untouched as a backup.\n\n"
            "• Saving without an extension will automatically produce a PNG file."
        )
        ttk.Label(tips_card, text=tips, style="Body.TLabel", wraplength=320, justify="left").grid(
            row=0, column=0, sticky="w"
        )

        workflow_card = ttk.LabelFrame(sidebar, text="Recommended workflow", style="Section.TLabelframe")
        workflow_card.grid(row=1, column=0, sticky="ew")
        workflow = (
            "1. Choose a source image.\n"
            "2. Review the suggested save path.\n"
            "3. Enter the hidden text.\n"
            "4. Save the encoded image.\n"
            "5. Decode later from the second tab."
        )
        ttk.Label(workflow_card, text=workflow, style="Body.TLabel", justify="left").grid(
            row=0, column=0, sticky="w"
        )

        shortcuts_card = ttk.LabelFrame(sidebar, text="Keyboard shortcuts", style="Section.TLabelframe")
        shortcuts_card.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        shortcuts = (
            "Ctrl+O  Open image for the active tab\n"
            "Ctrl+Shift+S  Choose output path\n"
            "Ctrl+Enter  Run the main action\n"
            "Esc  Clear the active tab"
        )
        ttk.Label(shortcuts_card, text=shortcuts, style="Body.TLabel", justify="left").grid(
            row=0, column=0, sticky="w"
        )

    def _build_decode_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        intro = ttk.Frame(parent, style="Surface.TFrame", padding=20)
        intro.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        intro.columnconfigure(0, weight=1)
        ttk.Label(intro, text="Decode a hidden message", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            intro,
            text="Load an encoded image to extract the hidden text. The decoded content appears below and can be copied with one click.",
            style="Body.TLabel",
            wraplength=980,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        frame = ttk.LabelFrame(parent, text="Decoding workspace", style="Section.TLabelframe")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Encoded image", style="Body.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.decode_image_entry = ttk.Entry(frame, textvariable=self.decode_image_var)
        self.decode_image_entry.grid(
            row=0, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(frame, text="Browse", style="Secondary.TButton", command=self._browse_decode_image).grid(
            row=0, column=2, sticky="ew", pady=(0, 8)
        )

        ttk.Label(frame, textvariable=self.decode_status_var, style="Muted.TLabel").grid(
            row=1, column=1, columnspan=2, sticky="w", padx=(12, 0), pady=(0, 12)
        )

        ttk.Label(frame, text="Decoded message", style="Body.TLabel").grid(row=2, column=0, sticky="nw")
        self.decoded_text = ScrolledText(
            frame,
            wrap="word",
            height=16,
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
        )
        self.decoded_text.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(12, 0), pady=(0, 14))
        self.decoded_text.configure(state="disabled")

        actions = ttk.Frame(frame, style="Surface.TFrame")
        actions.grid(row=3, column=0, columnspan=3, sticky="e")
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self._clear_decode_form).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(actions, text="Copy Message", style="Secondary.TButton", command=self._copy_decoded_message).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(
            actions,
            text="Decode",
            style="Primary.TButton",
            command=self._handle_decode,
        ).grid(row=0, column=2)

    def _browse_encode_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose source image",
            filetypes=[("Image files", "*.png *.bmp *.jpg *.jpeg *.tiff"), ("All files", "*.*")],
        )
        if file_path:
            self.encode_image_var.set(file_path)
            self._set_default_output_path(file_path)
            self._update_capacity(file_path)
            self.message_text.focus_set()
            self._set_status("Source image selected and save path refreshed.")

    def _browse_output_image(self) -> None:
        initial_name = self._suggest_output_name(self.encode_image_var.get())
        initial_dir = str(Path(self.encode_image_var.get()).parent) if self.encode_image_var.get() else None
        file_path = filedialog.asksaveasfilename(
            title="Save encoded image",
            defaultextension=".png",
            initialfile=initial_name,
            initialdir=initial_dir,
            filetypes=[("PNG image", "*.png"), ("BMP image", "*.bmp"), ("TIFF image", "*.tiff")],
        )
        if file_path:
            self.output_image_var.set(file_path)
            self.output_hint_var.set(f"Manual output selected: {file_path}")
            self._set_status("Output location selected.")

    def _browse_decode_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose image to decode",
            filetypes=[("Image files", "*.png *.bmp *.jpg *.jpeg *.tiff"), ("All files", "*.*")],
        )
        if file_path:
            self.decode_image_var.set(file_path)
            self.decode_status_var.set(f"Ready to decode: {file_path}")
            self.decoded_text.focus_set()
            self._set_status("Encoded image selected.")

    def _set_default_output_path(self, source_path: str) -> None:
        if not source_path:
            return
        source = Path(source_path)
        default_path = source.with_name(f"{source.stem}_encoded.png")
        self.output_image_var.set(str(default_path))
        self.output_hint_var.set(f"Suggested output: {default_path}")

    def _suggest_output_name(self, source_path: str) -> str:
        if not source_path:
            return "encoded_image.png"
        return f"{Path(source_path).stem}_encoded.png"

    def _update_capacity(self, image_path: str) -> None:
        try:
            capacity = self.service.get_capacity(image_path)
        except SteganographyError as error:
            self.capacity_var.set("Capacity: unavailable")
            self._show_error(str(error))
            return

        self.capacity_var.set(f"Capacity: {capacity} characters")

    def _handle_encode(self) -> None:
        request = EncodeRequest(
            source_image_path=self.encode_image_var.get().strip(),
            output_image_path=self.output_image_var.get().strip(),
            message=self.message_text.get("1.0", "end").rstrip("\n"),
        )

        try:
            result = self.service.encode_message(request)
        except SteganographyError as error:
            self._show_error(str(error))
            return
        except Exception as error:  # pragma: no cover - defensive UI handling
            self._show_error(f"Unexpected error: {error}")
            return

        self.output_image_var.set(result.output_image_path)
        self.output_hint_var.set(f"Saved output: {result.output_image_path}")
        success_message = "Message encoded successfully."
        if result.warning:
            success_message = f"{success_message}\n\nWarning: {result.warning}"
        messagebox.showinfo("Success", success_message)
        self._set_status(f"Saved encoded image to {result.output_image_path}.")

    def _handle_decode(self) -> None:
        try:
            decoded_message = self.service.decode_message(self.decode_image_var.get().strip())
        except SteganographyError as error:
            self._show_error(str(error))
            return
        except Exception as error:  # pragma: no cover - defensive UI handling
            self._show_error(f"Unexpected error: {error}")
            return

        self._set_decoded_text(decoded_message)
        self.decode_status_var.set("Decoded successfully. Review or copy the message below.")
        self._set_status("Message decoded successfully.")

    def _copy_decoded_message(self) -> None:
        message = self.decoded_text.get("1.0", "end").strip()
        if not message:
            messagebox.showwarning("Nothing to copy", "Decode a message first.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(message)
        self._set_status("Decoded message copied to clipboard.")

    def _clear_encode_form(self) -> None:
        self.encode_image_var.set("")
        self.output_image_var.set("")
        self.message_text.delete("1.0", "end")
        self.capacity_var.set("Capacity: —")
        self.message_count_var.set("0 characters")
        self.output_hint_var.set("Suggested file name will appear here.")
        self.encode_image_entry.focus_set()
        self._set_status("Encode form cleared.")

    def _clear_decode_form(self) -> None:
        self.decode_image_var.set("")
        self._set_decoded_text("")
        self.decode_status_var.set("Choose an image to reveal its hidden text.")
        self.decode_image_entry.focus_set()
        self._set_status("Decode form cleared.")

    def _set_decoded_text(self, content: str) -> None:
        self.decoded_text.configure(state="normal")
        self.decoded_text.delete("1.0", "end")
        if content:
            self.decoded_text.insert("1.0", content)
        self.decoded_text.configure(state="disabled")

    def _on_message_modified(self, _event: tk.Event) -> None:
        message = self.message_text.get("1.0", "end-1c")
        character_label = "character" if len(message) == 1 else "characters"
        self.message_count_var.set(f"{len(message)} {character_label}")
        self.message_text.edit_modified(False)

    def _active_tab_index(self) -> int:
        if self.notebook is None:
            return 0
        return self.notebook.index(self.notebook.select())

    def _handle_tab_changed(self, _event: tk.Event) -> None:
        if self._active_tab_index() == 0:
            self._set_status("Encode mode ready. Choose a source image or press Ctrl+O.")
        else:
            self._set_status("Decode mode ready. Choose an encoded image or press Ctrl+O.")

    def _handle_open_shortcut(self, _event: tk.Event) -> str:
        if self._active_tab_index() == 0:
            self._browse_encode_image()
        else:
            self._browse_decode_image()
        return "break"

    def _handle_save_shortcut(self, _event: tk.Event) -> str:
        if self._active_tab_index() == 0:
            self._browse_output_image()
        return "break"

    def _handle_primary_action_shortcut(self, _event: tk.Event) -> str:
        if self._active_tab_index() == 0:
            self._handle_encode()
        else:
            self._handle_decode()
        return "break"

    def _handle_clear_shortcut(self, _event: tk.Event) -> str:
        if self._active_tab_index() == 0:
            self._clear_encode_form()
        else:
            self._clear_decode_form()
        return "break"

    def _show_error(self, message: str) -> None:
        self._set_status(message)
        messagebox.showerror("Image Steganography Studio", message)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)


def launch_app() -> None:
    """Starts the Tkinter desktop application."""

    root = tk.Tk()
    app = SteganographyApp(root=root, service=build_default_service())
    root.mainloop()
    del app
