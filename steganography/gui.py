"""Tkinter GUI for the image steganography application."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .exceptions import SteganographyError
from .models import EncodeRequest
from .services import SteganographyService, build_default_service


class SteganographyApp:
    """Desktop application for encoding and decoding hidden text in images."""

    def __init__(self, root: tk.Tk, service: SteganographyService) -> None:
        self.root = root
        self.service = service
        self.root.title("Image Steganography Studio")
        self.root.geometry("920x660")
        self.root.minsize(860, 620)

        self.status_var = tk.StringVar(value="Ready. Choose an action to begin.")
        self.capacity_var = tk.StringVar(value="Capacity: —")
        self.encode_image_var = tk.StringVar()
        self.output_image_var = tk.StringVar()
        self.decode_image_var = tk.StringVar()

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Primary.TButton", padding=(14, 8))
        style.configure("Section.TLabelframe", padding=16)
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Image Steganography Studio", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Hide messages inside images and recover them later with a simple desktop interface.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky="nsew")

        encode_tab = ttk.Frame(notebook, padding=16)
        decode_tab = ttk.Frame(notebook, padding=16)
        notebook.add(encode_tab, text="Encode Message")
        notebook.add(decode_tab, text="Decode Message")

        self._build_encode_tab(encode_tab)
        self._build_decode_tab(decode_tab)

        footer = ttk.Label(
            container,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=(10, 8),
        )
        footer.grid(row=2, column=0, sticky="ew", pady=(14, 0))

    def _build_encode_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(parent, text="Create an encoded image", style="Section.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Source image").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.encode_image_var).grid(
            row=0, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(frame, text="Browse", command=self._browse_encode_image).grid(
            row=0, column=2, sticky="ew", pady=(0, 8)
        )

        ttk.Label(frame, textvariable=self.capacity_var).grid(
            row=1, column=1, sticky="w", padx=(12, 8), pady=(0, 14)
        )

        ttk.Label(frame, text="Secret message").grid(row=2, column=0, sticky="nw")
        self.message_text = ScrolledText(frame, wrap="word", height=12, font=("Segoe UI", 10))
        self.message_text.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(12, 0), pady=(0, 14))
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Output image").grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.output_image_var).grid(
            row=3, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(frame, text="Save As", command=self._browse_output_image).grid(
            row=3, column=2, sticky="ew", pady=(0, 8)
        )

        tips = (
            "Tips:\n"
            "• Prefer PNG or BMP for lossless steganography.\n"
            "• Bigger images can hold longer messages.\n"
            "• Keep an original copy of the source image."
        )
        ttk.Label(frame, text=tips, justify="left").grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(8, 16)
        )

        actions = ttk.Frame(frame)
        actions.grid(row=5, column=0, columnspan=3, sticky="e")
        ttk.Button(actions, text="Clear", command=self._clear_encode_form).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(
            actions,
            text="Encode and Save",
            style="Primary.TButton",
            command=self._handle_encode,
        ).grid(row=0, column=1)

    def _build_decode_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(parent, text="Read a hidden message", style="Section.TLabelframe")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Encoded image").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.decode_image_var).grid(
            row=0, column=1, sticky="ew", padx=(12, 8), pady=(0, 8)
        )
        ttk.Button(frame, text="Browse", command=self._browse_decode_image).grid(
            row=0, column=2, sticky="ew", pady=(0, 8)
        )

        ttk.Label(frame, text="Decoded message").grid(row=1, column=0, sticky="nw")
        self.decoded_text = ScrolledText(frame, wrap="word", height=14, font=("Segoe UI", 10))
        self.decoded_text.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(12, 0), pady=(0, 14))

        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=3, sticky="e")
        ttk.Button(actions, text="Clear", command=self._clear_decode_form).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text="Copy Message", command=self._copy_decoded_message).grid(
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
            self._set_status("Source image selected.")

    def _browse_output_image(self) -> None:
        initial_name = self._suggest_output_name(self.encode_image_var.get())
        file_path = filedialog.asksaveasfilename(
            title="Save encoded image",
            defaultextension=".png",
            initialfile=initial_name,
            filetypes=[("PNG image", "*.png"), ("BMP image", "*.bmp"), ("TIFF image", "*.tiff")],
        )
        if file_path:
            self.output_image_var.set(file_path)
            self._set_status("Output location selected.")

    def _browse_decode_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose image to decode",
            filetypes=[("Image files", "*.png *.bmp *.jpg *.jpeg *.tiff"), ("All files", "*.*")],
        )
        if file_path:
            self.decode_image_var.set(file_path)
            self._set_status("Encoded image selected.")

    def _set_default_output_path(self, source_path: str) -> None:
        if not source_path:
            return
        source = Path(source_path)
        default_path = source.with_name(f"{source.stem}_encoded.png")
        if not self.output_image_var.get():
            self.output_image_var.set(str(default_path))

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
            warning = self.service.encode_message(request)
        except SteganographyError as error:
            self._show_error(str(error))
            return
        except Exception as error:  # pragma: no cover - defensive UI handling
            self._show_error(f"Unexpected error: {error}")
            return

        success_message = "Message encoded successfully."
        if warning:
            success_message = f"{success_message}\n\nWarning: {warning}"
        messagebox.showinfo("Success", success_message)
        self._set_status(f"Saved encoded image to {request.output_image_path}.")

    def _handle_decode(self) -> None:
        try:
            decoded_message = self.service.decode_message(self.decode_image_var.get().strip())
        except SteganographyError as error:
            self._show_error(str(error))
            return
        except Exception as error:  # pragma: no cover - defensive UI handling
            self._show_error(f"Unexpected error: {error}")
            return

        self.decoded_text.delete("1.0", "end")
        self.decoded_text.insert("1.0", decoded_message)
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
        self._set_status("Encode form cleared.")

    def _clear_decode_form(self) -> None:
        self.decode_image_var.set("")
        self.decoded_text.delete("1.0", "end")
        self._set_status("Decode form cleared.")

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
