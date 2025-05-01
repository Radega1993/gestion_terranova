def pytest_addoption(parser):
    parser.addoption("--cleanup", action="store_true", default=False,
                    help="Limpiar datos de prueba antes de ejecutar los tests") 