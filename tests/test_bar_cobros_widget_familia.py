import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from datetime import datetime, timezone
from app.gui.widgets.bar_cobros_widget import BarCobrosWidget
from app.database.models import Socio, Deuda, DetalleVenta, Producto, MiembroFamilia

class TestBarCobrosWidgetFamilia(unittest.TestCase):
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
        
        # Crear miembros de familia de prueba
        self.miembro_familia1 = Socio(
            id=2,
            nombre="María Pérez",
            email="maria@example.com",
            es_principal=False,
            socio_principal_id=1
        )
        
        self.miembro_familia2 = Socio(
            id=3,
            nombre="Pedro Pérez",
            email="pedro@example.com",
            es_principal=False,
            socio_principal_id=1
        )
        
        # Crear productos de prueba
        self.producto1 = Producto(id=1, nombre="Producto 1", precio=10.0, stock_actual=5)
        self.producto2 = Producto(id=2, nombre="Producto 2", precio=20.0, stock_actual=3)
        
        # Crear deudas de prueba para el socio principal
        self.deuda_principal = Deuda(
            id=1,
            socio_id=1,
            fecha=datetime.now(timezone.utc),
            total=30.0,
            trabajador_id=1,
            pagada=False
        )
        
        # Crear deudas de prueba para los miembros de familia
        self.deuda_miembro1 = Deuda(
            id=2,
            socio_id=2,
            fecha=datetime.now(timezone.utc),
            total=20.0,
            trabajador_id=1,
            pagada=False
        )
        
        self.deuda_miembro2 = Deuda(
            id=3,
            socio_id=3,
            fecha=datetime.now(timezone.utc),
            total=40.0,
            trabajador_id=1,
            pagada=False
        )
        
        # Crear detalles de venta de prueba
        self.detalle_principal = DetalleVenta(
            id=1,
            deuda_id=1,
            producto_id=1,
            cantidad=2,
            precio=10.0
        )
        
        self.detalle_miembro1 = DetalleVenta(
            id=2,
            deuda_id=2,
            producto_id=2,
            cantidad=1,
            precio=20.0
        )
        
        self.detalle_miembro2 = DetalleVenta(
            id=3,
            deuda_id=3,
            producto_id=1,
            cantidad=2,
            precio=10.0
        )
        
        # Mock para messagebox
        self.messagebox_patcher = patch('app.gui.widgets.bar_cobros_widget.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
    
    def tearDown(self):
        self.messagebox_patcher.stop()
        self.root.destroy()
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_cargar_deudas_pendientes_familia(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver los miembros de familia
        self.session.query.return_value.filter_by.return_value.all.return_value = [
            self.miembro_familia1,
            self.miembro_familia2
        ]
        
        # Configurar el mock para devolver las deudas
        def mock_filter_by(**kwargs):
            if 'socio_id' in kwargs:
                if kwargs['socio_id'] == 1:
                    return MagicMock(all=lambda: [self.deuda_principal])
                elif kwargs['socio_id'] == 2:
                    return MagicMock(all=lambda: [self.deuda_miembro1])
                elif kwargs['socio_id'] == 3:
                    return MagicMock(all=lambda: [self.deuda_miembro2])
            return MagicMock(all=lambda: [])
        
        self.session.query.return_value.filter_by.side_effect = mock_filter_by
        
        # Configurar el mock para devolver los detalles de venta
        def mock_filter_by_detalles(**kwargs):
            if 'deuda_id' in kwargs:
                if kwargs['deuda_id'] == 1:
                    return MagicMock(all=lambda: [self.detalle_principal])
                elif kwargs['deuda_id'] == 2:
                    return MagicMock(all=lambda: [self.detalle_miembro1])
                elif kwargs['deuda_id'] == 3:
                    return MagicMock(all=lambda: [self.detalle_miembro2])
            return MagicMock(all=lambda: [])
        
        self.session.query.return_value.filter_by.side_effect = mock_filter_by_detalles
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio principal
        widget.socio_actual = self.socio_principal
        widget.cargar_deudas_pendientes(widget.socio_actual.id)
        
        # Verificar que se cargaron todas las deudas en la lista
        self.assertEqual(len(widget.lista_deudas.get_children()), 3)
        
        # Verificar que se muestra el total correcto (suma de todas las deudas)
        self.assertEqual(widget.total_deudas, 90.0)
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_obtener_total_deudas_familia(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver los miembros de familia
        self.session.query.return_value.filter_by.return_value.all.return_value = [
            self.miembro_familia1,
            self.miembro_familia2
        ]
        
        # Configurar el mock para devolver las deudas
        def mock_filter_by(**kwargs):
            if 'socio_id' in kwargs:
                if kwargs['socio_id'] == 1:
                    return MagicMock(all=lambda: [self.deuda_principal])
                elif kwargs['socio_id'] == 2:
                    return MagicMock(all=lambda: [self.deuda_miembro1])
                elif kwargs['socio_id'] == 3:
                    return MagicMock(all=lambda: [self.deuda_miembro2])
            return MagicMock(all=lambda: [])
        
        self.session.query.return_value.filter_by.side_effect = mock_filter_by
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Obtener el total de deudas de la familia
        total = widget.obtener_total_deudas_socio(self.socio_principal.id)
        
        # Verificar que el total es correcto (suma de todas las deudas)
        self.assertEqual(total, 90.0)
    
    @patch('app.gui.widgets.bar_cobros_widget.Session')
    def test_pagar_deuda_miembro_familia(self, mock_session):
        mock_session.return_value = self.session
        
        # Configurar el mock para devolver el socio principal
        self.session.query.return_value.get.return_value = self.socio_principal
        
        # Configurar el mock para devolver los miembros de familia
        self.session.query.return_value.filter_by.return_value.all.return_value = [
            self.miembro_familia1,
            self.miembro_familia2
        ]
        
        # Configurar el mock para devolver las deudas
        def mock_filter_by(**kwargs):
            if 'socio_id' in kwargs:
                if kwargs['socio_id'] == 1:
                    return MagicMock(all=lambda: [self.deuda_principal])
                elif kwargs['socio_id'] == 2:
                    return MagicMock(all=lambda: [self.deuda_miembro1])
                elif kwargs['socio_id'] == 3:
                    return MagicMock(all=lambda: [self.deuda_miembro2])
            return MagicMock(all=lambda: [])
        
        self.session.query.return_value.filter_by.side_effect = mock_filter_by
        
        # Configurar el mock para devolver los detalles de venta
        def mock_filter_by_detalles(**kwargs):
            if 'deuda_id' in kwargs:
                if kwargs['deuda_id'] == 1:
                    return MagicMock(all=lambda: [self.detalle_principal])
                elif kwargs['deuda_id'] == 2:
                    return MagicMock(all=lambda: [self.detalle_miembro1])
                elif kwargs['deuda_id'] == 3:
                    return MagicMock(all=lambda: [self.detalle_miembro2])
            return MagicMock(all=lambda: [])
        
        self.session.query.return_value.filter_by.side_effect = mock_filter_by_detalles
        
        # Crear el widget
        widget = BarCobrosWidget(self.root)
        
        # Simular selección de socio principal
        widget.socio_actual = self.socio_principal
        widget.cargar_deudas_pendientes(widget.socio_actual.id)
        
        # Simular selección de deuda de un miembro de familia
        widget.lista_deudas.insert('', 'end', values=(2, '2024-03-20', '20.0€'))
        widget.lista_deudas.selection_set(widget.lista_deudas.get_children()[1])  # Seleccionar deuda del miembro 1
        
        # Mock para simular que el pago fue exitoso
        self.mock_messagebox.askyesno.return_value = True
        
        # Llamar al método de pago
        widget.pagar_deuda()
        
        # Verificar que se creó el diálogo de pago
        self.session.query.return_value.get.assert_called_with(2)  # Verificar que se consultó la deuda del miembro
        
        # Verificar que se actualizó la lista de deudas
        self.assertEqual(len(widget.lista_deudas.get_children()), 2)

if __name__ == '__main__':
    unittest.main() 