# Ciclo aut�nomo de aprendizaje

`learn.py` crea un registro persistente de modelos evaluados. Cada ciclo:

1. Carga velas OHLC de un CSV o datos de demostraci�n.
2. Prueba combinaciones limitadas de la estrategia en el tramo de entrenamiento.
3. Las valida en un tramo temporal separado.
4. Guarda el candidato �nicamente si supera cantidad m�nima de operaciones, *profit factor* y m�ximo *drawdown*.
5. Si falla, conserva el modelo anterior y anota el rechazo.

Ejecuta un ciclo:

```powershell
python learn.py --csv .\data\mercado.csv
```

El archivo `reports/model_registry.json` conserva el historial de los �ltimos 30 ciclos. El agente est� restringido a `PAPER_TRADING_ONLY`; no puede conectarse ni enviar �rdenes reales.

