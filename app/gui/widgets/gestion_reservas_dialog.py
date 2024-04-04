import tkinter as tk
from tkinter import messagebox, ttk

from app.database.connection import Session
from app.database.models import Reserva


class DialogoGestionReserva(tk.Toplevel):
    def __init__(self, parent, reserva_id_str):
        super().__init__(parent)
        self.reserva_id = int(reserva_id_str.split(': ')[1])
        self.parent = parent
        
        self.title("Gestionar Reserva")
        self.geometry("300x200")

        ttk.Label(self, text="¿Qué acción deseas realizar?").pack(pady=10)

        ttk.Button(self, text="Finalizar Pago", command=self.finalizar_pago).pack(fill=tk.X, padx=20, pady=5)
        ttk.Button(self, text="Eliminar Reserva", command=self.eliminar_reserva).pack(fill=tk.X, padx=20, pady=5)

        self.transient(parent)
        
        self.update_idletasks()
        self.grab_set()
        self.wait_window(self)

    def finalizar_pago(self):
        # Implementa la lógica para finalizar el pago
        with Session() as session:
            reserva = session.query(Reserva).filter_by(id=self.reserva_id).first()
            if reserva and reserva.pagada == False:
                reserva.importe_abonado = reserva.precio
                reserva.pagada = True
                session.commit()
                messagebox.showinfo("Pago finalizado", "El pago ha sido finalizado correctamente.")
                self.parent.cargar_reservas_existentes()
                self.destroy()

    def eliminar_reserva(self):
        respuesta = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que quieres eliminar esta reserva?")
        if respuesta:
            with Session() as session:
                reserva_a_eliminar = session.query(Reserva).filter_by(id=self.reserva_id).first()
                servicio_id = reserva_a_eliminar.servicio_id
                fecha_reserva = reserva_a_eliminar.fecha_reserva
                session.delete(reserva_a_eliminar)
                session.commit()

                # Comprueba si hay reservas en lista de espera para el mismo servicio y día
                reserva_en_lista_de_espera = session.query(Reserva).filter_by(servicio_id=servicio_id, fecha_reserva=fecha_reserva, en_lista_de_espera=True).order_by(Reserva.fecha_creacion).first()
                if reserva_en_lista_de_espera:
                    reserva_en_lista_de_espera.en_lista_de_espera = False
                    session.commit()
                    # Notifica al usuario que su reserva ha sido confirmada
                    messagebox.showinfo("Lista de espera", "Una reserva en lista de espera ha sido confirmada.")

                messagebox.showinfo("Reserva eliminada", "La reserva ha sido eliminada correctamente.")
                self.parent.cargar_reservas_existentes()
                self.destroy()

