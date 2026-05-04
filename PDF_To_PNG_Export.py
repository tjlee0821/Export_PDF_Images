import os
import fitz  # PyMuPDF
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter.simpledialog import askstring
from tkinterdnd2 import DND_FILES, TkinterDnD


DPI = 300


def open_pdf_with_password(pdf_path, root):
    doc = fitz.open(pdf_path)

    if doc.needs_pass:
        for _ in range(3):  # 3번까지 시도
            password = askstring(
                "비밀번호 입력",
                f"{os.path.basename(pdf_path)}\n비밀번호를 입력하세요:",
                show="*",
                parent=root
            )

            if password is None:
                doc.close()
                return None

            if doc.authenticate(password):
                return doc

            messagebox.showerror("오류", "비밀번호가 틀렸습니다.")

        doc.close()
        return None

    return doc


def pdf_to_png(pdf_path, root):
    folder = os.path.dirname(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    doc = open_pdf_with_password(pdf_path, root)
    if doc is None:
        return False

    zoom = DPI / 72
    matrix = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        output_path = os.path.join(
            folder,
            f"{base_name}_{i + 1}.png"
        )
        pix.save(output_path)

    doc.close()
    return True


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF → PNG Export (암호 지원)")
        self.root.geometry("420x300")

        self.label = tk.Label(
            root,
            text="PDF 드래그\n(암호 있으면 입력창 표시)",
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

        success = 0
        fail = 0

        for file in files:
            file = file.strip()

            if not file.lower().endswith(".pdf"):
                continue

            self.status.config(text=f"처리 중: {os.path.basename(file)}")
            self.root.update_idletasks()

            try:
                if pdf_to_png(file, self.root):
                    success += 1
                else:
                    fail += 1
            except Exception as e:
                print(e)
                fail += 1

        self.status.config(text=f"완료: {success} / 실패: {fail}")

        messagebox.showinfo(
            "완료",
            f"성공: {success}\n실패: {fail}"
        )


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = App(root)
    root.mainloop()