# Creación de Usuarios IAM
En esta carpeta están los archivos necesarios para crear nuevos usuarios de manera automática en IAM. Se ha creado a partir de la 
información proporcionada en estas páginas de la Wiki: [Altas y Bajas de Usuarios](https://wikis.tid.es/na/index.php/Altas_y_bajas_de_usuarios)
y [Política de Roles y Accesos](https://wikis.tid.es/na/index.php/Política_de_roles_y_accesos).

Para ello, se tiene que ejecutar el job de Jenkins llamado *IAM_New_User_Registration*, que se encuentra dentro de la carpeta 
*Infrastructure*, y modificar su configuración. Lo vemos con este ejemplo:

```
python3 smtp.py --rol "Desarrollador" --casodeuso1 "PLEXT TOA" --casodeuso2 "PLEXT ASSIA" --pro --newuser Test.test  
$usuario $password --address ejemplo@telefonica.com
```
* **--rol** - Disponemos de las siguientes opciones:

      "Desarrollador global" - Se crea cuenta en dev.
      "Desarrollador" - Se crea cuenta en dev.
      "Desarrollador avanzado de Tableau" - Se crea cuenta en dev.
      "Responsable de area usuaria" - Se crea cuenta en pro si se solicita (se comenta más adelante).
      "Engineering" - Se crea cuenta en dev, pro, int y opt.
      "Engineering Manager" - Se crea cuenta en dev, pro, int y opt.
      
* **--casodeuso1**, **--casodeuso2** y **--casodeuso3**: Para los casos de *Desarrollador* y *Desarrollador Avanzado de Tableau*, se pueden
indicar un máximo de 3 casos de usos diferentes, para poder incluir dicho usuario al grupo correspondiente, además de los grupos asignados
a todos los usuarios creados, *BasicIAM* y *ForceMFA*:
      
      "PLEXT"
	    "PLEXT TOA"
	    "PLEXT ASSIA"
	    "PLEXT HADA"
	    "ASTRO"
	    "VIDEO Y PLATAFORMAS"
      
* **--pro** - Si se pide crear una cuenta en *pro*, se introduce únicamente este parámetro. Relevante especialmente para los casos de
*Desarrollador global*, *Desarrollador*, *Desarrollador Avanzado de Tableau* y *Responsable de area usuaria*
* **--newuser** - Se introduce el usuario a crear con la forma ***nombre***.***apellido***
* **$usuario y $password** - Credenciales para poder mandar emails.
* **--address** - En este parámetro se introduce la dirección de correo a la que se mandarán los emails de registro y de credenciales.
