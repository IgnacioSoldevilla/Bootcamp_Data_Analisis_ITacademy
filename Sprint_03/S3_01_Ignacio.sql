
-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  1 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************

-- Añadir la estructura de la tabla `user` y cargar sus datos ejecutando los ficheros sql que me proporciona el ejercicio

-- Para crear una relacion PK - FK ambos deben ser del mismo tipo y el campo user(id) es CHAR(10) y el transaction(user_id) es INT
-- Voy a cambiar en la tabla user el user(id) de CHAR(10) a INT

ALTER TABLE user 
MODIFY COLUMN id INT;

-- Añado la relacion entre la tabla user (id) con la tabla transaction (user_id) creando una FK en la tabla transaction
	ALTER TABLE transaction 
	ADD CONSTRAINT fk_transaction_user 
	FOREIGN KEY (user_id) 
	REFERENCES user(id);



-- EJERCICIO 1.  *************** Tu tarea es diseñar y crear una tabla llamada "credit_card" que almacene detalles cruciales sobre las tarjetas de crédito.
--                               La nueva tabla debe ser capaz de identificar de forma única cada tarjeta y establecer una relación adecuada con las otras dos tablas ("transaction" y "company").
--                               Después de crear la tabla será necesario que ingreses la información del documento denominado "datos_introducir_credit".
--                               Recuerda mostrar el diagrama y realizar una breve descripción del mismo *************************************************************************************************

USE transactions;

-- Creamos la tabla credit_card
    CREATE TABLE IF NOT EXISTS credit_card (
        id VARCHAR(20) PRIMARY KEY,
        iban VARCHAR(50),
        pan VARCHAR(50),
        pin VARCHAR(4),
        cvv INT,
        expiring_date VARCHAR(20)
    );
    
   
-- Modifico la columna cvv de tipo INT a tipo VARCHAR(4) para que si un CVV empieza por 0 se almacene ese cero. En los INT los ceros por la izquierda no se almacenan.
-- Hubiese sido mejor hacerlo en la definición de la tabla, pero com ya la tengo definida, le cambio el tipo
ALTER TABLE credit_card
MODIFY COLUMN cvv VARCHAR(4);

   -- compruebo que estan correctamente creadas 
    SHOW TABLES;
    SHOW COLUMNS FROM credit_card;

-- cargo los datos de la tabla con el fichero facilitado en el ejercicio

-- Añado la relacion entre la tabla credit_card (id) con la tabla transaction (credit_card_id) creando una FK en la tabla transaction
	ALTER TABLE transaction 
	ADD CONSTRAINT fk_transaction_credit_card 
	FOREIGN KEY (credit_card_id) 
	REFERENCES credit_card(id);





-- EJERCICIO 2.  *************** El departamento de Recursos Humanos ha identificado un error en el número de cuenta asociado a su tarjeta de crédito con ID CcU-2938.
--                               La información que debe mostrarse para este registro es: TR323456312213576817699999.
--                               Recuerda mostrar que el cambio se realizó. ******************************************************************************************************************


-- Visualizo los datos originales de este ID
SELECT *
FROM credit_card
WHERE id = "CcU-2938"
;

-- Los datos originales son:
-- 	# id,      iban,                          pan,               pin,    cvv,   expiring_date
-- 'CcU-2938', 'TR301950312213576817638661', '5424465566813633', '3257', '984', '10/30/22'

-- Modifico los datos del registro con ID= "CcU-2938" para el nuevo valor de iban
UPDATE credit_card
SET iban = "TR323456312213576817699999"
WHERE id = "CcU-2938"
;

-- Visualizo los datos despues del cambio de este ID
SELECT *
FROM credit_card
WHERE id = "CcU-2938"
;



-- EJERCICIO 3.  *************** En la tabla "transaction" ingresa una nueva transacción con la siguiente información: 
--                                Id	108B1D1D-5B23-A76C-55EF-C568E49A99DD
--                                credit_card_id	CcU-9999
--                                company_id	b-9999
--                                user_id	9999
--                                lato	829.999
--                                longitud	-117.999
--                                amunt	111.11
--                                declined	0     *********************************************************************************************************************************

-- Compruebo que no exista un registro con el ID = 108B1D1D-5B23-A76C-55EF-C568E49A99D nuevo a crear
SELECT *
FROM transaction
WHERE id = "108B1D1D-5B23-A76C-55EF-C568E49A99D";

-- Compruebo que exista el 'credit_card_id' que voy a añadir en la tabla credit_card
SELECT *
FROM credit_card
WHERE id = "CcU-9999";

-- Como no existe, lo creo
INSERT INTO credit_card (id)
VALUE ("CcU-9999");

-- Compruebo que se ha creado el 'credit_card_id' que voy a añadir en la tabla credit_card
SELECT *
FROM credit_card
WHERE id = "CcU-9999";


-- Compruebo que exista el 'company_id' que voy a añadir en la tabla company
SELECT *
FROM company
WHERE id = "b-9999";

-- Como no existe, lo creo
INSERT INTO company (id)
VALUE ("b-9999");

-- Compruebo que se ha creado el 'company_id' que voy a añadir en la tabla company
SELECT *
FROM company
WHERE id = "b-9999";


-- Compruebo que exista el 'user_id' que voy a añadir en la tabla user
SELECT *
FROM user
WHERE id = "9999";

-- Como no existe, lo creo
INSERT INTO user (id)
VALUE ("9999");

-- Compruebo que se ha creado el 'user_id' que voy a añadir en la tabla user
SELECT *
FROM user
WHERE id = "9999";


-- Añado el registro a la tabla transaction con los datos ya definidos
INSERT INTO transaction (id, credit_card_id, company_id, user_id, lat, longitude, amount, declined) 
VALUES ('108B1D1D-5B23-A76C-55EF-C568E49A99D', 'CcU-9999', 'b-9999', '9999', '829.999', '-117.999', '111.11','0');

-- Compruebo que se ha creado correctamente
SELECT *
FROM transaction
WHERE id = "108B1D1D-5B23-A76C-55EF-C568E49A99D";



-- EJERCICIO 4.  *************** Desde recursos humanos te solicitan eliminar la columna "pan" de la tabla credit_card. Recuerda mostrar el cambio realizado.. *****************************

-- Visualizo las columnas de la tabla para comprobar que existe la columna "pan"
SHOW COLUMNS FROM credit_card;

-- Borrado de columna pan
ALTER TABLE credit_card DROP COLUMN pan;

-- Visualizo las columnas de la tabla para comprobar que ya NO existe la columna "pan"
SHOW COLUMNS FROM credit_card;




-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  2 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************


-- EJERCICIO 1.  *************** Elimina de la tabla transacción el registro con ID 000447FE-B650-4DCF-85DE-C7ED0EE1CAAD de la base de datos. **************************************************

-- Primero lo visualizo para asegurarme que esta
SELECT *
FROM transaction
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";

-- Elimino el registro
DELETE FROM transaction
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";

-- Compruebo que ya no exister para asegurarme que se ha borrado
SELECT *
FROM transaction
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";


-- EJERCICIO 2.  *************** La sección de marketing desea tener acceso a información específica para realizar análisis y estrategias efectivas.
--                               Se ha solicitado crear una vista que proporcione detalles clave sobre las compañías y sus transacciones.
--                               Será necesaria que crees una vista llamada VistaMarketing que contenga la siguiente información:
--                               Nombre de la compañía. Teléfono de contacto. País de residencia. Media de compra realizado por cada compañía.
--                               Presenta la vista creada, ordenando los datos de mayor a menor promedio de compra.. *****************************************************************************


-- Creo la vista probando la consulta primero y luego la pongo en la vista. 
-- Entiendo que la ordenacion descendente NO tiene que estar incluida en la vista
CREATE VIEW VistaMarketing AS
	SELECT 
		c.company_name AS compañia, 
		c.phone AS telefono_contacto, 
		c.country AS pais_residencia, 
		ROUND(AVG(t.amount),2) AS media_compras
	FROM company AS c
	JOIN transaction AS t
	ON c.id = t.company_id
	GROUP BY compañia, telefono_contacto, pais_residencia
;

-- visualizo la lista de vistas para ver que esta creada
SHOW FULL TABLES IN transactions WHERE TABLE_TYPE = 'VIEW';

-- pruebo que funciona la llamada
SELECT *
FROM vistamarketing
ORDER BY media_compras DESC;


-- EJERCICIO 3.  *************** Filtra la vista VistaMarketing para mostrar sólo las compañías que tienen su país de residencia en "Germany". *****************************************

SELECT *
FROM vistamarketing
WHERE pais_residencia = "Germany"
;





-- ************************************************************************************************************************************************************************
-- ******************************************* N I V E L  3 ***************************************************************************************************************
-- ************************************************************************************************************************************************************************

-- EJERCICIO 1.  *************** Todo explicado en el fichero pdf del sprint 03 y solo faltaria ejecutar el añadir el campo "fecha_actual" del tipo DATE en la tabla "credit_card" ******************************

-- Visualizo los campos de la tabla antes de añadir el nuevo campo
DESCRIBE credit_card;

-- Añado el nuevo campo o columna
ALTER TABLE credit_card ADD fecha_actual DATE;

-- Visualizo los campos de la tabla para comprobar que se ha añadido el nuevo campo
DESCRIBE credit_card;


-- EJERCICIO 2.  *************** La empresa también le pide crear una vista llamada "InformeTecnico" que contenga la siguiente información:
--                                 ID de la transacción
--                                 Nombre del usuario/a
--                                 Apellido del usuario/a
--                                 IBAN de la tarjeta de crédito usada.
--                                 Nombre de la compañía de la transacción realizada.
--                               Asegúrese de incluir información relevante de las tablas que conocerá y utilice alias para cambiar de nombre columnas según sea necesario.
--                               Muestra los resultados de la vista, ordena los resultados de forma descendente en función de la variable ID de transacción. **************************************************



-- visualizo la lista de vistas para ver que NO esta creada la vista InformeTecnico
SHOW FULL TABLES IN transactions WHERE TABLE_TYPE = 'VIEW';

-- Creo la vista probando la consulta primero y luego la pongo en la vista. 
-- Entiendo que la ordenacion descendente NO tiene que estar incluida en la vista
CREATE VIEW InformeTecnico AS
	SELECT 
		t.id AS id_transaccion,
		u.name AS nombre_usuario, 
		u.surname AS apellido_usuario,
		cc.iban AS iban_tarjeta,
		c.company_name AS compañia,
        u.city AS ciudad,
        u.country AS pais
	FROM transaction AS t
	JOIN user AS u
	ON t.user_id = u.id
	JOIN credit_card AS cc
	ON t.credit_card_id = cc.id
	JOIN company AS c
	ON t.company_id = c.id
;

-- visualizo la lista de vistas para ver que SI esta creada la vista InformeTecnico
SHOW FULL TABLES IN transactions WHERE TABLE_TYPE = 'VIEW';


-- pruebo que funciona la llamada y que la ordena descendente por el id de la tabla transaction
SELECT *
FROM informetecnico
ORDER BY id_transaccion DESC;



