import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3

class ProductDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                precio REAL,
                stock INTEGER
            )
        """)
        self.conn.commit()

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", str(e))

    def fetch_all_products(self):
        return self.execute_query("SELECT * FROM productos")

    def add_product(self, nombre, precio, stock):
        self.execute_query("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)", nombre, precio, stock)

    def remove_product(self, product_id):
        self.execute_query("DELETE FROM productos WHERE id=?", product_id)

    def update_product(self, product_id, nombre, precio, stock):
        self.execute_query("UPDATE productos SET nombre=?, precio=?, stock=? WHERE id=?", nombre, precio, stock, product_id)

    def search_product(self, search_term):
        return self.execute_query("SELECT * FROM productos WHERE nombre LIKE ?", '%' + search_term + '%')


class ProductCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Productos")
        self.db = ProductDB("productos.db")
        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_input_fields(self):
        fields = [("Nombre del Producto:", 10), ("Precio:", 10), ("Stock:", 10)]
        self.entries = {}
        for label_text, width in fields:
            label = ttk.Label(self.root, text=label_text)
            label.pack(pady=(0, 5), padx=10, anchor="w")

            entry = ttk.Entry(self.root, width=width)
            entry.pack(pady=(0, 10), padx=10, fill="x")
            self.entries[label_text] = entry

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        buttons = [("Agregar", self.add_product), 
                   ("Eliminar", self.remove_product),
                   ("Actualizar", self.update_product), 
                   ("Buscar", self.search_product),
                   ("Mostrar Todo", self.show_all_products)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def load_products(self):
        self.clear_table()
        for row in self.db.fetch_all_products():
            self.tree.insert("", "end", values=row)

    def add_product(self):
        nombre = self.entries["Nombre del Producto:"].get()
        precio = float(self.entries["Precio:"].get())
        stock = int(self.entries["Stock:"].get())
        self.db.add_product(nombre, precio, stock)
        messagebox.showinfo("Éxito", "Producto agregado con éxito")
        self.load_products()
        self.clear_input_fields()

    def remove_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            self.db.remove_product(product_id)
            messagebox.showinfo("Éxito", "Producto eliminado con éxito")
            self.load_products()

    def update_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            nombre = self.entries["Nombre del Producto:"].get()
            precio = float(self.entries["Precio:"].get())
            stock = int(self.entries["Stock:"].get())
            self.db.update_product(product_id, nombre, precio, stock)
            messagebox.showinfo("Éxito", "Producto actualizado con éxito")
            self.load_products()
            self.clear_input_fields()

    def search_product(self):
        search_term = self.entries["Nombre del Producto:"].get()
        if search_term:
            self.clear_table()
            for row in self.db.search_product(search_term):
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")

    def show_all_products(self):
        self.load_products()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductCRUDApp(root)
    root.mainloop()
