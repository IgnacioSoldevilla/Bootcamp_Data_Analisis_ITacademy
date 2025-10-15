USE transactions;


-- 0) Mostra totes les dades de la taula company para ayuda.
SELECT * 
FROM company;

-- 0) Mostra totes les dades de la taula transaction para ayuda.
SELECT * 
FROM transaction;

-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  1 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- EJERCICIO 2.  *************** Utilizando JOIN realizarás las siguientes consultas: *************************************************************************************

-- ***** Ejercicio 2.1) Listado de los países que están generando ventas. *****
SELECT DISTINCT c.country AS paises_generan_ventas
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
WHERE t.declined =0;

-- ***** Ejercicio 2.2) Desde cuántos países se generan las ventas. *****
SELECT count(DISTINCT c.country) AS paises_realizando_ventas
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
WHERE t.declined =0;

-- ***** Ejercicio 2.3) Identifica a la compañía con la mayor media de ventas. *****
SELECT c.company_name AS compañia_mayor_media_ventas, ROUND(AVG(t.amount),2) AS ventas_medias
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
GROUP BY c.company_name
ORDER BY ventas_medias DESC
LIMIT 1;

-- EJERCICIO 3.  *************** Utilizando sólo subconsultas (sin utilizar JOIN): *************************************************************************************

-- ***** Ejercicio 3.1) Muestra todas las transacciones realizadas por empresas de Alemania. *****

-- Query principal con EXISTS
SELECT t.*
FROM transaction AS t
WHERE EXISTS (SELECT c.id
			FROM company AS c
			WHERE (t.company_id=c.id) AND (c.country = "Germany"));


-- Query principal con IN
SELECT t.*
FROM transaction AS t
WHERE t.company_id IN (SELECT c.id
					FROM company AS c
					WHERE c.country = "Germany");


-- subquery secundaria
SELECT c.id
FROM company AS c
WHERE c.country = "Germany";


-- ***** Ejercicio 3.2) Lista las empresas que han realizado transacciones por un amount superior a la media de todas las transacciones. *****
-- Entiendo que con que una empresa haya realizado 1 transaccion superior a la media ya la cuento

-- Query principal con EXISTS
SELECT c.company_name, c.id
FROM company AS c
WHERE EXISTS (
    SELECT t.company_id
    FROM transaction AS t
    WHERE (c.id = t.company_id) 
		AND (t.amount >= (
			SELECT AVG(t.amount)
			FROM transaction AS t)) 
);


-- con IN
SELECT c.company_name, c.id
FROM company AS c
WHERE c.id IN (
    SELECT t.company_id
    FROM transaction AS t
    WHERE t.amount >= (
        SELECT AVG(t.amount)
        FROM transaction AS t)
);

-- subquery secundarias
SELECT avg(t.amount)
FROM transaction AS t;

SELECT t.company_id
    FROM transaction AS t
    WHERE t.amount > (
        SELECT AVG(t.amount)
        FROM transaction AS t);



-- ***** Ejercicio 3.3) Eliminarán del sistema las empresas que carecen de transacciones registradas, entrega el listado de estas empresas. *****

-- Query principal con EXISTS
SELECT c.company_name AS nombre_compañia_sin_tracsacciones
FROM company AS c
WHERE NOT EXISTS (
    SELECT DISTINCT t.company_id
	FROM transaction AS t
	WHERE c.id = t.company_id
);


-- Query principal con IN
SELECT c.company_name AS nombre_compañia_SIN_tracsacciones
FROM company AS c
WHERE id NOT IN (
    SELECT DISTINCT t.company_id
From transaction AS t
);


-- subquery secundaria
SELECT DISTINCT t.company_id
From transaction AS t;



-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  2 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- EJERCICIO 1.  *************** Identifica los cinco días que se generó la mayor cantidad de ingresos en la empresa por ventas. 
--                               Muestra la fecha de cada transacción junto con el total de las ventas. *******************************************************************

SELECT 
	DATE_FORMAT(t.timestamp, "%m-%d-%Y") AS fecha_dia, 
	ROUND(SUM(amount),2) AS total_ventas
FROM transaction AS t
WHERE t.declined = 0
GROUP BY DATE_FORMAT(t.timestamp, "%m-%d-%Y")
ORDER BY total_ventas DESC
LIMIT 5;


-- EJERCICIO 2.  *************** ¿Cuál es la media de ventas por país? Presenta los resultados ordenados de mayor a menor medio. *******************************************

SELECT c.country AS PAIS, ROUND(AVG(t.amount),2) AS ventas_medias
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
GROUP BY c.country
ORDER BY ventas_medias DESC;


-- EJERCICIO 3.  *************** En tu empresa, se plantea un nuevo proyecto para lanzar algunas campañas publicitarias para hacer competencia a la compañía “Non Institute”.
--                               Para ello, te piden la lista de todas las transacciones realizadas por empresas que están ubicadas en el mismo país que esta compañía. *********

-- EJERCICIO 3.1.  *** Muestra el listado aplicando JOIN y subconsultas. ***

-- Query principal
SELECT c.company_name, c.country, t.*
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
WHERE (c.country = (SELECT c.country
						FROM company AS c
						WHERE c.company_name = "Non Institute"))
	AND (c.company_name <> "Non Institute")
    AND (t.declined = 0)-- ENTIENDO QUE SOLO HAY QUE LISTAR LAS COMPAÑIAS COMPETENCIA Y POR ESO QUITO LA "Non Institute"
;

-- subquery secundaria
SELECT c.country
FROM company AS c
WHERE c.company_name = "Non Institute";


-- EJERCICIO 3.2.  *** Muestra el listado aplicando solo subconsultas. ***

-- Query principal
SELECT t.*
FROM transaction AS t
WHERE t.company_id IN (
					SELECT c.id
					FROM company AS c
					Where c.country = (
						SELECT c.country
						FROM company AS c
						WHERE c.company_name = "Non Institute")
AND (c.company_name <> "Non Institute")
AND (t.declined = 0)
);


-- subquery secundaria
SELECT c.id
FROM company AS c
Where c.country = (SELECT c.country
				FROM company AS c
				WHERE c.company_name = "Non Institute"
				)
AND (c.company_name <> "Non Institute");



-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  3 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************

-- EJERCICIO 1.  *************** Presenta el nombre, teléfono, país, fecha y amount, de aquellas empresas que realizaron transacciones con un valor comprendido entre 350 y 400 euros
--                               y en alguna de estas fechas: 29 de abril de 2015, 20 de julio de 2018 y 13 de marzo de 2024.
--                                 Ordena los resultados de mayor a menor cantidad. ****************************************************************************************

-- Usando IN
SELECT c.company_name, c.phone, c.country, DATE_FORMAT((t.timestamp),"%d-%m-%Y") AS Fecha, t.amount
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
WHERE t.amount BETWEEN 350 AND 400
AND (DATE(t.timestamp) IN ('2015-04-29', '2018-07-20', '2024-03-13'))
ORDER BY t.amount DESC;

-- Usando EXISTS
SELECT c.company_name, c.phone, c.country, DATE_FORMAT((t.timestamp),"%d-%m-%Y") AS Fecha, t.amount
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
WHERE t.amount BETWEEN 350 AND 400
AND EXISTS (
    SELECT 1
    FROM (
        SELECT '2015-04-29' AS fecha
        UNION ALL
        SELECT '2018-07-20'
        UNION ALL
        SELECT '2024-03-13'
    ) AS fechas
    WHERE fechas.fecha = DATE(t.timestamp)
)
ORDER BY t.amount DESC;

-- EJERCICIO 2.  *************** Necesitamos optimizar la asignación de los recursos y dependerá de la capacidad operativa que se requiera, 
--                               por lo que te piden la información sobre la cantidad de transacciones que realizan las empresas, pero el departamento de recursos humanos es exigente y 
--                               quiere un listado de las empresas en las que especifiques si tienen más de 400 transacciones o menos.. ***************************************************


SELECT c.company_name, COUNT(t.id) AS total_transacciones,
    CASE 
        WHEN COUNT(t.id) > 400 THEN 'Más de 400 transacciones'
        ELSE '400 o menos transacciones'
    END AS clasificacion
FROM company AS c
JOIN transaction AS t
ON c.id = t.company_id
GROUP BY c.company_name;


