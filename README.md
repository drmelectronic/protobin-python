# protobin

**protobin** es una biblioteca Python diseñada para facilitar la interacción con el formato de transferencia de datos Protobin en modo binario. Esta biblioteca proporciona una interfaz sencilla y eficiente para:

* **Serializar** objetos Python en datos Protobin.
* **Deserializar** datos Protobin en objetos Python.
* **Validar** la integridad de los datos Protobin.

## Instalación

Para instalar `protobin`, puedes utilizar pip:

```bash
pip install protobin
```

## Cómo empezar

### Primeros Pasos
Declare un protocolo de la siguiente forma:

```python
from protobin import Protocol
protocol = Protocol(js={'medida': [
        {'key': 'id', 'bytes': 1, 'type': 'unsigned'},
        {'key': 'nombre', 'type': 'string'},
        {'key': 'valor', 'bytes': 2, 'type': 'signed'}
    ]})
```

luego cree la variable que desea transmitir como un diccionario de python, codiféquela, decodifíquela, y compruebe que la información se recuperó correctamente 

```python
data = {'id': 2, 'nombre': 'Voltaje', 'valor': -20}
binary = protocol.encode(data, 'medida')
print('binary', binary)
recv = protocol.decode(binary, 'medida')
print('recv', recv)
```

### Archivo Json

El protocolo se declara en un archivo *.json o un objeto dict en python.
Éste contiene un diccionario donde cada clave del diccionario es el identificador de un formato.

```json
{
  "formato1": [{}, {}, {}],
  "formato2": [{}, {}]  
}
```

Cada formato se declara como una lista de campos, y cada campo es representado por un diccionario, que debe tener un **key** para identificar el dato que se almacenará en esa posición, también debe tener un **type** que define el tipo de dato que se guardará y opcionalmente **bytes** o **length** para definir la cantidad de espacio o datos que se guardarán.


### Tipos de Datos

**array** : Sirve para declarar listas de objetos, requiere el campo **array* que contiene un formato completo.

**bits** : Sirve para declarar una lista de valores booleanos como un arreglo de bits en la cantidad necesaria de bytes. Es opcional el campo **length** si se quiere fijar una cantidad de elementos y usar un byte menos en su codificación.

**bool** : Sirve para declarar un único valor booleano en un byte. No requiere campos adicionales, ocupa 1 byte.

**char** : Sirve para declarar un único valor booleano en un byte. No requiere campos adicionales, ocupa 1 byte.

**date** : Sirve para declarar un valor datetime.date. No requiere campos adicionales, ocupa 3 bytes.

**datetime** : Sirve para declarar un valor datetime.datetime con presicion de segundos. No requiere campos adicionales, ocupa 6 bytes.

**flags** : Sirve para declarar una lista de keys cuyos valores sean booleanos y representarlos en un arreglo de bits. No requiere campos adicionales.

**float** : Sirve para declarar un valor numérico con una precisión fija de decimales. Requiere el campo **bytes** y **decimales**, tamaño variable.

**signed** : Sirve para declarar un valor entero positivo. Requiere el campo **bytes**, tamaño variable.

**string** : Sirve para declarar un texto. Es opcional el campo **bytes**, tamaño variable.

**time** : Sirve para declarar un valor datetime.time con presicion de minutos. No requiere campos adicionales, ocupa 2 bytes.

**timestamp** : Sirve para declarar un valor datetime.datetime con presicion de microsegundos. No requiere campos adicionales, ocupa 8 bytes.

**unsigned** : Sirve para declarar un valor entero. Requiere el campo **bytes**, tamaño variable.
