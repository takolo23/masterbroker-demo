class IQOptionAdapter:
    """Interface intentionally disabled until an authorized official integration is confirmed."""
    mode = 'DEMO_ONLY'
    def connect(self, *args, **kwargs):
        raise RuntimeError('Conector IQ Option no configurado. No ingreses credenciales ni actives dinero real.')
    def place_order(self, *args, **kwargs):
        raise RuntimeError('Ejecuci�n real bloqueada. Valida una API/integraci�n autorizada y prueba en demo primero.')

