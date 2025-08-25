import customtkinter as ctk
from gathering_funs import fetch_market_data, save_market_data
from tkinter import messagebox
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AlbionApp(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.title("Albion Online Market Data")
    self.geometry("600x450")

    # Entradas para listas separadas por comas
    self.label_items = ctk.CTkLabel(self, text="Items (IDs separados por coma):")
    self.label_items.pack(pady=(15,5))
    self.entry_items = ctk.CTkEntry(self, width=550)
    self.entry_items.insert(0, "T4_MAIN_CURSEDSTAFF,T5_MAIN_CURSEDSTAFF,T6_MAIN_CURSEDSTAFF")
    self.entry_items.pack()

    self.label_cities = ctk.CTkLabel(self, text="Ciudades (separadas por coma):")
    self.label_cities.pack(pady=(15,5))
    self.entry_cities = ctk.CTkEntry(self, width=550)
    self.entry_cities.insert(0, "Thetford,Martlock,Lymhurst,Bridgewatch,Fort Sterling,Caerleon,Black Market")
    self.entry_cities.pack()

    self.label_qualities = ctk.CTkLabel(self, text="Calidades (números separados por coma):")
    self.label_qualities.pack(pady=(15,5))
    self.entry_qualities = ctk.CTkEntry(self, width=550)
    self.entry_qualities.insert(0, "0,1,2,3,4,5")
    self.entry_qualities.pack()

    # Botón para fetch
    self.btn_fetch = ctk.CTkButton(self, text="Consultar datos", command=self.threaded_fetch)
    self.btn_fetch.pack(pady=(20,5))

    # Text area para mostrar resultados cortos
    self.txt_output = ctk.CTkTextbox(self, width=580, height=120)
    self.txt_output.pack(pady=(10,5))

    # Botón guardar CSV
    self.btn_save = ctk.CTkButton(self, text="Guardar CSV", command=self.save_csv, state="disabled")
    self.btn_save.pack(pady=10)

    self.market_data = None

  def threaded_fetch(self):
    self.btn_fetch.configure(state="disabled")
    self.txt_output.delete("0.0", "end")
    threading.Thread(target=self.fetch_data).start()

  def fetch_data(self):
    try:
      items = [i.strip() for i in self.entry_items.get().split(",") if i.strip()]
      cities = [c.strip() for c in self.entry_cities.get().split(",") if c.strip()]
      qualities = [int(q.strip()) for q in self.entry_qualities.get().split(",") if q.strip().isdigit()]
      API_URL = "https://west.albion-online-data.com/api/v2/stats/prices/"

      self.print_output(f"Consultando {len(items)} items en {len(cities)} ciudades con {len(qualities)} calidades...\n")
      data = fetch_market_data(items, cities, qualities, API_URL)
      self.market_data = data

      self.print_output(f"Datos obtenidos: {len(data)} registros\n")
      # Mostrar 5 registros de resumen
      for entry in data[:5]:
        line = f"{entry['Item ID']} | {entry['City']} | Q{entry['Quality']} | Sell Min: {entry['sell_price_min']} | Buy Max: {entry['buy_price_max']}\n"
        self.print_output(line)

      self.btn_save.configure(state="normal")
    except Exception as e:
      messagebox.showerror("Error", f"Ocurrió un error: {e}")
    finally:
      self.btn_fetch.configure(state="normal")

  def print_output(self, text):
    self.txt_output.insert("end", text)
    self.txt_output.see("end")

  def save_csv(self):
    if self.market_data:
      save_market_data(self.market_data, "cursed_staff")
      messagebox.showinfo("Guardado", "Archivo CSV guardado en carpeta output.")
    else:
      messagebox.showwarning("Aviso", "No hay datos para guardar.")

if __name__ == "__main__":
  app = AlbionApp()
  app.mainloop()
