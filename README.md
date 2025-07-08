# Bot de Discord para Gestión de Personajes de Rol

## Descripción General

Este bot de Discord está diseñado para gestionar personajes de rol (DyD) utilizando una base de datos MongoDB. Permite a los usuarios crear, editar, visualizar y eliminar personajes y sus atributos directamente desde Discord. Además, incluye una API REST básica para acceder a los datos de los personajes.

## Características Principales

- **Gestión completa de personajes**: Crear, editar, visualizar y eliminar personajes
- **Sistema de atributos anidados**: Soporte para atributos complejos con estructura de objetos
- **Persistencia de datos**: Almacenamiento en MongoDB
- **API REST**: Endpoint para consultar personajes vía HTTP
- **Interfaz Discord**: Comandos intuitivos con prefijo `!`

## Tecnologías Utilizadas

- **Discord.py**: Biblioteca para interactuar con la API de Discord
- **MongoDB**: Base de datos NoSQL para almacenamiento de personajes
- **Flask**: Framework web para la API REST
- **Python-dotenv**: Gestión de variables de entorno
- **Threading**: Ejecución concurrente del bot y la API

## Configuración

### Variables de Entorno

El programa requiere las siguientes variables de entorno en un archivo `.env`:

```env
TOKEN=tu_token_de_discord_bot
MONGO_URI=mongodb://tu_uri_de_mongodb
```

### Dependencias

```bash
pip install discord.py flask pymongo python-dotenv
```

## Comandos Disponibles

### `!status`
Verifica el estado de conexión del bot.

**Uso:**
```
!status
```

**Respuesta:**
- "El bot está en línea." (si está conectado)
- "El bot está conectando..." (si está iniciando)

### `!crear <nombre>`
Crea un nuevo personaje con el nombre especificado.

**Parámetros:**
- `nombre`: Nombre del personaje a crear

**Ejemplo:**
```
!crear Aragorn
```

### `!añadir <nombre> <nombre_atributo> <tipo_atributo>`
Añade un nuevo atributo a un personaje existente.

**Parámetros:**
- `nombre`: Nombre del personaje
- `nombre_atributo`: Nombre del atributo (soporta notación de puntos para atributos anidados)
- `tipo_atributo`: Tipo de atributo (`str` para cadena, `obj` para objeto)

**Ejemplos:**
```
!añadir Aragorn clase str
!añadir Aragorn estadisticas obj
!añadir Aragorn estadisticas.fuerza str
```

### `!ver <nombre> [nombre_atributo]`
Visualiza un personaje completo o un atributo específico.

**Parámetros:**
- `nombre`: Nombre del personaje
- `nombre_atributo` (opcional): Atributo específico a visualizar

**Ejemplos:**
```
!ver Aragorn
!ver Aragorn clase
!ver Aragorn estadisticas.fuerza
```

### `!editar <nombre> <nombre_atributo> <nuevo_valor>`
Edita el valor de un atributo existente.

**Parámetros:**
- `nombre`: Nombre del personaje
- `nombre_atributo`: Nombre del atributo a editar
- `nuevo_valor`: Nuevo valor para el atributo

**Ejemplo:**
```
!editar Aragorn clase Guerrero
!editar Aragorn estadisticas.fuerza 18
```

### `!borrar <nombre> [nombre_atributo]`
Elimina un personaje completo o un atributo específico.

**Parámetros:**
- `nombre`: Nombre del personaje
- `nombre_atributo` (opcional): Atributo específico a eliminar

**Ejemplos:**
```
!borrar Aragorn estadisticas.fuerza
!borrar Aragorn
```

### `!verTodos`
Muestra todos los personajes y sus atributos.

**Uso:**
```
!verTodos
```

## API REST

### Endpoint: `GET /`
Retorna todos los personajes en formato JSON.

**Respuesta exitosa (200):**
```json
[
  {
    "id": "Aragorn",
    "atributos": {
      "nombre": "Aragorn",
      "clase": "Guerrero",
      "estadisticas": {
        "fuerza": "18"
      }
    }
  }
]
```

**Respuesta de error (500):**
```json
{
  "error": "Descripción del error"
}
```

## Estructura de Datos

Los personajes se almacenan en MongoDB con la siguiente estructura:

```json
{
  "_id": "ObjectId_generado_por_mongo",
  "nombre": "nombre_del_personaje",
  "atributo1": "valor1",
  "atributo2": {
    "sub_atributo": "valor"
  }
}
```

### Componentes Principales

1. **Bot de Discord**: Maneja los comandos y la interacción con usuarios
2. **Base de Datos MongoDB**: Almacena los datos de personajes
3. **API Flask**: Proporciona acceso REST a los datos
4. **Sistema de Threading**: Permite ejecutar el bot y la API simultáneamente

### Flujo de Datos

1. Usuario ejecuta comando en Discord
2. Bot procesa el comando
3. Bot interactúa con MongoDB
4. Bot envía respuesta al usuario
5. API Flask puede consultar los mismos datos independientemente

## Manejo de Errores

El sistema incluye manejo de errores para:
- Personajes inexistentes
- Atributos inexistentes
- Tipos de atributos inválidos
- Errores de conexión a la base de datos
- Errores de acceso a atributos anidados

## Limitaciones

- Solo soporta tipos de atributos `str` y `obj`
- No incluye autenticación o autorización
- La API REST es de solo lectura
- No hay validación de datos de entrada avanzada

## Instalación y Ejecución

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Configura las variables de entorno en `.env`
4. Ejecuta el programa: `python bot.py`

El bot se conectará a Discord y la API estará disponible en `http://localhost:5000`
