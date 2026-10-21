# IQ Option MasterBroker - modo seguro de investigaci�n

Sistema local para analizar velas OHLC, ejecutar simulaciones, validar estrategias con *walk-forward* y llevar una bit�cora SQLite. Est� dise�ado para que el aprendizaje ajuste y compare par�metros **solo en simulaci�n**; nunca cambia una estrategia en operaci�n ni aumenta el tama�o despu�s de una p�rdida.

## Qu� incluye

- Estrategia de confluencia: tendencia EMA, RSI y volatilidad.
- Motor de *backtesting* con costos y una separaci�n temporal de entrenamiento/prueba.
- Selector de par�metros con controles de calidad; rechaza candidatos que no superen el umbral.
- Gesti�n estricta de riesgo: riesgo por operaci�n, p�rdida m�xima diaria, operaciones m�ximas, racha m�xima de p�rdidas y cortacircuitos.
- Bit�cora de cada decisi�n y operaci�n en SQLite.
- Adaptador IQ Option sin credenciales y deliberadamente bloqueado para ejecutar dinero real.

## Equipo de agentes demo

El panel y el servicio local incluyen cuatro agentes internos con consenso auditable:

- **Analista de mercado:** revisa la confluencia de la se?al y su direcci?n.
- **Guardi?n de riesgo:** bloquea una propuesta si no alcanza la confianza configurada o existe una pausa por noticia.
- **Validador de ejecuci?n demo:** confirma que cualquier entrada sea estrictamente virtual.
- **Revisor de aprendizaje:** exige registro y validaci?n antes de promover cambios de estrategia.

El coordinador devuelve `HIGHER`, `LOWER` o `NO_OPERAR`; por defecto est? en **solo analizar**, confianza m?nima de **85%** y confirmaci?n del usuario. Su estado se guarda en `reports/agent_team_status.json` y puede leerse desde `http://127.0.0.1:8765/api/agents`.

## Uso

Requiere Python 3.11+ y no instala paquetes externos.

```powershell
cd IQOption_MasterBroker
python run_demo.py
```

El comando genera:

- `reports/walk_forward_report.json`
- `reports/trades.csv`
- `reports/masterbroker.sqlite`

Para datos reales, coloca un CSV en `data/` con columnas `timestamp,open,high,low,close,volume` y usa `--csv .\data\archivo.csv`.

```powershell
python run_demo.py --csv .\data\EURUSD_5m.csv
```

## Puesta en producci�n

No conectes contrase�as, cookies o claves a c�digo o chats. Antes de cualquier ejecuci�n con saldo real se necesita: usar cuenta demo, revisar los resultados fuera de muestra, confirmar que la plataforma autoriza la integraci�n elegida y habilitar manualmente una conexi�n auditada. `IQOptionAdapter.place_order()` lanza un error por dise�o.

## L�mites por defecto

| Control | Valor |
| --- | ---: |
| Riesgo por operaci�n | 0.5% |
| P�rdida m�xima diaria | 2% |
| Operaciones por d�a | 4 |
| Racha m�xima de p�rdidas | 3 |
| M�nimo de operaciones de prueba | 30 |

Estos l�mites est�n en `masterbroker/config.py`.
## Memoria de aprendizaje

Cada ciclo se guarda en dos archivos:

- `reports/model_registry.json`: estado y estrategia actual.
- `reports/learning_ledger.jsonl`: memoria de auditor�a **append-only**. Conserva cada evaluaci�n, incluso las rechazadas, sin eliminar ciclos previos.

El agente solo puede promover un modelo para simulaci�n despu�s de validaci�n fuera de muestra. Nunca activa ejecuci�n real ni altera los l�mites de riesgo.
## Sesi�n de IQ Option en navegador

`configure_browser_demo.py` conserva el perfil de la sesi�n que abriste en el navegador: cuenta **DEMO**, EUR/USD Blitz, 1 minuto y $1 virtual.

No guarda contrase�as, cookies, c�digos de verificaci�n ni datos de pago. El perfil deja `order_execution` en `DISABLED`; conecta el contexto de la sesi�n al agente sin habilitar �rdenes.

## Servicio de aprendizaje continuo

Ejecuta `INICIAR_MASTERBROKER_DEMO.cmd` para iniciar el servicio local. No requiere instalaciones adicionales: usa Python local y las librer�as est�ndar. El servicio solo procesa informaci�n que exista en `data/inbox` y `data/research`; guarda cada lectura en sus bit�coras persistentes.
# Panel, alertas y datos

- **Panel local:** al abrir `INICIAR_MASTERBROKER_DEMO.cmd`, visita `http://127.0.0.1:8765`. Muestra estado, �ltima se�al demo y alertas.
- **Alertas de noticia:** una nota nueva que mencione eventos como FOMC, CPI, NFP, inflaci�n o tipos de inter�s activa una pausa de seguridad y la registra.
- **Perfiles por activo:** `data/asset_profiles.json` conserva una configuraci�n independiente por activo.
- **Datos en vivo opcionales:** `masterbroker/data_source.py` incorpora un lector de Forex Intraday de Alpha Vantage. Requiere una clave local en la variable de entorno `ALPHAVANTAGE_API_KEY`; jam�s la guardes en este proyecto ni la compartas aqu�. Los datos se usan para investigaci�n y se�ales demo, nunca para enviar �rdenes.

## Dise�o y datos en vivo

La app se actualiza cada dos segundos con la actividad que genera el agente y las fuentes de datos configuradas. Muestra la sesi�n demo de IQ Option como contexto; no afirma ni inventa operaciones del navegador. Para ver datos de precio nuevos debe existir un CSV nuevo en `data/inbox` o configurarse una fuente autorizada, como el conector opcional de Alpha Vantage.

