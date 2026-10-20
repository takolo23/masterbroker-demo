# Investigaci�n base - IQ Option y automatizaci�n

Consultado el 20 de octubre de 2026.

1. La gu�a oficial de IQ Option indica que la automatizaci�n debe partir de reglas claras, *stop losses*, supervisi�n y registro de operaciones.
2. Su gu�a sobre bots de IA indica que el paso inicial debe ser probar en demo, con l�mite de riesgo por operaci�n, p�rdida m�xima diaria/semanal, operaciones por d�a, control manual y sin acceso a retiros.
3. En la documentaci�n revisada no se identific� una API p�blica oficial de ejecuci�n de �rdenes. Por ello este proyecto no automatiza el inicio de sesi�n ni env�a �rdenes al broker.

Fuentes oficiales:
- https://blog.iqoption.com/en/how-to-set-up-a-trading-bot/
- https://blog.iqoption.com/en/how-ai-trading-bots-work/
- https://iqoption.com/en/quotes

Decisi�n de dise�o: todas las pruebas se ejecutan localmente sobre datos CSV o datos sint�ticos; la ejecuci�n real est� bloqueada en el adaptador hasta verificar por escrito una integraci�n permitida y completar pruebas demo.

