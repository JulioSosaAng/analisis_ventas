# app.py - Panel dashboard (Pyodide-friendly)
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as mpe
from matplotlib.ticker import FuncFormatter, MaxNLocator
import panel as pn
from panel.template import MaterialTemplate


# Enable Panel (material theme + custom scrollbar CSS)
pn.extension('tabulator', raw_css=["""
/* Scrollbar más visible para los MultiSelect con clase .scroll-visible */
.scroll-visible select{
  scrollbar-width: auto;                 /* Firefox */
  scrollbar-color: #8a8a8a #f1f1f1;
}
.scroll-visible select::-webkit-scrollbar{
  width: 12px;                           /* Chrome/Edge/Safari */
}
.scroll-visible select::-webkit-scrollbar-track{
  background: #f1f1f1;
  border-radius: 8px;
}
.scroll-visible select::-webkit-scrollbar-thumb{
  background: #8a8a8a;
  border-radius: 8px;
  border: 2px solid #f1f1f1;
}
.scroll-visible select::-webkit-scrollbar-thumb:hover{
  background: #5a5a5a;
}
"""])

# ========= 1) DATA =========
def load_df():
    # Lee data/ventas.csv junto a app.py
    posibles = ["data/ventas.csv", "./data/ventas.csv"]
    df = None
    for ruta in posibles:
        try:
            df = pd.read_csv(ruta, encoding="latin-1")
            break
        except Exception:
            continue
    if df is None:
        raise FileNotFoundError("No se encontró 'data/ventas.csv'. Verificá la ruta.")

    # Tipos básicos
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
    required_cols = ['fecha', 'ciudad', 'categoria', 'total_venta']
    faltan = [c for c in required_cols if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas obligatorias en el CSV: {faltan}")

    # Strings
    df['ciudad'] = df['ciudad'].astype(str)
    df['categoria'] = df['categoria'].astype(str)

    # Numérico
    df['total_venta'] = pd.to_numeric(df['total_venta'], errors='coerce').fillna(0.0)

    # --- Normalización robusta de ciudades (unifica "San Miguel de Tucumán" en "Tucumán") ---
    import unicodedata, re

    def _strip_accents(s: str) -> str:
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

    ALIAS_TUCUMAN = {
        "tucuman",
        "san miguel de tucuman",
        "san miguel tucuman",
        "s m de tucuman",
        "s.m. de tucuman",
        "Tucumán",
        "San Miguel de Tucumán",        
    }

    def _canon_city(s):
        original = str(s).strip()
        s0 = _strip_accents(original).lower()
        s0 = re.sub(r"\s+", " ", s0)  # colapsa espacios
        if s0 in ALIAS_TUCUMAN:
            return "Tucumán"
        return original  # dejá el resto tal como viene (con tildes)

    df['ciudad'] = df['ciudad'].map(_canon_city)

    return df

df = load_df()

# ========= 2) RESPONSIVE HELPERS =========
def responsive_cfg(container_width):
    w = container_width or 1200
    if w < 520:      # móvil
        return dict(figsize=(5.0, 3.2), fs_title=14, fs_label=10, fs_tick=9, xtick_rot=15, labelpad=10)
    elif w < 900:    # tablet
        return dict(figsize=(7.0, 4.2), fs_title=16, fs_label=12, fs_tick=10, xtick_rot=15, labelpad=10)
    else:            # desktop
        return dict(figsize=(8.5, 5.0), fs_title=18, fs_label=12, fs_tick=11, xtick_rot=15, labelpad=12)

def _apply_fig_cfg(fig, cfg):
    # Adjust figure and fonts post-hoc if the plotting function doesn't accept kwargs
    try:
        fig.set_size_inches(*cfg['figsize'], forward=True)
    except Exception:
        pass
    for ax in getattr(fig, "axes", []):
        try: ax.title.set_fontsize(cfg['fs_title'])
        except Exception: pass
        try:
            ax.xaxis.label.set_fontsize(cfg['fs_label'])
            ax.yaxis.label.set_fontsize(cfg['fs_label'])
            ax.xaxis.labelpad = cfg['labelpad']
        except Exception: pass
        try:
            ax.tick_params(axis='x', labelsize=cfg['fs_tick'])
            ax.tick_params(axis='y', labelsize=cfg['fs_tick'])
            for t in ax.get_xticklabels(): t.set_rotation(cfg['xtick_rot'])
        except Exception: pass
    return fig

# ========= 3) PLOTTING FUNCTIONS =========
def create_monthly_sales_chart(df, mes_inicial, mes_final, *, figsize=(8.5,5.0),
                               fs_title=16, fs_label=12, fs_tick=10, labelpad=12, xtick_rot=0):
    """Ventas mensuales como burbujas + línea, con etiquetas legibles."""
    inicio_rango = pd.to_datetime(mes_inicial)
    fin_rango = pd.to_datetime(mes_final) + pd.offsets.MonthEnd(0)
    dff = df[(df['fecha'] >= inicio_rango) & (df['fecha'] <= fin_rango)].copy()

    if dff.empty:
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title("No hay datos para esta selección", fontsize=fs_title)
        ax.axis('off'); plt.close(fig); return fig

    ventas_por_mes = dff.groupby(pd.Grouper(key='fecha', freq='ME'))['total_venta'].sum()
    meses = ventas_por_mes.index.strftime('%b %Y')

    base_color = '#4682B4'
    accent_color = '#00bcd4'
    vmax = ventas_por_mes.values.max() if len(ventas_por_mes)>0 else 0
    sizes = (ventas_por_mes.values / vmax * 200) if vmax > 0 else np.zeros_like(ventas_por_mes.values)

    colores = [base_color]*len(ventas_por_mes)
    if vmax > 0:
        idx_max = int(np.argmax(ventas_por_mes.values))
        colores[idx_max] = accent_color

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    ax.scatter(meses, ventas_por_mes.values, s=sizes, c=colores, alpha=0.85, edgecolor='black')
    ax.plot(meses, ventas_por_mes.values, color=base_color, linestyle='-', alpha=0.6)

    def format_k(num, pos):
        return f'{num/1000:.0f}k' if abs(num) >= 1000 else f'{num:.0f}'
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.yaxis.set_major_formatter(FuncFormatter(format_k))

    # Etiquetas con offset dinámico y halo
    for x, y, s in zip(meses, ventas_por_mes.values, sizes):
        offset_pts = 4 + np.sqrt(s) * 0.5
        txt = ax.annotate(f'{y:.0f}', xy=(x, y), xytext=(0, offset_pts),
                          textcoords='offset points', ha='center', va='bottom',
                          fontsize=fs_tick, fontweight='bold', color='black', clip_on=False)
        txt.set_path_effects([mpe.withStroke(linewidth=2, foreground="white")])

    if vmax > 0:
        ax.set_ylim(0, vmax * 1.25)

    ax.set_title(f"Ventas mensuales ({inicio_rango.strftime('%b %Y')} - {fin_rango.strftime('%b %Y')})",
                 fontsize=fs_title, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=fs_label, labelpad=labelpad)
    ax.set_ylabel('Total venta', fontsize=fs_label)
    ax.tick_params(axis='x', labelsize=fs_tick)
    for t in ax.get_xticklabels(): t.set_rotation(xtick_rot)
    ax.grid(axis='y', alpha=0.3)
    plt.close(fig)
    return fig

def create_city_sales_chart(df, ciudades_seleccionadas, *, figsize=(8.5,5.0),
                            fs_title=16, fs_label=12, fs_tick=10, labelpad=12, xtick_rot=0):
    """Barras de total de ventas por ciudad (para ciudades seleccionadas)."""
    if not ciudades_seleccionadas:
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title("Selecciona al menos una ciudad", fontsize=fs_title)
        ax.axis('off'); plt.close(fig); return fig

    dff = df[df['ciudad'].isin(ciudades_seleccionadas)].copy()
    if dff.empty:
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title("Sin datos para las ciudades seleccionadas", fontsize=fs_title)
        ax.axis('off'); plt.close(fig); return fig

    serie = dff.groupby('ciudad')['total_venta'].sum().sort_values(ascending=False)
    base_color = '#4682B4'; accent_color = '#00bcd4'
    colores = [accent_color if i==0 else base_color for i in range(len(serie))]

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    bars = ax.bar(serie.index, serie.values, color=colores, alpha=0.85)

    def format_k(num, pos):
        return f'{num/1000:.0f}k' if abs(num) >= 1000 else f'{num:.0f}'
    ax.yaxis.set_major_formatter(FuncFormatter(format_k))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))

    ymax = serie.values.max() if len(serie)>0 else 0
    for bar, val in zip(bars, serie.values):
        txt = ax.annotate(f'{val:.0f}', xy=(bar.get_x()+bar.get_width()/2, val),
                          xytext=(0, 8), textcoords='offset points',
                          ha='center', va='bottom', fontsize=fs_tick, fontweight='bold', color='black')
        txt.set_path_effects([mpe.withStroke(linewidth=2, foreground="white")])
    if ymax>0: ax.set_ylim(0, ymax*1.15)

    titulo = ("Total de Ventas - Ciudades Seleccionadas"
              if len(ciudades_seleccionadas)!=1 else f"Total de Ventas - {ciudades_seleccionadas[0]}")
    ax.set_title(titulo, fontsize=fs_title, fontweight='bold')
    ax.set_xlabel('Ciudad', fontsize=fs_label, labelpad=labelpad)
    ax.set_ylabel('Total venta', fontsize=fs_label)
    ax.tick_params(axis='x', labelsize=fs_tick)
    for t in ax.get_xticklabels(): t.set_rotation(xtick_rot)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.close(fig)
    return fig

def create_category_sales_chart(df, *, figsize=(8.5,5.0),
                                fs_title=16, fs_label=12, fs_tick=10, labelpad=12, xtick_rot=0):
    """Barras de ventas por categoría con etiquetas legibles."""
    serie = (df.groupby('categoria', observed=True)['total_venta']
               .sum().sort_values(ascending=False))

    base_color = '#4682B4'; accent_color = '#00bcd4'
    colores = [accent_color if i==0 else base_color for i in range(len(serie))]

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    bars = ax.bar(serie.index, serie.values, color=colores, alpha=0.85)

    def format_k(num, pos):
        return f'{num/1000:.0f}k' if abs(num) >= 1000 else f'{num:.0f}'
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.yaxis.set_major_formatter(FuncFormatter(format_k))

    ymax = serie.values.max() if len(serie)>0 else 0
    for bar, val in zip(bars, serie.values):
        txt = ax.annotate(f'{val:.0f}',
                          xy=(bar.get_x()+bar.get_width()/2, val),
                          xytext=(0, 8), textcoords='offset points',
                          ha='center', va='bottom',
                          fontsize=fs_tick, fontweight='bold', color='black', clip_on=False)
        txt.set_path_effects([mpe.withStroke(linewidth=2, foreground="white")])
    if ymax>0: ax.set_ylim(0, ymax*1.15)

    ax.set_title('Ventas por categoría', fontsize=fs_title, fontweight='bold')
    ax.set_xlabel('Categoría', fontsize=fs_label, labelpad=labelpad)
    ax.set_ylabel('Total venta', fontsize=fs_label)
    ax.tick_params(axis='x', labelsize=fs_tick)
    for t in ax.get_xticklabels(): t.set_rotation(xtick_rot)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.close(fig)
    return fig

# ========= 4) WIDGETS =========
ciudades_unicas   = sorted(df['ciudad'].unique().tolist())
fechas_por_mes    = sorted(df['fecha'].dt.strftime('%Y-%m').unique().tolist())
categorias_unicas = sorted(df['categoria'].unique().tolist())

filtro_modo_ciudad = pn.widgets.RadioBoxGroup(
    name='Modo de Visualización',
    options=['Ver todas las ciudades', 'Comparar dos ciudades'],
    value='Ver todas las ciudades'
)
filtro_todas_ciudades = pn.widgets.MultiSelect(
    name='Seleccionar Ciudades',
    options=ciudades_unicas,
    value=ciudades_unicas,
    sizing_mode='stretch_width',
    size=min(len(ciudades_unicas), 12),
    css_classes=['scroll-visible']
)
filtro_ciudad1 = pn.widgets.Select(name='Ciudad 1', options=ciudades_unicas, value=ciudades_unicas[0])
filtro_ciudad2 = pn.widgets.Select(name='Ciudad 2', options=ciudades_unicas, value=ciudades_unicas[1])

filtro_mes_inicial = pn.widgets.Select(name='Mes Inicial', options=fechas_por_mes, value=fechas_por_mes[0])
filtro_mes_final   = pn.widgets.Select(name='Mes Final',   options=fechas_por_mes, value=fechas_por_mes[-1])

filtro_cat_mes_inicial = pn.widgets.Select(name='Mes Inicial', options=fechas_por_mes, value=fechas_por_mes[0])
filtro_cat_mes_final   = pn.widgets.Select(name='Mes Final',   options=fechas_por_mes, value=fechas_por_mes[-1])
filtro_cat_ciudades    = pn.widgets.MultiSelect(
    name="Ciudades",
    options=ciudades_unicas,
    value=ciudades_unicas,
    sizing_mode='stretch_width',
    size=min(len(ciudades_unicas), 12),
    css_classes=['scroll-visible']
)
filtro_cat_categorias  = pn.widgets.MultiSelect(
    name="Categorías",
    options=categorias_unicas,
    value=categorias_unicas,
    sizing_mode='stretch_width',
    size=min(len(categorias_unicas), 12),
    css_classes=['scroll-visible']
)

# ========= 5) RESPONSIVE WIDTH ANCHOR =========
width_anchor = pn.Spacer(sizing_mode='stretch_width', height=0)

# ========= 6) CALLBACKS =========
def _filtrar_df(df_base, mes_ini, mes_fin, ciudades_sel, categorias_sel):
    ini = pd.to_datetime(mes_ini)
    fin = pd.to_datetime(mes_fin) + pd.offsets.MonthEnd(0)
    m = (
        (df_base['fecha'] >= ini) & (df_base['fecha'] <= fin) &
        (df_base['ciudad'].isin(ciudades_sel)) &
        (df_base['categoria'].isin(categorias_sel))
    )
    return df_base.loc[m].copy()

def _mensual_resp(w, mi, mf):
    cfg = responsive_cfg(w)
    try:
        fig = create_monthly_sales_chart(df=df, mes_inicial=mi, mes_final=mf, **cfg)
    except TypeError:
        fig = create_monthly_sales_chart(df=df, mes_inicial=mi, mes_final=mf)
        fig = _apply_fig_cfg(fig, cfg)
    return pn.pane.Matplotlib(fig, tight=True, sizing_mode='stretch_width')

grafico_interactivo_mensual = pn.bind(
    _mensual_resp, width_anchor.param.width, filtro_mes_inicial, filtro_mes_final
)

@pn.depends(filtro_modo_ciudad, filtro_todas_ciudades, filtro_ciudad1, filtro_ciudad2, width_anchor.param.width)
def generar_grafico_ciudad(modo, ciudades_todas, ciudad1, ciudad2, w):
    cfg = responsive_cfg(w)
    ciudades = ciudades_todas if modo == 'Ver todas las ciudades' else [ciudad1, ciudad2]
    try:
        fig = create_city_sales_chart(df, ciudades, **cfg)
    except TypeError:
        fig = create_city_sales_chart(df, ciudades)
        fig = _apply_fig_cfg(fig, cfg)
    return pn.pane.Matplotlib(fig, tight=True, sizing_mode='stretch_width')

@pn.depends(filtro_cat_mes_inicial, filtro_cat_mes_final, filtro_cat_ciudades, filtro_cat_categorias, width_anchor.param.width)
def generar_grafico_categoria(m_ini, m_fin, ciudades_sel, categorias_sel, w):
    cfg = responsive_cfg(w)
    dff = _filtrar_df(df, m_ini, m_fin, ciudades_sel, categorias_sel)
    if dff.empty:
        fig, ax = plt.subplots(figsize=cfg['figsize'])
        ax.set_title("Sin datos para los filtros seleccionados", fontsize=cfg['fs_title'])
        ax.axis('off'); plt.close(fig)
        return pn.pane.Matplotlib(fig, tight=True, sizing_mode='stretch_width')
    try:
        fig = create_category_sales_chart(dff, **cfg)
    except TypeError:
        fig = create_category_sales_chart(dff)
        fig = _apply_fig_cfg(fig, cfg)
    return pn.pane.Matplotlib(fig, tight=True, sizing_mode='stretch_width')

# ========= 7) TABS =========
tabs = pn.Tabs(
    ("Ventas Mensuales", grafico_interactivo_mensual),
    ("Ventas por Ciudad", generar_grafico_ciudad),
    ("Ventas por Categoría", generar_grafico_categoria),
    tabs_location='above'
)

# ========= 8) SIDEBAR DINÁMICO =========
def _bloque_filtros_ciudad():
    col_todas = pn.Column(
        pn.pane.Markdown("### Ventas por Ciudad"),
        filtro_modo_ciudad,
        pn.Spacer(height=5),
        pn.pane.Markdown("**Seleccionar Ciudades - Para Seleccionar Multiples Ciudades, Mantener Ctrl**"),
        filtro_todas_ciudades
    )
    col_comparar = pn.Column(
        pn.pane.Markdown("### Ventas por Ciudad"),
        filtro_modo_ciudad,
        pn.Spacer(height=5),
        pn.Row(filtro_ciudad1),
        pn.Row(filtro_ciudad2)
    )
    return pn.bind(lambda modo: col_todas if modo == 'Ver todas las ciudades' else col_comparar,
                   filtro_modo_ciudad)

def sidebar_contenido(active_tab_index):
    # 0 = Mensuales, 1 = Ciudad, 2 = Categoría
    if active_tab_index == 0:
        return pn.Column(
            pn.pane.Markdown("### Ventas Mensuales"),
            pn.Row(filtro_mes_inicial),
            pn.Row(filtro_mes_final),
        )
    elif active_tab_index == 1:
        return _bloque_filtros_ciudad()
    else:
        return pn.Column(
            pn.pane.Markdown("### Ventas por Categoría"),
            pn.pane.Markdown("**Rango de meses**"),
            pn.Row(filtro_cat_mes_inicial),
            pn.Row(filtro_cat_mes_final),
            pn.pane.Markdown("**Ciudades - Para Seleccionar Multiples Ciudades, Mantener Ctrl**"),
            filtro_cat_ciudades,
            pn.pane.Markdown("**Categorías**"),
            filtro_cat_categorias
        )

sidebar_dinamico = pn.bind(sidebar_contenido, active_tab_index=tabs.param.active)

# ========= 9) TEMPLATE =========
template = MaterialTemplate(
    site="Volver al Portfolio",
    title="Dashboard de Ventas de la Empresa",
    site_url="https://juliososaang.github.io/mi-portfolio/",
    sidebar=[sidebar_dinamico],
    main=[pn.Column(width_anchor, tabs)]
)

# Important for Panel convert / serve
template.servable()
