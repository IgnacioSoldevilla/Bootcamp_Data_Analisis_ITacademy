
-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  1 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- Primero creo la nueva base de datos
CREATE DATABASE IF NOT EXISTS transactions_2;

-- Compruebo que se ha creado correctamente
SHOW DATABASES;

-- la seleccionamos para trabajar con ella
USE transactions_2;

-- Creo la tabla american_users
CREATE TABLE IF NOT EXISTS american_users (
	id VARCHAR(10) PRIMARY KEY,
	name VARCHAR(100),
	surname VARCHAR(100),
	phone VARCHAR(150),
	email VARCHAR(150),
	birth_date VARCHAR(100),
	country VARCHAR(150),
	city VARCHAR(150),
	postal_code VARCHAR(100),
	address VARCHAR(255)    
);

-- Creo la tabla european_users 
CREATE TABLE IF NOT EXISTS european_users (
	id VARCHAR(10) PRIMARY KEY,
	name VARCHAR(100),
	surname VARCHAR(100),
	phone VARCHAR(150),
	email VARCHAR(150),
	birth_date VARCHAR(100),
	country VARCHAR(150),
	city VARCHAR(150),
	postal_code VARCHAR(100),
	address VARCHAR(255)  
);

-- me aseguro que se han creado
SHOW TABLES;



-- Introduzco los datos del fichero american_users.csv que me da el ejercicio
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\american_users.csv'
	INTO TABLE american_users 
	FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;

-- Cuento las filas introducidas para comprobar que tiene las mismas que el csv que son 1010 sin contar la cabecera
SELECT FORMAT(COUNT(*),0) AS total_records
FROM american_users;

-- Introduzco los datos del fichero european_users.csv que me da el ejercicio
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\european_users.csv'
	INTO TABLE european_users
	FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;
-- Cuento las filas introducidas para comprobar que tiene las mismas que el csv que son 3990 sin contar la cabecera
SELECT FORMAT(COUNT(*),0) AS total_records
FROM european_users AS eu;


-- añado el campo continent
ALTER TABLE american_users ADD continent VARCHAR(150); 

-- compruebo que la columna continent esta vacia
SELECT au.*
FROM american_users AS au;

-- Cargo el valor american en la campo continent para todos los registros
UPDATE american_users 
SET continent = "american"
WHERE id <> "0";

-- compruebo que la columna continent ya tiene el valor american y esta en todos los registros (1010)
SELECT FORMAT(COUNT(au.continent),0) AS total_records_with_american
FROM american_users AS au;


-- ************************************************************************************************************************

-- añado el campo continent a la tabla european_users
ALTER TABLE european_users ADD continent VARCHAR(150); 

-- compruebo que la columna continent esta vacia
SELECT eu.*
FROM european_users AS eu;

-- Cargo el valor european en la campo continent para todos los registros
UPDATE european_users 
SET continent = "european"
WHERE id <> "0";

-- compruebo que la columna continent ya tiene el valor european y esta en todos los registros (3990)
SELECT FORMAT(COUNT(eu.continent),0) AS total_records_with_european
FROM european_users AS eu;


-- ******************** UNIR LAS 2 TABLAS EN UNA *****************************************************************************



-- Creo la tabla total_users de igual estructura que las anteriores
CREATE TABLE IF NOT EXISTS total_users (
	id VARCHAR(10) PRIMARY KEY,
	name VARCHAR(100),
	surname VARCHAR(100),
	phone VARCHAR(150),
	email VARCHAR(150),
	birth_date VARCHAR(100),
	country VARCHAR(150),
	city VARCHAR(150),
	postal_code VARCHAR(100),
	address VARCHAR(255),
    continent VARCHAR(150)
);

-- Copio todos los registros de las tablas european_users y american_users una vez comprobados que no se repiten los indices entre las 2 tablas (si se repitiese alguno daria error)
INSERT INTO total_users SELECT * FROM european_users;
INSERT INTO total_users SELECT * FROM american_users;

-- Verifico que se han introducido el total de registros 1010 + 3990 = 5000
SELECT tu.continent AS continent, FORMAT(COUNT(*),0) AS users
FROM total_users AS tu
GROUP BY tu.continent;




-- Creo la tabla companies
CREATE TABLE IF NOT EXISTS companies (
	company_id VARCHAR(15) PRIMARY KEY,
	company_name VARCHAR(255),
	phone VARCHAR(15),
	email VARCHAR(100),
	country VARCHAR(100),
	website VARCHAR(255)
);

-- Introduzco los datos del fichero companies.csv que me da el ejercicio
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\companies.csv'
	INTO TABLE companies 
	FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;

-- Cuento las filas introducidas para comprobar que tiene las mismas que el csv que son 100 sin contar la cabecera
SELECT COUNT(*) AS total_records
FROM companies;


-- Creamos la tabla credit_cards
    CREATE TABLE IF NOT EXISTS credit_cards (
        id VARCHAR(20) PRIMARY KEY,
        user_id  VARCHAR(15),
        iban VARCHAR(50),
        pan VARCHAR(50),
        pin VARCHAR(4),
        cvv VARCHAR(4),
        track1 VARCHAR(100),
        track2 VARCHAR(100),
        expiring_date VARCHAR(20)
    );

-- Introduzco los datos del fichero credit_cards.csv que me da el ejercicio
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\credit_cards.csv'
	INTO TABLE credit_cards 
	FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;

-- Cuento las filas introducidas para comprobar que tiene las mismas que el csv que son 5000 sin contar la cabecera
SELECT FORMAT(COUNT(*),0) AS total_records
FROM credit_cards;



-- Creamos la tabla transactions
    CREATE TABLE IF NOT EXISTS transactions (
        id VARCHAR(255) PRIMARY KEY,
        card_id VARCHAR(20),
        business_id VARCHAR(15), 
        timestamp TIMESTAMP,
        amount DECIMAL(10, 2),
        declined BOOLEAN,
        product_ids VARCHAR(50),
        user_id VARCHAR(10),
        lat VARCHAR(30),
        longitude VARCHAR(30),
		FOREIGN KEY (card_id) REFERENCES credit_cards(id),
		FOREIGN KEY (business_id) REFERENCES companies(company_id),
		FOREIGN KEY (user_id) REFERENCES total_users(id)
    );

-- Introduzco los datos del fichero transactions.csv que me da el ejercicio. OJO que los datos estan separados por ; en vez de por ,
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\transactions.csv'
	INTO TABLE transactions 
	FIELDS TERMINATED BY ';'
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;

-- Cuento las filas introducidas para comprobar que tiene las mismas que el csv que son 100,000 sin contar la cabecera
SELECT FORMAT(COUNT(*),0) AS total_records
FROM transactions;


-- Voy a borrar las tablas `american_users` y `european_users` pq ya solo utilizaré la tabla `total_users`:

DROP TABLE IF EXISTS european_users;
DESCRIBE european_users;


DROP TABLE IF EXISTS american_users;
DESCRIBE american_users;






-- EJERCICIO 1.  *************** Realiza una subconsulta que muestre a todos los usuarios con más de 80 transacciones utilizando al menos 2 tablas. **********************************************************

-- Respuesta 1.1: Usando Subconsulta NO correlacionada pero no me visualiza los transactions_number de cada user
SELECT 
  tu.id AS user_id,
  tu.name,
  tu.surname
FROM total_users AS tu
WHERE EXISTS (
  SELECT t.user_id
  FROM transactions AS t
  WHERE tu.id = t.user_id
  GROUP BY t.user_id
  HAVING COUNT(*) > 80);




-- Respuesta 1.2: Usando Subconsulta correlacionada para que me visualice tambien transactions_number
SELECT tu.id AS user_id, tu.name, tu.surname,
  (
    SELECT COUNT(*) 
    FROM transactions t 
    WHERE t.user_id = tu.id
  ) AS transactions_number
FROM total_users AS tu
WHERE (
    SELECT COUNT(*) 
    FROM transactions t 
    WHERE t.user_id = tu.id
) > 80
ORDER BY transactions_number DESC;
;





-- Respuesta 2: Usando JOIN
SELECT tu.id AS user_id , tu.name AS name, tu.surname AS surname, COUNT(t.user_id) AS transactions_number
FROM total_users AS tu
JOIN transactions AS t
ON tu.id = t.user_id
GROUP BY user_id
HAVING transactions_number > 80
ORDER BY transactions_number DESC
;


-- EJERCICIO 2.  *************** Muestra la media de amount por IBAN de las tarjetas de crédito en la compañía Donec Ltd., utiliza por lo menos 2 tablas. **********************************************************


SELECT c.company_name AS company_name, cc.iban AS iban, ROUND(AVG(t.amount),2) AS average_amount
FROM credit_cards AS cc
JOIN transactions AS t
ON cc.id = t.card_id
JOIN companies AS c
ON t.business_id = c.company_id
GROUP BY company_name, iban
HAVING company_name = "Donec Ltd"
ORDER BY average_amount DESC   
;







-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  2 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- SOLUCION del creado de la nueva tabla que la voy a llamar credit_state

-- Creo la estructura de la tabla
CREATE TABLE IF NOT EXISTS credit_state(
	card_id VARCHAR(20) PRIMARY KEY,
    card_state VARCHAR(10)
);


-- compruebo que se ha creado correctamente y esta vacia
SELECT *
FROM credit_state AS CS;


-- cargo los datos
INSERT INTO credit_state (
						SELECT sbn.card_id,
						CASE
								WHEN sbn.sum_3_last = 3 THEN "inactive"
								ELSE "active"
						END AS state
						FROM (
							SELECT rnk.card_id, SUM(rnk.declined) AS sum_3_last
							FROM (SELECT
									t.card_id,
									t.timestamp,
									t.declined,
									ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY timestamp DESC) AS rn
								FROM transactions AS t
								) AS rnk
							WHERE rnk.rn <= 3
							GROUP BY rnk.card_id
							ORDER BY rnk.card_id DESC
						) AS sbn
)
;

-- compruebo que se han cargado los datos. Debe haber 5.000 filas
SELECT *
FROM credit_state AS CS;




-- ____________PARA LLEGAR AL SELECT UTILIZADO EN LA SENTENCIA ANTERIOR, A CONTINUACIÓN LO VOY CALCULANDO PASO A PASO _______________

-- SOLUCION FINAL del QUERY ---
SELECT sbn.card_id,
CASE
		WHEN sbn.sum_3_last = 3 THEN "inactive"
		ELSE "active"
END AS state
FROM (
	SELECT rnk.card_id, SUM(rnk.declined) AS sum_3_last
	FROM (SELECT
			t.card_id,
			t.timestamp,
			t.declined,
			ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY timestamp DESC) AS rn
		FROM transactions AS t
		) AS rnk
	WHERE rnk.rn <= 3
	GROUP BY rnk.card_id
	ORDER BY rnk.card_id DESC
) AS sbn
;




-- ****************** Voy a llegar a la solucion final por pasos consecutivos  *******************************

-- 1.- Funcion ventana para poner un numero de columna por particion de identidad de tarjeta y ordenadas descendente por fecha
    SELECT
        t.card_id,
        t.timestamp,
        t.declined,
        ROW_NUMBER() OVER (PARTITION BY t.card_id ORDER BY t.timestamp DESC) AS rn
    FROM transactions AS t;


-- 2.- Añadir que solo salgan las 3 posiciones primeras que seran las 3 fechas más actuales
SELECT *
FROM (SELECT
        t.card_id,
        t.timestamp,
        t.declined,
        ROW_NUMBER() OVER (PARTITION BY t.card_id ORDER BY t.timestamp DESC) AS rn
    FROM transactions AS t
	) AS rnk
WHERE rnk.rn <= 3;

-- 3.- hago la suma de los 3 declined de cada grupo y si da 3 es inactiva y en caso contrario es activa

SELECT rnk.card_id, SUM(rnk.declined) AS sum_3_last
FROM (SELECT
        t.card_id,
        t.timestamp,
        t.declined,
        ROW_NUMBER() OVER (PARTITION BY t.card_id ORDER BY t.timestamp DESC) AS rn
    FROM transactions AS t
	) AS rnk
WHERE rn <= 3
GROUP BY rnk.card_id
ORDER BY rnk.card_id DESC
;

-- 4.- añado la columna de estado
SELECT sbn.card_id, sbn.sum_3_last,
CASE
		WHEN sbn.sum_3_last = 3 THEN "inactive"
		ELSE "active"
END AS state
FROM (
	SELECT rnk.card_id, SUM(rnk.declined) AS sum_3_last
	FROM (SELECT
			t.card_id,
			t.timestamp,
			t.declined,
			ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY timestamp DESC) AS rn
		FROM transactions AS t
		) AS rnk
	WHERE rnk.rn <= 3
	GROUP BY rnk.card_id
	ORDER BY rnk.card_id DESC
) AS sbn
;




-- EJERCICIO 1.  *************** ¿Cuántas tarjetas están activas? **********************************************************

SELECT cs.card_state, COUNT(cs.card_state) AS quantity
FROM credit_state AS cs
GROUP BY cs.card_state
HAVING cs.card_state = "active"
;






-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  3 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- Crea una tabla con la que podamos unir los datos del nuevo archivo products.csv con la base de datos creada, -----------
-- teniendo en cuenta que desde transaction tienes product_ids. Genera la siguiente consulta: -----------------------------




-- Creo la tabla products
CREATE TABLE IF NOT EXISTS products (
	id INT PRIMARY KEY,
	product_name VARCHAR(100),
	price VARCHAR(10),
    colour VARCHAR(15),
    weight VARCHAR(10),
    warehouse_id VARCHAR(10)
);


-- Introduzco los datos del fichero products.csv que me da el ejercicio
LOAD DATA
	INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\products.csv'
	INTO TABLE products 
	FIELDS TERMINATED BY ','
	ENCLOSED BY '"'
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
;


SELECT *
FROM products;


-- Creo la tabla intermedia para la relacion N:M llamada transactions_products
CREATE TABLE IF NOT EXISTS transactions_products (
	id_transactions_products INT AUTO_INCREMENT PRIMARY KEY,
	id_transaction VARCHAR(255),
	id_product INT,
    FOREIGN KEY(id_product) REFERENCES products(id),
    FOREIGN KEY(id_transaction) REFERENCES transactions(id)
);


SELECT *
FROM transactions_products;



-- pasar el campo product_ids de la tabla transactions a alamcenado como JSON
INSERT INTO transactions_products (id_transaction, id_product)   -- inserta los 2 campos en la tabla `transactions_products`
SELECT
  t.id AS id_transaction,  -- el indice de la tabla transactions sera el mismo que pondre en la tabla `transactions_products` en el campo id_transaction
  CAST(j.id_product AS UNSIGNED) AS id_product    -- convierte el valor formato texto en formato INT sin signo, eliminando los espacios y asigna alias id_product
FROM transactions AS t
JOIN JSON_TABLE(             -- genera una fila por cada valor
  CONCAT(
    '["', REPLACE(t.product_ids, ',', '","'), '"]'   -- pongo cada valor de product_ids en formato de 75,73, 98 a  '["75"," 73","78"]'
  ),
  '$[*]' COLUMNS (id_product VARCHAR(10) PATH '$')    -- Recorre todos los elementos JSON y crea una fila por cada uno
) AS j;



-- Compruebo que la tabla “transactions_products” Ahora ya tiene registros
SELECT *
FROM transactions_products;


-- Compruebo que se ha trasformado bien un indice concreto de la tabla "transactions"
SELECT *
FROM transactions
WHERE id = "29322BF7-84F4-4A6C-9FFC-C60B6BBD8DCD";

-- Compruebo que se ha trasformado bien un indice concreto de la tabla "transactions" en la "transactions_products
SELECT *
FROM transactions_products
WHERE id_transaction = "29322BF7-84F4-4A6C-9FFC-C60B6BBD8DCD";





-- EJERCICIO 1.  *************** Necesitamos conocer el número de veces que se ha vendido cada producto **********************************************************

-- Contar las unidades vendidas de cada producto
SELECT p.product_name AS product_name, tp.id_product AS product_id, FORMAT(COUNT(tp.id_product),0) AS units_sold
FROM transactions_products AS tp
JOIN products AS p
ON tp.id_product = p.id
GROUP BY product_name, product_id
ORDER BY units_sold DESC
;




