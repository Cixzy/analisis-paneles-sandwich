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

## Cuando hagas una nueva prueba

Sigue estos pasos cada vez que tengas datos de un ensayo nuevo:

**1.** Copia el CSV que exportó la máquina a la misma carpeta que `MaterialData.py`

**2.** Abre `config.json` con cualquier editor de texto y cambia:

- `"archivo_csv"` → el nombre exacto de tu nuevo CSV
- `"geometrias"` → los nombres y dimensiones de las geometrías nuevas

Los valores `h`, `b` y `L` los encuentras en el **PDF de informe** que genera la máquina:

| PDF          | config.json |
|--------------|-------------|
| Espesor      | `h`         |
| Anchura      | `b`         |
| Soporte_inferior | `L`     |

**Ejemplo:**
```json
{
  "archivo_csv": "Ensayo_Octubre2026.csv",
  "geometrias": {
    "Rombo":     {"h": 25.0, "b": 22.0, "L": 150},
    "Triangulo": {"h": 28.5, "b": 20.0, "L": 150},
    "Estrella":  {"h": 24.0, "b": 21.0, "L": 100}
  }
}
```

**3.** Corre el programa:
```
python MaterialData.py
```

Las figuras se guardan en `figuras/` y se sobreescriben si ya existían.

> Si una geometría está en el CSV pero no en el config.json, el programa la omite con un aviso.
> Si quieres analizar varias pruebas distintas, guarda una copia del config.json por cada ensayo.

### Analizar solo algunas geometrías

Pon únicamente las que te interesen en `"geometrias"`. Las demás se omiten automáticamente.

### Comparar geometrías de dos sesiones distintas

La máquina genera un CSV por sesión. Para compararlas juntas, primero únelas en Excel:

1. Abre ambos CSV en Excel
2. Copia todas las columnas del segundo CSV y pégalas **a la derecha** del primero
   (respetando el formato: fila 1 = nombres, fila 2 = columnas, fila 3 = unidades)
3. Guarda como nuevo CSV, por ejemplo `Comparacion.csv`
4. En `config.json` pon el nombre del archivo nuevo y las dimensiones de **todas** las geometrías incluidas

El programa no distingue de qué sesión vienen los datos — solo necesita que estén en el mismo archivo con el formato correcto.

---

## Actualizar el repositorio de GitHub

Cada vez que modifiques algo (el código, el config.json, etc.) tienes que subir los cambios
manualmente con estos 3 comandos en la terminal, **en este orden**:

**1. Registrar qué archivos cambiaron:**
```
git add .
```

**2. Guardar los cambios con una descripción:**
```
git commit -m "descripción breve de lo que cambiaste"
```

**3. Subir a GitHub:**

Primero pon tu token en la URL (reemplaza `TU_TOKEN`):
```
git remote set-url origin https://Cixzy:TU_TOKEN@github.com/Cixzy/analisis-paneles-sandwich.git
```
Luego sube:
```
git push
```
Y después borra el token de la URL:
```
git remote set-url origin https://github.com/Cixzy/analisis-paneles-sandwich.git
```

> El token lo generas en github.com → foto de perfil → Settings → Developer settings →
> Personal access tokens → Tokens (classic) → Generate new token (classic).
> Marca solo la casilla **repo** y cópialo antes de cerrar la página.

---

## Notas

- Si una geometría aparece en el CSV pero **no** en el config.json, el programa la omite
  y muestra un aviso en la terminal.
- El CSV debe tener el formato estándar de la máquina: 3 filas de encabezado
  (nombres / columnas / unidades) seguidas de los datos numéricos.
- Los valores decimales van con punto, no con coma: `25.146`, no `25,146`.
