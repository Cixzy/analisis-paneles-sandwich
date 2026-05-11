# Instrucciones — Analizador de ensayos de flexión a 3 puntos

## ¿Qué hace este programa?

Lee los datos que exporta la máquina universal, calcula propiedades mecánicas por geometría
(módulo elástico, energía absorbida, SEA, esfuerzo máximo) y genera 9 figuras listas para publicación
en la carpeta `figuras/`.

---

## Archivos necesarios (todos en esta carpeta)

| Archivo            | Descripción                                          |
|--------------------|------------------------------------------------------|
| `MaterialData.py`  | El programa — **no modificar**                       |
| `config.json`      | Aquí se indica qué CSV analizar y las dimensiones    |
| Tu archivo `.csv`  | El que exporta la máquina universal                  |

---

## Paso 1 — Preparar el config.json

Abre `config.json` con cualquier editor de texto (Notepad, VS Code, etc.).

Verás algo así:

```json
{
  "archivo_csv": "HEXAGONOS.csv",
  "geometrias": {
    "Carrito": {"h": 27.0, "b": 76.0, "L": 160},
    "Panal":   {"h": 32.0, "b": 209.0, "L": 160}
  }
}
```

Cambia:

1. **`"archivo_csv"`** → el nombre exacto de tu archivo CSV (incluyendo `.csv`)
2. **`"geometrias"`** → una entrada por cada geometría que quieras analizar, con sus dimensiones

### ¿De dónde saco h, b y L?

La máquina genera un **PDF de informe** junto al CSV. En la tabla de parámetros busca:

| Columna del PDF       | Campo en config.json | Descripción                  |
|-----------------------|----------------------|------------------------------|
| **Espesor**           | `"h"`                | Altura/espesor de la probeta (mm) |
| **Anchura**           | `"b"`                | Ancho de la probeta (mm)     |
| **Soporte_inferior**  | `"L"`                | Distancia entre apoyos (mm)  |

### Ejemplo con nuevas geometrías

```json
{
  "archivo_csv": "Ensayo_Junio2026.csv",
  "geometrias": {
    "Rombo":     {"h": 25.0, "b": 22.0, "L": 150},
    "Triangulo": {"h": 28.5, "b": 20.0, "L": 150},
    "Hexagono2": {"h": 24.0, "b": 21.0, "L": 100}
  }
}
```

> **Importante:** El nombre de cada geometría debe escribirse **exactamente igual** que aparece
> en la primera fila del CSV (respetando mayúsculas, números y guiones bajos).

---

## Paso 2 — Correr el programa

Abre una terminal en esta carpeta y escribe:

```
python MaterialData.py
```

Las figuras se guardan automáticamente en `figuras/`. La terminal también imprime una tabla
resumen con los valores numéricos de cada geometría.

---

## Agregar geometrías en el futuro

Solo añade una línea más en `"geometrias"` del config.json con el nombre y las tres dimensiones.
No necesitas modificar el código Python.

---

## Notas

- Si una geometría aparece en el CSV pero **no** en el config.json, el programa la omite
  y muestra un aviso en la terminal.
- El CSV debe tener el formato estándar de la máquina: 3 filas de encabezado
  (nombres / columnas / unidades) seguidas de los datos numéricos.
- Los valores decimales van con punto, no con coma: `25.146`, no `25,146`.
