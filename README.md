# 📊 Dashboard de Ventas de la Empresa

Dashboard interactivo de análisis de ventas construido con **Panel**, **Pandas** y **Matplotlib**. Permite explorar la evolución mensual de las ventas, comparar el rendimiento entre ciudades y analizar la distribución por categoría de producto, todo desde una interfaz web responsive con filtros dinámicos.

🔗 **Demo en vivo:** [https://juliososaang.github.io/analisis_ventas/app.html](https://juliososaang.github.io/analisis_ventas/app.html)

---

## ✨ Características

- **Tres vistas interactivas** organizadas en pestañas:
  - **Ventas Mensuales:** evolución de las ventas mes a mes con gráfico de burbujas y línea de tendencia.
  - **Ventas por Ciudad:** ranking de ciudades por total de ventas, con modo de comparación directa entre dos ciudades.
  - **Ventas por Categoría:** distribución de ventas por categoría de producto, filtrable por rango de meses, ciudades y categorías.
- **Sidebar dinámico:** los filtros cambian automáticamente según la pestaña activa.
- **Diseño responsive:** los gráficos y tipografías se adaptan a móvil, tablet y escritorio.
- **Normalización robusta de datos:** unifica variantes de nombres de ciudades (por ejemplo, "San Miguel de Tucumán" → "Tucumán") ignorando tildes y mayúsculas.
- **Despliegue estático:** compatible con GitHub Pages mediante `panel convert`.

---

## 🛠️ Stack Tecnológico

| Herramienta | Uso |
|---|---|
| [Panel](https://panel.holoviz.org/) | Framework de dashboard interactivo |
| [Pandas](https://pandas.pydata.org/) | Manipulación y análisis de datos |
| [NumPy](https://numpy.org/) | Cálculos numéricos |
| [Matplotlib](https://matplotlib.org/) | Visualizaciones |
| [Jupyter](https://jupyter.org/) | Notebook de análisis exploratorio |

---

## 📁 Estructura del Proyecto

```
.
├── app.py                 # Dashboard interactivo con Panel
├── analisis.ipynb         # Notebook de análisis exploratorio
├── data/
│   └── ventas.csv         # Dataset de ventas
├── docs/                  # Build estático para GitHub Pages (panel convert)
├── requirements.txt       # Dependencias del proyecto
├── .gitignore
└── README.md
```

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/juliososaang/mi-portfolio.git
cd mi-portfolio
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
# Windows (CMD)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 💻 Uso

### Ejecutar el dashboard en local

Desde la raíz del proyecto:

```bash
panel serve app.py
```

o, si el comando `panel` no está en el PATH del sistema:

```bash
python -m panel serve app.py
```

Luego abrí en el navegador:

```
http://localhost:5006/app
```

### Explorar el notebook de análisis

```bash
jupyter notebook analisis.ipynb
```

---

## 📈 Análisis Exploratorio

El notebook `analisis.ipynb` documenta el proceso de análisis previo al dashboard:

- Carga y limpieza del dataset (`encoding="latin-1"`, parseo de fechas).
- Exploración inicial con `df.info()`, `df.describe()` y `df.isnull().sum()`.
- Optimización de memoria convirtiendo columnas a tipo `category`.
- Normalización de nombres de ciudades y categorías.
- Visualizaciones de ventas mensuales, por ciudad y por categoría.

---

## 🌐 Despliegue en GitHub Pages

El proyecto incluye un build estático en la carpeta `docs/`, generado con:

```bash
panel convert app.py --to pyodide-worker --out docs
```

GitHub Pages sirve automáticamente el contenido de `docs/` en la URL del demo.

---

## 🧪 Requisitos del Sistema

- Python 3.10 o superior
- Navegador moderno (Chrome, Firefox, Edge, Safari)

---

## 👤 Autor

**Julio Sosa**

- GitHub: [@juliososaang](https://github.com/juliososaang)
- Portfolio: [juliososaang.github.io/mi-portfolio](https://juliososaang.github.io/mi-portfolio/)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consultá el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- Dataset de ventas sintético creado para fines educativos y de portfolio.
- Documentación oficial de [Panel](https://panel.holoviz.org/) y [Pandas](https://pandas.pydata.org/).