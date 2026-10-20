# Inicio con un clic

Haz doble clic en `INICIAR_MASTERBROKER_DEMO.cmd`.

El agente se queda activo y revisa cada minuto:

- `data/inbox/*.csv`: velas OHLC con `timestamp,open,high,low,close,volume`. Cada archivo nuevo se prueba, aprende y queda registrado.
- `data/research/*.md` o `*.txt`: notas de an�lisis o investigaci�n. El agente guarda una memoria append-only de cada lectura.

El estado actual aparece en `reports/agent_status.json`. La orden real permanece desactivada y el perfil de IQ Option es exclusivamente DEMO.

