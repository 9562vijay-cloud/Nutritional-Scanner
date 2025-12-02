import cv2
import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import zxingcpp

# -------------------------------
# FUNCTION 1 – SCAN BARCODES
# -------------------------------
def scan_barcode():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open webcam.")
        return None

    messagebox.showinfo("Info", "Scanning... Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to grab frame.")
            break

        cv2.imshow("Scanning Barcode", frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        results = zxingcpp.read_barcodes(gray)

        if results:
            barcode_data = results[0].text
            print("Barcode detected:", barcode_data)

            cap.release()
            cv2.destroyAllWindows()
            return barcode_data

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# ----------------------------------------
# FUNCTION 2 – GET NUTRITION FROM API
# ----------------------------------------
def get_macros_from_barcode(barcode):
    if not barcode:
        return None

    url = f"https://world.openfoodfacts.net/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") == 1:
            product = data["product"]
            nutriments = product.get("nutriments", {})

            return {
                "Product Name": product.get("product_name", "N/A"),
                "Brand": product.get("brands", "N/A"),
                "Calories (kcal/100g)": nutriments.get("energy-kcal_100g"),
                "Protein (g/100g)": nutriments.get("proteins_100g"),
                "Carbs (g/100g)": nutriments.get("carbohydrates_100g"),
                "Fat (g/100g)": nutriments.get("fat_100g"),
                "Image": product.get("image_front_small_url")
            }
        else:
            return None
    except:
        return None


# -----------------------------
# GUI LOGIC – DISPLAY
# -----------------------------
def start_scan():
    barcode = scan_barcode()
    if barcode:
        entry_barcode.delete(0, tk.END)
        entry_barcode.insert(0, barcode)
        fetch_data()


def fetch_data():
    barcode = entry_barcode.get().strip()

    if not barcode:
        messagebox.showwarning("Warning", "Please enter or scan a barcode.")
        return

    macros = get_macros_from_barcode(barcode)

    for row in tree.get_children():
        tree.delete(row)

    if macros:
        tree.insert("", "end", values=("Product Name", macros["Product Name"]))
        tree.insert("", "end", values=("Brand", macros["Brand"]))
        tree.insert("", "end", values=("Calories (kcal/100g)", macros["Calories (kcal/100g)"]))
        tree.insert("", "end", values=("Protein (g/100g)", macros["Protein (g/100g)"]))
        tree.insert("", "end", values=("Carbs (g/100g)", macros["Carbs (g/100g)"]))
        tree.insert("", "end", values=("Fat (g/100g)", macros["Fat (g/100g)"]))

        show_product_image(macros["Image"])
    else:
        messagebox.showerror("Error", "Product not found or no nutrition data available.")
        img_label.config(image='')


# ---------------------------------------------
# FUNCTION – SHOW PRODUCT IMAGE IN TKINTER
# ---------------------------------------------
def show_product_image(image_url):
    try:
        import requests
        from PIL import Image, ImageTk
        import io

        response = requests.get(image_url, timeout=10)
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))

        img = img.resize((300, 300), Image.Resampling.LANCZOS) 
        photo = ImageTk.PhotoImage(img)

        img_label.configure(image=photo, text="")
        img_label.image = photo 
    except:
        img_label.configure(image="", text="Image\nnot available", fg="#94A3B8")


# ---------------------------------------------
# BUILD GUI
# ---------------------------------------------
window = tk.Tk()
window.title("Barcode Nutrition Scanner")
window.geometry("800x850")
window.resizable(False, False)
window.configure(bg="#785964")

PRIMARY   = "#d5c7bc"
ACCENT    = "#454545"   
DANGER    = "#EF4444"
WARNING   = "#F59E0B"
BG_LIGHT  = "#F1F5F9"
CARD      = "#FFFFFF"

title_label = tk.Label(window, text="NUTRITION SCANNER", 
                       font=("Showcard Gothic", 25), 
                       fg=PRIMARY, bg="#785964")
title_label.pack(pady=(20, 10))

frame_top = tk.Frame(window, bg="#785964")
frame_top.pack(pady=15)

entry_barcode = tk.Entry(frame_top, font=("Arial", 14), width=28, 
                         relief="solid", bd=2, highlightthickness=2, 
                         highlightcolor=PRIMARY, highlightbackground="#E2E8F0")
entry_barcode.grid(row=0, column=0, padx=10)
entry_barcode.insert(0, "3017624010701")

btn_fetch = tk.Button(frame_top, text="Fetch Data", font=("Arial", 12, "bold"),
                      bg=PRIMARY, fg="white", relief="flat", padx=25, pady=10,
                      activebackground="#454545", activeforeground="white",
                      cursor="hand2",command=fetch_data)
btn_fetch.grid(row=0, column=1, padx=10)

btn_scan = tk.Button(window, text="Scan Barcode", font=("Arial", 16, "bold"),
                     bg=ACCENT, fg="white", relief="flat", pady=15,
                     activebackground="#d5c7bc", cursor="hand2",command=start_scan)
btn_scan.pack(pady=20, padx=80, fill="x")

img_label = tk.Label(window,padx=10, pady=10, bg=CARD, relief="solid", bd=1, highlightbackground="#E2E8F0",
                     text="Product image appears here",)
img_label.pack(pady=10)

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
                background="#f1fffa",
                foreground="#1E293B",
                rowheight=20,
                fieldbackground="white",
                font=("Arial", 11),
                borderwidth=1,
                relief="solid")

style.configure("Treeview.Heading",
                background=PRIMARY,
                foreground="#f1fffa",
                font=("Arial", 11, "bold"),
                padding=10)

style.map("Treeview", background=[("selected", "#f1fffa")])
style.map("Treeview.Heading", background=[("active", "#454545")])

table_frame = tk.Frame(window, bg="#f1fffa")
table_frame.pack(pady=10, padx=40, fill="both", expand=True)

tree = ttk.Treeview(table_frame, columns=("Nutrient", "Value"), show="headings", height=12)
tree.heading("Nutrient", text="Nutrient")
tree.heading("Value", text="Value per 100g")
tree.column("Nutrient", width=250, anchor="w")
tree.column("Value", width=250, anchor="center")
tree.pack(fill="both", expand=True)

window.mainloop()
