import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path

carpeta = Path(__file__).parent
figuras = carpeta / "figuras"
figuras.mkdir(exist_ok=True)

plt.rcParams.update({"figure.dpi": 150, "font.size": 11})

# ── Configuración desde JSON ──────────────────────────────────────────────────
with open(carpeta / "config.json", encoding="utf-8") as f:
    config = json.load(f)

csv_nombre  = config["archivo_csv"]
dimensiones = config["geometrias"]

# Detección automática de geometrías y columnas desde fila 1 del CSV
_header = pd.read_csv(carpeta / csv_nombre, header=None, nrows=1).iloc[0]
geometria_cols = {}
for i, val in enumerate(_header):
    if pd.notna(val) and str(val).strip():
        geometria_cols[str(val).strip()] = [i, i + 1, i + 2]

df_raw = pd.read_csv(carpeta / csv_nombre, skiprows=3, header=None)

datos = {}
for nombre, columnas in geometria_cols.items():
    if nombre not in dimensiones:
        print(f"[Aviso] '{nombre}' está en el CSV pero sin dimensiones en config.json — se omite.")
        continue
    df = df_raw[columnas].copy()
    df.columns = ["Tiempo", "Fuerza", "Desplazamiento"]
    df = df.apply(pd.to_numeric, errors="coerce")
    datos[nombre] = df

# ── Figura 1: Fuerza vs Desplazamiento (todas) con anotaciones ───────────────
fig, ax = plt.subplots(figsize=(11, 6))
for nombre, df in datos.items():
    df_limpio = df.dropna()
    ax.plot(df_limpio["Desplazamiento"], df_limpio["Fuerza"], label=nombre)


ax.set_xlabel("Desplazamiento (mm)")
ax.set_ylabel("Fuerza (N)")
ax.set_title("Fuerza vs. Desplazamiento — todas las geometrías")
ax.legend(fontsize=9)
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(figuras / "fig1_fuerza_desplazamiento.png", bbox_inches="tight")
plt.show()

# ── Figura 1b: Fuerza vs Desplazamiento — una por geometría ──────────────────
for nombre, df in datos.items():
    df_limpio = df.dropna()
    idx_max   = df_limpio["Fuerza"].idxmax()
    x_max     = df_limpio["Desplazamiento"][idx_max]
    y_max     = df_limpio["Fuerza"][idx_max]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df_limpio["Desplazamiento"], df_limpio["Fuerza"], color="steelblue", lw=1.5)
    ax.scatter(x_max, y_max, color="red", zorder=5, s=60,
               label=f"F_max = {y_max:.1f} N @ {x_max:.2f} mm")
    ax.set_xlabel("Desplazamiento (mm)")
    ax.set_ylabel("Fuerza (N)")
    ax.set_title(f"Fuerza vs. Desplazamiento — {nombre}")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figuras / f"fig1b_fuerza_desplazamiento_{nombre}.png", bbox_inches="tight")
    plt.show()

# ── Figura 2: Esfuerzo vs Deformación (todas) con anotación de zonas ─────────
fig, ax = plt.subplots(figsize=(11, 6))
for nombre, df in datos.items():
    df_limpio = df.dropna().copy()
    h, b, L = dimensiones[nombre]["h"], dimensiones[nombre]["b"], dimensiones[nombre]["L"]
    df_limpio["Esfuerzo"]    = (3 * df_limpio["Fuerza"] * L) / (2 * b * h**2)
    df_limpio["Deformacion"] = (6 * df_limpio["Desplazamiento"] * h) / (L**2)
    ax.plot(df_limpio["Deformacion"], df_limpio["Esfuerzo"], label=nombre)


ax.set_xlabel("Deformación (mm/mm)")
ax.set_ylabel("Esfuerzo (N/mm²)")
ax.set_title("Esfuerzo vs. Deformación — todas las geometrías")
ax.legend(fontsize=9)
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(figuras / "fig2_esfuerzo_deformacion.png", bbox_inches="tight")
plt.show()

# ── Figura 2b: Esfuerzo vs Deformación — una por geometría ───────────────────
for nombre, df in datos.items():
    df_limpio = df.dropna().copy()
    h, b, L   = dimensiones[nombre]["h"], dimensiones[nombre]["b"], dimensiones[nombre]["L"]
    df_limpio["Esfuerzo"]    = (3 * df_limpio["Fuerza"] * L) / (2 * b * h**2)
    df_limpio["Deformacion"] = (6 * df_limpio["Desplazamiento"] * h) / (L**2)
    idx_max   = df_limpio["Esfuerzo"].idxmax()
    e_max     = df_limpio["Deformacion"][idx_max]
    s_max     = df_limpio["Esfuerzo"][idx_max]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df_limpio["Deformacion"], df_limpio["Esfuerzo"], color="darkorange", lw=1.5)
    ax.scatter(e_max, s_max, color="red", zorder=5, s=60,
               label=f"σ_max = {s_max:.2f} N/mm²")
    ax.set_xlabel("Deformación (mm/mm)")
    ax.set_ylabel("Esfuerzo (N/mm²)")
    ax.set_title(f"Esfuerzo vs. Deformación — {nombre}")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figuras / f"fig2b_esfuerzo_deformacion_{nombre}.png", bbox_inches="tight")
    plt.show()

# ── Figuras 3: Punto de falla con zonas sombreadas ───────────────────────────
resultados = {}
for nombre, df in datos.items():
    df_limpio = df.dropna().copy()
    h, b, L = dimensiones[nombre]["h"], dimensiones[nombre]["b"], dimensiones[nombre]["L"]
    volumen = L * b * h

    idx_max  = df_limpio["Fuerza"].idxmax()
    x_max    = df_limpio["Desplazamiento"][idx_max]
    y_max    = df_limpio["Fuerza"][idx_max]
    d_vals   = df_limpio["Desplazamiento"].values
    d_fin    = d_vals[-1]

    df_limpio["Esfuerzo"]    = (3 * df_limpio["Fuerza"] * L) / (2 * b * h**2)
    df_limpio["Deformacion"] = (6 * df_limpio["Desplazamiento"] * h) / (L**2)

    energia  = np.trapezoid(df_limpio["Fuerza"], df_limpio["Desplazamiento"])
    sea      = energia / volumen
    n_el     = max(2, int(len(df_limpio) * 0.20))
    zona_el  = df_limpio.iloc[:n_el]
    coef     = np.polyfit(zona_el["Deformacion"], zona_el["Esfuerzo"], 1)
    modulo   = coef[0]

    resultados[nombre] = {
        "F_max": y_max, "d_max": x_max,
        "sigma_max": df_limpio["Esfuerzo"].max(),
        "energia": energia, "SEA": sea, "modulo": modulo, "volumen": volumen,
    }

    # Límite zona elástica ≈ último punto antes de que F supere el 30% del máximo (solo en carga)
    df_pre  = df_limpio.loc[:idx_max]
    f30     = 0.30 * y_max
    mask_el = df_pre["Fuerza"] < f30
    d_elastico = df_pre[mask_el]["Desplazamiento"].max() if mask_el.any() else x_max * 0.2

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axvspan(0,           d_elastico, alpha=0.12, color="green")
    ax.axvspan(d_elastico,  x_max,      alpha=0.10, color="orange")
    ax.axvspan(x_max,       d_fin,      alpha=0.10, color="red")

    ax.plot(df_limpio["Desplazamiento"], df_limpio["Fuerza"], color="steelblue", lw=1.5)
    ax.scatter(x_max, y_max, color="red", zorder=5, s=60,
               label=f"Falla: {y_max:.1f} N @ {x_max:.2f} mm")

    ymax_plot = y_max * 1.15
    ax.text(d_elastico * 0.3,    ymax_plot * 0.92, "Elástica",   color="green",     fontsize=8)
    ax.text((d_elastico + x_max) / 2, ymax_plot * 0.92, "Plástica", color="darkorange", fontsize=8, ha="center")
    ax.text(x_max + (d_fin - x_max) * 0.2, ymax_plot * 0.92, "Post-falla", color="red", fontsize=8)

    ax.set_xlabel("Desplazamiento (mm)")
    ax.set_ylabel("Fuerza (N)")
    ax.set_title(f"Punto de falla — {nombre}")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figuras / f"fig3_falla_{nombre}.png", bbox_inches="tight")
    plt.show()

# ── Figura 4: SEA con etiquetas de valor y línea media ───────────────────────
nombres_sea  = list(resultados.keys())
valores_sea  = [resultados[n]["SEA"] for n in nombres_sea]
media_sea    = float(np.mean(valores_sea))

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(nombres_sea, valores_sea, color="steelblue", edgecolor="white")

for bar, val in zip(bars, valores_sea):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
            f"{val:.4f}", ha="center", va="bottom", fontsize=8)

ax.axhline(media_sea, color="red", linestyle="--", linewidth=1.2,
           label=f"Media = {media_sea:.4f} N·mm/mm³")
ax.set_xlabel("Geometría")
ax.set_ylabel("SEA (N·mm / mm³)")
ax.set_title("Absorción de Energía Específica por Volumen")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(figuras / "fig4_sea_barras.png", bbox_inches="tight")
plt.show()

# ── Figura 5: Radar chart ─────────────────────────────────────────────────────
categorias = ["Esfuerzo\nMáx (N/mm²)", "Energía\n(N·mm)", "SEA\n(N·mm/mm³)", "Módulo\n(N/mm²)"]
N = len(categorias)
angulos = [n / float(N) * 2 * np.pi for n in range(N)]
angulos += angulos[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
props   = ["sigma_max", "energia", "SEA", "modulo"]
maximos = [max(resultados[n][p] for n in resultados) for p in props]

for nombre, res in resultados.items():
    vals_norm = [res[p] / m if m != 0 else 0 for p, m in zip(props, maximos)]
    vals_norm += vals_norm[:1]
    ax.plot(angulos, vals_norm, linewidth=1.5, label=nombre)
    ax.fill(angulos, vals_norm, alpha=0.1)

ax.set_xticks(angulos[:-1])
ax.set_xticklabels(categorias, size=10)
ax.set_title("Comparación multipropiedad — todas las geometrías", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15))
plt.tight_layout()
plt.savefig(figuras / "fig5_radar.png", bbox_inches="tight")
plt.show()

# ── Tabla resumen en consola ──────────────────────────────────────────────────
print(f"\n{'Geometría':12s} {'F_max(N)':>10s} {'σ_max(N/mm²)':>13s} {'E(N·mm)':>12s} {'SEA':>12s} {'E_flex':>12s}")
print("-" * 75)
for nombre, res in resultados.items():
    print(f"{nombre:12s} {res['F_max']:>10.2f} {res['sigma_max']:>13.4f} "
          f"{res['energia']:>12.2f} {res['SEA']:>12.5f} {res['modulo']:>12.1f}")

# ── Estadístico 1: Estadísticas descriptivas ─────────────────────────────────
print("\n--- Estadísticas descriptivas de Fuerza (N) ---")
for nombre, df in datos.items():
    df_limpio = df.dropna().copy()
    stats = df_limpio["Fuerza"].describe()
    print(f"\n{nombre}:\n{stats.to_string()}")

# ── Estadístico 2: Boxplot con media marcada ──────────────────────────────────
fuerzas_pos = [datos[n].dropna()["Fuerza"].clip(lower=0).values for n in datos]
medias      = [np.mean(f) for f in fuerzas_pos]

fig, ax = plt.subplots(figsize=(10, 6))
bp = ax.boxplot(fuerzas_pos, tick_labels=list(datos.keys()), patch_artist=True,
                medianprops=dict(color="red", linewidth=2))
colores_box = [plt.colormaps["tab10"](i) for i in range(10)]
for i, (patch, color) in enumerate(zip(bp["boxes"], colores_box)):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
    ax.plot(i + 1, medias[i], marker="D", color="black", markersize=6, zorder=5)

media_patch = Line2D([0], [0], marker="D", color="black",
                         linestyle="None", markersize=6, label="Media")
mediana_patch = mpatches.Patch(color="red", label="Mediana")
ax.legend(handles=[media_patch, mediana_patch], fontsize=9)


ax.set_xlabel("Geometría")
ax.set_ylabel("Fuerza (N)")
ax.set_title("Distribución de Fuerza por geometría (boxplot)")
ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(figuras / "fig6_boxplot.png", bbox_inches="tight")
plt.show()

# ── Estadístico 3: Heatmap de correlaciones ───────────────────────────────────
props_names = ["σ_max\n(N/mm²)", "Energía\n(N·mm)", "SEA\n(N·mm/mm³)", "Módulo\n(N/mm²)"]
props_keys  = ["sigma_max", "energia", "SEA", "modulo"]
matriz      = np.array([[resultados[n][k] for k in props_keys] for n in resultados])
df_props    = pd.DataFrame(matriz, columns=props_names, index=list(resultados.keys()))
corr        = df_props.corr()

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(im, ax=ax, label="Coeficiente de Pearson")
ax.set_xticks(range(len(props_names)))
ax.set_yticks(range(len(props_names)))
ax.set_xticklabels(props_names, fontsize=9)
ax.set_yticklabels(props_names, fontsize=9)
for i in range(len(props_names)):
    for j in range(len(props_names)):
        val = corr.values[i, j]
        color_txt = "white" if abs(val) > 0.6 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                fontsize=11, fontweight="bold", color=color_txt)
ax.set_title("Mapa de correlación entre propiedades mecánicas")
plt.tight_layout()
plt.savefig(figuras / "fig7_heatmap_correlacion.png", bbox_inches="tight")
plt.show()

# ── Estadístico 4: TOPSIS con etiquetas y ganador ────────────────────────────
matriz_norm  = matriz / np.sqrt((matriz ** 2).sum(axis=0))
pesos        = np.ones(len(props_keys)) / len(props_keys)
matriz_pond  = matriz_norm * pesos
ideal_mejor  = matriz_pond.max(axis=0)
ideal_peor   = matriz_pond.min(axis=0)
d_mejor      = np.sqrt(((matriz_pond - ideal_mejor) ** 2).sum(axis=1))
d_peor       = np.sqrt(((matriz_pond - ideal_peor)  ** 2).sum(axis=1))
score_topsis = d_peor / (d_mejor + d_peor)

nombres_lista = list(resultados.keys())
ranking = sorted(zip(nombres_lista, score_topsis), key=lambda x: x[1], reverse=True)

print("\n--- Ranking TOPSIS ---")
for i, (nombre, s) in enumerate(ranking, 1):
    print(f"  {i}. {nombre:12s}: score = {s:.4f}")

nombres_rank = [r[0] for r in ranking]
scores_rank  = [r[1] for r in ranking]
colores_rank = ["gold" if i == 0 else "steelblue" for i in range(len(nombres_rank))]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(nombres_rank, scores_rank, color=colores_rank, edgecolor="white")

for bar, val in zip(bars, scores_rank):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
            f"{val:.3f}", ha="center", va="bottom", fontsize=9)

ax.annotate("Geometría óptima\n(criterios iguales)",
            xy=(0, scores_rank[0]), xytext=(1.5, scores_rank[0] * 0.95),
            arrowprops=dict(arrowstyle="->", color="darkgoldenrod"),
            fontsize=9, color="darkgoldenrod")

ax.set_xlabel("Geometría (ordenadas por ranking)")
ax.set_ylabel("Score TOPSIS")
ax.set_title("Ranking TOPSIS — selección de geometría óptima global")
ax.set_ylim(0, max(scores_rank) * 1.2)
ax.grid(axis="y", linestyle="--", alpha=0.5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(figuras / "fig8_topsis.png", bbox_inches="tight")
plt.show()

# ── Estadístico 5: Rigidez instantánea con anotaciones ───────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
for nombre, df in datos.items():
    df_limpio = df.dropna().copy()
    F = df_limpio["Fuerza"].values
    d = df_limpio["Desplazamiento"].values
    k = np.gradient(F, d)
    ax.plot(d, k, label=nombre, alpha=0.85)

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.annotate("k > 0: panel\ncargando",
            xy=(0.5, 800), xytext=(3, 1200),
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=8, color="gray")
ax.annotate("k < 0: post-falla\n(softening)",
            xy=(5, -100), xytext=(8, -250),
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=8, color="gray")

ax.set_xlabel("Desplazamiento (mm)")
ax.set_ylabel("Rigidez instantánea dF/dd (N/mm)")
ax.set_title("Evolución de la rigidez instantánea durante el ensayo")
ax.set_ylim(-500, 3000)
ax.legend(fontsize=9)
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(figuras / "fig9_rigidez_instantanea.png", bbox_inches="tight")
plt.show()
