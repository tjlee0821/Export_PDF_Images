import os
import fitz  # PyMuPDF
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD


DPI = 300


def pdf_to_png(pdf_path):
    folder = os.path.dirname(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    doc = fitz.open(pdf_path)

    zoom = DPI / 72
    matrix = fitz.Matrix(zoom, zoom)

    for page_index in range(len(doc)):
        page = doc[page_index]

        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        output_path = os.path.join(
            folder,
            f"{base_name}_{page_index + 1}.png"
        )

        pix.save(output_path)

    doc.close()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to PNG Export")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        self.label = tk.Label(
            root,
            text="PDF 파일을 여기에 드래그하세요\n\n300 DPI PNG로 변환됩니다",
            font=("Arial", 14),
            justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=20, pady=20)

        self.status = tk.Label(
            root,
            text="대기 중",
            font=("Arial", 11),
            fg="gray"
        )
        self.status.pack(pady=15)

        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)

        success_count = 0
        error_count = 0

        for file_path in files:
            file_path = file_path.strip()

            if not file_path.lower().endswith(".pdf"):
                error_count += 1
                continue

            try:
                self.status.config(text=f"변환 중: {os.path.basename(file_path)}")
                self.root.update_idletasks()

                pdf_to_png(file_path)
                success_count += 1

            except Exception as e:
                error_count += 1
                print(f"[ERROR] {file_path}: {e}")

        self.status.config(
            text=f"완료: {success_count}개 PDF 변환 / 오류: {error_count}개"
        )

        messagebox.showinfo(
            "완료",
            f"PDF 변환 완료\n\n성공: {success_count}개\n오류: {error_count}개"
        )


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = App(root)
    root.mainloop()