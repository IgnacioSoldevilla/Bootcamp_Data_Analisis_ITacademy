Este directorio contendra 3 ficheros, en formato parquet, por cada empresa: df, train y validación
Para identificarlos, cada fichero se llamara: 
  "name_empresa"_"ticker_empresa"_df.parquet
  "name_empresa"_"ticker_empresa"_train.parquet
  "name_empresa"_"ticker_empresa"_validación.parquet

El fichero _df contiene datos tratados intermedios para obteer los resultados. 
El de train es el que se hace la busqueda de pautas y en el de validación en el que se probaran esas pautas
