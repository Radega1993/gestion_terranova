# EstadoApp.py

class EstadoApp:
    _instance = None
    usuario_logueado_id = None

    @staticmethod
    def get_instance():
        if EstadoApp._instance is None:
            EstadoApp._instance = EstadoApp()
        return EstadoApp._instance

    @classmethod
    def set_usuario_logueado_id(cls, usuario_id):
        cls.usuario_logueado_id = usuario_id

    @classmethod
    def get_usuario_logueado_id(cls):
        return cls.usuario_logueado_id
