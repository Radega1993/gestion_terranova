import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from datetime import datetime, timezone
from app.gui.widgets.bar_cobros_widget import BarCobrosWidget
from app.database.models import Socio, Deuda, DetalleVenta, Producto, MiembroFamilia

class TestBarCobrosWidget(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        
        # Mock de la sesión
        self.session = MagicMock()
        
        # Crear socio principal de prueba
        self.socio_principal = Socio(
            id=1,
            nombre="Juan Pérez",
            email="juan@example.com",
            es_principal=True
        )
        
        # Crear miembro de familia de prueba
        self.miembro_familia = Socio(
            id=2,
            nombre="María Pérez",
            email="maria@example.com",
            es_principal=False,
            socio_principal_id=1
        )
        
        # Crear productos de prueba
        self.producto1 = Producto(id=1, nombre="Producto 1", precio=10.0, stock_actual=5)
        self.producto2 = Producto(id=2, nombre="Producto 2", precio=20.0, stock_actual=3)
        
        # Crear deudas de prueba
        self.deuda1 = Deuda(
            id=1,
            socio_id=1,
            fecha=datetime.now(timezone.utc),
            total=30.0,
            trabajador_id=1,
            pagada=False
        )
        
        self.deuda2 = Deuda(
            id=2,
            socio_id=2,
            fecha=datetime.now(timezone.utc),
            total=20.0,
            trabajador_id=1,
            pagada=False
        )
        
        # Crear detalles de venta de prueba
        self.detalle1 = DetalleVenta(
            id=1,
            deuda_id=1,
            producto_id=1,
            cantidad=2,
            precio=10.0
        )
        
        self.detalle2 = DetalleVenta(
            id=2,
            deuda_id=1,
            producto_id=2,
            cantidad=1,
            precio=20.0
        )
        
        # Mock para messagebox
        self.messagebox_patcher = patch('app.gui.widgets.bar_cobros_widget.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
    
    def tearDown(self):
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_cargar_deudas_pendientes_socio_principal(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver las deudas
        self.session.query.return_value.filter_by.return_value.all.return_value = [self.deuda1]
        
        # Configurar el mock para devolver los detalles de venta
        self.session.query.return_value.filter_by.return_value.all.side_effect = [
            [self.detalle1, self.detalle2]  # Para la primera llamada (detalles de venta)
        ]
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio
        widget.socio_actual = self.socio_principal
        widget.cargar_deudas_pendientes(widget.socio_actual.id)
        
        # Verificar que se cargaron las deudas en la lista
        self.assertEqual(len(widget.lista_deudas.get_children()), 1)
        
        # Verificar que se muestra el total correcto
        self.assertEqual(widget.total_deudas, 30.0)
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_obtener_total_deudas_socio(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver las deudas
        self.session.query.return_value.filter_by.return_value.all.return_value = [self.deuda1]
        
        # Configurar el mock para devolver los detalles de venta
        self.session.query.return_value.filter_by.return_value.all.side_effect = [
            [self.detalle1, self.detalle2]  # Para la primera llamada (detalles de venta)
        ]
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Obtener el total de deudas
        total = widget.obtener_total_deudas_socio(self.socio_principal.id)
        
        # Verificar que el total es correcto
        self.assertEqual(total, 30.0)
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_pagar_deuda(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver las deudas
        self.session.query.return_value.filter_by.return_value.all.return_value = [self.deuda1]
        
        # Configurar el mock para devolver los detalles de venta
        self.session.query.return_value.filter_by.return_value.all.side_effect = [
            [self.detalle1, self.detalle2]  # Para la primera llamada (detalles de venta)
        ]
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio y deuda
        widget.socio_actual = self.socio_principal
        widget.cargar_deudas_pendientes(widget.socio_actual.id)
        
        # Simular selección de deuda
        widget.lista_deudas.insert('', 'end', values=(1, '2024-03-20', '30.0€'))
        widget.lista_deudas.selection_set(widget.lista_deudas.get_children()[0])
        
        # Mock para simular que el pago fue exitoso
        self.mock_messagebox.askyesno.return_value = True
        
        # Llamar al método de pago
        widget.pagar_deuda()
        
        # Verificar que se creó el diálogo de pago
        self.session.query.return_value.get.assert_called_with(1)  # Verificar que se consultó la deuda
        
        # Verificar que se actualizó la lista de deudas
        self.assertEqual(len(widget.lista_deudas.get_children()), 0)

    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_seleccionar_deuda_sin_socio(self, mock_session):
        mock_session.return_value = self.session
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Intentar seleccionar una deuda sin socio
        widget.seleccionar_deuda()
        
        # Verificar que se mostró el mensaje de error
        self.mock_messagebox.showerror.assert_called_with("Error", "Debe seleccionar un socio primero")

    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_seleccionar_deuda_sin_seleccion(self, mock_session):
        mock_session.return_value = self.session
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio
        widget.socio_actual = self.socio_principal
        
        # Intentar seleccionar una deuda sin selección
        widget.seleccionar_deuda()
        
        # Verificar que se mostró el mensaje de error
        self.mock_messagebox.showerror.assert_called_with("Error", "Debe seleccionar una deuda")

    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_seleccionar_deuda_no_encontrada(self, mock_session):
        mock_session.return_value = self.session
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio
        widget.socio_actual = self.socio_principal
        
        # Simular selección de deuda
        widget.lista_deudas.insert('', 'end', values=(999, '2024-03-20', '30.0€'))
        widget.lista_deudas.selection_set(widget.lista_deudas.get_children()[0])
        
        # Configurar el mock para devolver None al buscar la deuda
        self.session.query.return_value.get.return_value = None
        
        # Intentar seleccionar una deuda que no existe
        widget.seleccionar_deuda()
        
        # Verificar que se mostró el mensaje de error
        self.mock_messagebox.showerror.assert_called_with("Error", "No se encontró la deuda")

    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_seleccionar_deuda_sin_detalles(self, mock_session):
        mock_session.return_value = self.session
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio
        widget.socio_actual = self.socio_principal
        
        # Simular selección de deuda
        widget.lista_deudas.insert('', 'end', values=(1, '2024-03-20', '30.0€'))
        widget.lista_deudas.selection_set(widget.lista_deudas.get_children()[0])
        
        # Configurar el mock para devolver la deuda pero sin detalles
        self.session.query.return_value.get.return_value = self.deuda1
        self.session.query.return_value.filter_by.return_value.all.return_value = []
        
        # Intentar seleccionar una deuda sin detalles
        widget.seleccionar_deuda()
        
        # Verificar que se mostró el mensaje de error
        self.mock_messagebox.showerror.assert_called_with("Error", "No se encontraron detalles para la deuda")

    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_actualizar_total_deudas(self, mock_session):
        mock_session.return_value = self.session
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Configurar el mock para devolver el total de deudas
        self.session.query.return_value.filter.return_value.scalar.return_value = 50.0
        
        # Simular selección de socio
        widget.socio_actual = self.socio_principal
        
        # Actualizar el total de deudas
        widget.actualizar_total_deudas_socio(widget.socio_actual.id)
        
        # Verificar que se actualizó el label con el total correcto
        self.assertEqual(widget.total_deudas_label.cget("text"), "Total deudas: 50.00€")

if __name__ == '__main__':
    unittest.main() 