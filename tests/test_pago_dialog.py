import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.database.models import Deuda, Venta, DetalleVenta, Producto, Socio
from app.gui.widgets.pago_dialog import PagoDialog
from app.database.database import Session

class TestPagoDialog(unittest.TestCase):
    def setUp(self):
        self.session = Session()
        
        # Crear datos de prueba
        self.socio = Socio(
            id=1,
            nombre="Test Socio",
            email="test@test.com",
            es_principal=True
        )
        
        self.producto = Producto(
            id=1,
            nombre="Test Producto",
            precio=10.0,
            stock_actual=100
        )
        
        self.deuda = Deuda(
            id=1,
            socio_id=self.socio.id,
            fecha=datetime.now(),
            total=30.0,
            trabajador_id=1,
            pagada=False
        )
        
        self.detalle_venta = DetalleVenta(
            producto_id=self.producto.id,
            cantidad=3,
            precio=10.0,
            deuda_id=self.deuda.id
        )
        
        # Mock del widget padre
        self.parent = MagicMock()
        
    def tearDown(self):
        self.session.rollback()
        self.session.close()
        
    @patch('app.gui.widgets.pago_dialog.Session')
    def test_pago_completo_deuda(self, mock_session):
        """Prueba el pago completo de una deuda"""
        mock_session.return_value = self.session
        dialog = PagoDialog(self.parent, self.socio.id, [], True, self.deuda.id)
        dialog.entry_monto.get = MagicMock(return_value="30.0")
        
        # Simular el pago
        dialog.procesar_pago()
        
        # Verificar que la deuda se marcó como pagada
        self.assertTrue(self.deuda.pagada)
        self.assertEqual(self.deuda.metodo_pago, "efectivo")  # método por defecto
        
    @patch('app.gui.widgets.pago_dialog.Session')
    def test_pago_parcial_deuda(self, mock_session):
        """Prueba el pago parcial de una deuda"""
        mock_session.return_value = self.session
        dialog = PagoDialog(self.parent, self.socio.id, [], True, self.deuda.id)
        dialog.entry_monto.get = MagicMock(return_value="20.0")
        
        # Simular el pago parcial
        dialog.procesar_pago()
        
        # Verificar que se creó una nueva deuda con el monto restante
        deudas = self.session.query(Deuda).filter_by(socio_id=self.socio.id, pagada=False).all()
        self.assertEqual(len(deudas), 1)
        self.assertEqual(deudas[0].total, 10.0)  # 30 - 20 = 10
        
    @patch('app.gui.widgets.pago_dialog.Session')
    def test_pago_venta_normal(self, mock_session):
        """Prueba el pago de una venta normal (no deuda)"""
        mock_session.return_value = self.session
        detalles_venta = [
            {"producto_id": self.producto.id, "cantidad": 2, "precio": 10.0}
        ]
        dialog = PagoDialog(self.parent, self.socio.id, detalles_venta, False, None)
        dialog.entry_monto.get = MagicMock(return_value="20.0")
        
        # Simular el pago
        dialog.procesar_pago()
        
        # Verificar que se creó la venta
        ventas = self.session.query(Venta).filter_by(socio_id=self.socio.id).all()
        self.assertEqual(len(ventas), 1)
        self.assertEqual(ventas[0].total, 20.0)
        
    @patch('app.gui.widgets.pago_dialog.Session')
    def test_validacion_monto(self, mock_session):
        """Prueba la validación del monto de pago"""
        mock_session.return_value = self.session
        dialog = PagoDialog(self.parent, self.socio.id, [], True, self.deuda.id)
        dialog.entry_monto.get = MagicMock(return_value="-10.0")
        
        # Simular el pago con monto inválido
        with self.assertRaises(ValueError):
            dialog.procesar_pago()
            
if __name__ == '__main__':
    unittest.main() 