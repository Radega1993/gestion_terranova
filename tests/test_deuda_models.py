import unittest
from datetime import datetime, date
from decimal import Decimal
from app.database.connection import Session
from app.database.models import Deuda, Venta, DetalleVenta, Producto, Socio, Usuario

class TestDeudaModels(unittest.TestCase):
    def setUp(self):
        self.session = Session()
        
        # Crear usuario trabajador
        self.trabajador = Usuario(
            nombre="Test Trabajador",
            user="test_worker",
            tipo_usuario="trabajador",
            contrasena_hash="test_hash",
            activo=True
        )
        self.session.add(self.trabajador)
        
        # Crear socio
        self.socio = Socio(
            nombre="Test Socio",
            primer_apellido="Test",
            segundo_apellido="Test",
            email="test_deuda@test.com",
            dni="12345678A",
            direccion="Test Address",
            poblacion="Test City",
            codigo_postal="12345",
            provincia="Test Province",
            telefono="123456789",
            fecha_nacimiento=date(1990, 1, 1),
            fecha_registro=date.today(),
            activo=True,
            es_principal=True
        )
        self.session.add(self.socio)
        
        # Crear productos
        self.producto1 = Producto(
            nombre="Producto 1",
            precio=10.0,
            stock_actual=100,
            activo=True
        )
        self.producto2 = Producto(
            nombre="Producto 2",
            precio=15.0,
            stock_actual=100,
            activo=True
        )
        self.producto3 = Producto(
            nombre="Producto 3",
            precio=5.0,
            stock_actual=100,
            activo=True
        )
        
        self.session.add_all([self.producto1, self.producto2, self.producto3])
        self.session.commit()

    def test_pago_parcial_deuda(self):
        """Test para verificar el proceso de pago parcial de una deuda"""
        
        # 1. Crear una deuda con múltiples productos
        deuda = Deuda(
            fecha=date.today(),
            total=85.0,  # 2*10 + 3*15 + 4*5 = 20 + 45 + 20 = 85
            socio_id=self.socio.id,
            trabajador_id=self.trabajador.id,
            pagada=False
        )
        self.session.add(deuda)
        self.session.flush()
        
        # Agregar detalles de venta a la deuda
        detalles = [
            DetalleVenta(
                producto_id=self.producto1.id,
                cantidad=2,
                precio=10.0,
                deuda_id=deuda.id
            ),
            DetalleVenta(
                producto_id=self.producto2.id,
                cantidad=3,
                precio=15.0,
                deuda_id=deuda.id
            ),
            DetalleVenta(
                producto_id=self.producto3.id,
                cantidad=4,
                precio=5.0,
                deuda_id=deuda.id
            )
        ]
        self.session.add_all(detalles)
        self.session.commit()
        
        # Verificar estado inicial
        deuda_inicial = self.session.query(Deuda).get(deuda.id)
        self.assertEqual(deuda_inicial.total, 85.0)
        self.assertEqual(len(deuda_inicial.detalles), 3)
        
        # 2. Realizar pago parcial
        # Pagar: 1 unidad del producto1 (10) y 2 unidades del producto2 (30)
        venta = Venta(
            fecha=date.today(),
            total=40.0,
            socio_id=self.socio.id,
            trabajador_id=self.trabajador.id,
            pagada=True,
            metodo_pago='efectivo'
        )
        self.session.add(venta)
        self.session.flush()
        
        # Actualizar detalles de la deuda y crear detalles de la venta
        detalles_venta = [
            DetalleVenta(
                producto_id=self.producto1.id,
                cantidad=1,
                precio=10.0,
                venta_id=venta.id
            ),
            DetalleVenta(
                producto_id=self.producto2.id,
                cantidad=2,
                precio=15.0,
                venta_id=venta.id
            )
        ]
        self.session.add_all(detalles_venta)
        
        # Actualizar cantidades en la deuda original
        for detalle in deuda.detalles:
            if detalle.producto_id == self.producto1.id:
                detalle.cantidad -= 1
            elif detalle.producto_id == self.producto2.id:
                detalle.cantidad -= 2
                
        # Actualizar total de la deuda
        deuda.total = 45.0  # 1*10 + 1*15 + 4*5 = 10 + 15 + 20 = 45
        self.session.commit()
        
        # 3. Verificar estado final
        deuda_final = self.session.query(Deuda).get(deuda.id)
        self.assertEqual(deuda_final.total, 45.0)
        
        # Verificar detalles restantes en la deuda
        detalles_restantes = {
            (d.producto_id, d.cantidad): d.precio 
            for d in deuda_final.detalles
        }
        
        self.assertEqual(len(detalles_restantes), 3)
        self.assertEqual(detalles_restantes[(self.producto1.id, 1)], 10.0)
        self.assertEqual(detalles_restantes[(self.producto2.id, 1)], 15.0)
        self.assertEqual(detalles_restantes[(self.producto3.id, 4)], 5.0)
        
        # Verificar venta creada
        venta_realizada = self.session.query(Venta).get(venta.id)
        self.assertEqual(venta_realizada.total, 40.0)
        self.assertEqual(len(venta_realizada.detalles), 2)
        
        detalles_venta = {
            (d.producto_id, d.cantidad): d.precio 
            for d in venta_realizada.detalles
        }
        self.assertEqual(detalles_venta[(self.producto1.id, 1)], 10.0)
        self.assertEqual(detalles_venta[(self.producto2.id, 2)], 15.0)

    def tearDown(self):
        # Limpiar la base de datos
        self.session.query(DetalleVenta).delete()
        self.session.query(Venta).delete()
        self.session.query(Deuda).delete()
        self.session.query(Producto).delete()
        self.session.query(Socio).delete()
        self.session.query(Usuario).delete()
        self.session.commit()
        self.session.close() 