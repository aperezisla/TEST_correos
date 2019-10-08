# Creación de Usuarios IAM
En esta carpeta están los archivos necesarios para crear nuevos usuarios de manera automática en IAM. Se ha creado a partir de la 
información proporcionada en estas páginas de la Wiki: [Altas y Bajas de Usuarios](https://wikis.tid.es/na/index.php/Altas_y_bajas_de_usuarios)
y [Política de Roles y Accesos](https://wikis.tid.es/na/index.php/Política_de_roles_y_accesos).

Para ello, se tiene que ejecutar con parámetros el job de Jenkins llamado *IAM_New_User_Registration*, que se encuentra dentro de la carpeta 
*Infrastructure*. Los parámetros son los siguientes:

* **rol** - Disponemos de las siguientes opciones:

      Desarrollador_Global - Se crea cuenta en dev.
      Desarrollador - Se crea cuenta en dev.
      Desarrollador_Avanzado_De_Tableau - Se crea cuenta en dev.
      Responsable_De_Area_Usuaria - Se crea cuenta en pro si se solicita (se comenta más adelante).
      Engineering - Se crea cuenta en dev, pro, int y opt.
      Engineering_Manager - Se crea cuenta en dev, pro, int y opt.
      
* **casodeuso1**, **casodeuso2** y **casodeuso3**: Para los casos de *Desarrollador* y *Desarrollador Avanzado de Tableau*, se pueden
indicar un máximo de 3 casos de usos diferentes, para poder incluir dicho usuario al grupo correspondiente, además de los grupos asignados
a todos los usuarios creados, *BasicIAM* y *ForceMFA*. Si no hay que indicar caso de uso, indicar un No.
      
      
      "PLEXT"
      "PLEXT_TOA"
      "PLEXT_ASSIA"
      "PLEXT_HADA"
      "ASTRO"
      "VIDEO_Y_PLATAFORMAS"
      
* **pro** - Si se pide crear una cuenta en *pro*, se introduce únicamente este parámetro. Relevante especialmente para los casos de
*Desarrollador global*, *Desarrollador*, *Desarrollador Avanzado de Tableau* y *Responsable de area usuaria*
* **newuser** - Se introduce el usuario a crear con la forma ***nombre***.***apellido***
* **$usuario y $password** - Credenciales para poder mandar emails.
* **address** - En este parámetro se introduce la dirección de correo a la que se mandarán los emails de registro y de credenciales.
