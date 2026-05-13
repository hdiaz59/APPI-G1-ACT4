# =========================================================
# DASHBOARD INTERACTIVO PARA EL ANÁLISIS DE MORTALIDAD EN COLOMBIA (AÑO 2019)
# =========================================================

import os
import json
import pandas as pd

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIG APP
# =========================================================

app = dash.Dash(

    __name__,

    external_stylesheets=[
        dbc.themes.FLATLY
    ]
)

server = app.server

# =========================================================
# VARIABLES GLOBALES
# =========================================================

modelo = None
controlador = None

# =========================================================
# MODELO
# =========================================================

class ModeloMortalidad:

    def __init__(self):

        # =================================================
        # RUTA BASE
        # =================================================

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        # =================================================
        # DATASET
        # =================================================

        ruta_excel = os.path.join(
            BASE_DIR,
            "data",
            "Mortalidad2.xlsx"
        )

        self.df = pd.read_excel(ruta_excel)

        # =================================================
        # LIMPIEZA
        # =================================================

        self.df.columns = (

            self.df.columns
            .str.strip()
            .str.replace(" ", "_")
        )

        # =================================================
        # GEOJSON
        # =================================================

        ruta_geojson = os.path.join(
            BASE_DIR,
            "data",
            "depts.json"
        )

        with open(ruta_geojson, encoding="utf-8") as f:

            self.geojson = json.load(f)

        # =================================================
        # IDS GEOJSON
        # =================================================

        for feature in self.geojson["features"]:

            feature["id"] = (
                feature["properties"]["NOMBRE_DPT"]
            )

        # =================================================
        # SEXO
        # =================================================

        self.df["SEXO_LABEL"] = self.df["SEXO"].map({

            1: "Masculino",

            2: "Femenino",

            3: "Indeterminado"

        }).fillna("Sin información")

        # =================================================
        # EDAD
        # =================================================

        self.df["RANGO_EDAD"] = self.df[
            "GRUPO_EDAD1"
        ].apply(self.clasificar_grupo_edad)

    # =====================================================
    # CLASIFICAR EDAD
    # =====================================================

    def clasificar_grupo_edad(self, codigo):

        try:

            codigo = int(codigo)

            if 0 <= codigo <= 4:
                return "Menor de 1 mes"

            elif 5 <= codigo <= 6:
                return "1 a 11 meses"

            elif 7 <= codigo <= 8:
                return "1 a 4 años"

            elif 9 <= codigo <= 10:
                return "5 a 14 años"

            elif codigo == 11:
                return "15 a 19 años"

            elif 12 <= codigo <= 13:
                return "20 a 29 años"

            elif 14 <= codigo <= 16:
                return "30 a 44 años"

            elif 17 <= codigo <= 19:
                return "45 a 59 años"

            elif 20 <= codigo <= 24:
                return "60 a 84 años"

            elif 25 <= codigo <= 28:
                return "85 a 100+ años"

            else:
                return "Sin información"

        except:

            return "Sin información"


# =========================================================
# CONTROLADOR
# =========================================================

class ControladorMortalidad:

    def __init__(self, modelo):

        self.modelo = modelo

    # =====================================================
    # FILTROS
    # =====================================================

    def filtrar_datos(
        self,
        departamento,
        edad,
        sexo,
        enfermedad
    ):

        df = self.modelo.df.copy()

        if departamento != "TODOS":

            df = df[
                df["DES_DEPARTAMENTO"] == departamento
            ]

        if edad != "TODOS":

            df = df[
                df["RANGO_EDAD"] == edad
            ]

        if sexo != "TODOS":

            df = df[
                df["SEXO_LABEL"] == sexo
            ]

        if enfermedad != "TODOS":

            df = df[
                df["DESCRIPCION__MUERTE"] == enfermedad
            ]

        return df

    # =====================================================
    # MAPA
    # =====================================================

    def crear_mapa(self, df):

        df_mapa = (

            df.groupby("DES_DEPARTAMENTO")
            .size()
            .reset_index(name="TOTAL")
        )

        fig = go.Figure(go.Choroplethmapbox(

            geojson=self.modelo.geojson,

            locations=df_mapa["DES_DEPARTAMENTO"],

            z=df_mapa["TOTAL"],

            featureidkey="id",

            text=df_mapa["DES_DEPARTAMENTO"],

            colorscale="Reds",

            marker_opacity=0.7,

            marker_line_width=0.5,

            hovertemplate=
                "<b>%{text}</b><br>" +
                "Muertes: %{z:,}<extra></extra>"
        ))

        fig.update_layout(

            mapbox_style="carto-positron",

            mapbox_zoom=4.7,

            mapbox_center={

                "lat": 4.57,

                "lon": -74.0
            },

            height=700,

            margin={
                "r":0,
                "t":50,
                "l":0,
                "b":0
            },

            title="Distribución Mortalidad por Departamento"
        )

        return fig

    # =====================================================
    # LINEA
    # =====================================================

    def crear_linea(self, df):


        meses = {

            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre"
        }

        df_linea = (

            df.groupby("MES")
            .size()
            .reset_index(name="TOTAL")
            .sort_values("MES")
        )

        df_linea["MES_NOMBRE"] = (
            df_linea["MES"]
            .astype(int)
            .map(meses)
        )

        fig = px.line(

            df_linea,

            x="MES_NOMBRE",

            y="TOTAL",

            markers=True,

            text="TOTAL",

            title="Total Muertes por Mes"
        )

        fig.update_traces(

            textposition="top center"
        )

        return fig

    # =====================================================
    # HOMICIDIOS
    # =====================================================

    def crear_homicidios(self, df):

        df_h = df[
            df["COD_MUERTE"]
            .astype(str)
            .str.startswith("X95", na=False)
        ]

        top = (

            df_h.groupby("MUNICIPIO")
            .size()
            .reset_index(name="TOTAL")
            .sort_values(
                "TOTAL",
                ascending=False
            )
            .head(5)
        )

        fig = px.bar(

            top,

            x="MUNICIPIO",

            y="TOTAL",

            text="TOTAL",

            color="TOTAL",

            title="Top 5 Ciudades Más Violentas"
        )

        fig.update_traces(

            textposition="outside"
        )

        return fig

    # =====================================================
    # TORTA
    # =====================================================

    def crear_torta(self, df):

        menor = (

            df.groupby("MUNICIPIO")
            .size()
            .reset_index(name="TOTAL")
            .sort_values(
                "TOTAL",
                ascending=True
            )
            .head(10)
        )

        fig = px.pie(

            menor,

            names="MUNICIPIO",

            values="TOTAL",

            title="10 Ciudades Menor Mortalidad"
        )

        fig.update_traces(

            textinfo="percent+label+value"
        )

        return fig

    # =====================================================
    # SEXO
    # =====================================================

    def crear_sexo(self, df):

        df_sexo = (

            df.groupby([
                "DES_DEPARTAMENTO",
                "SEXO_LABEL"
            ])
            .size()
            .reset_index(name="TOTAL")
        )

        fig = px.bar(

            df_sexo,

            x="DES_DEPARTAMENTO",

            y="TOTAL",

            color="SEXO_LABEL",

            text="TOTAL",

            barmode="stack",

            title="Muertes por Sexo"
        )

        return fig

    # =====================================================
    # HISTOGRAMA
    # =====================================================

    def crear_histograma(self, df):

        df_hist = (

            df.groupby("RANGO_EDAD")
            .size()
            .reset_index(name="TOTAL")
        )

        fig = px.bar(

            df_hist,

            x="RANGO_EDAD",

            y="TOTAL",

            color="RANGO_EDAD",

            text="TOTAL",

            title="Distribución Grupo Edad"
        )

        return fig

    # =====================================================
    # TABLA
    # =====================================================

    def crear_tabla(self, df):

        tabla = (

            df.groupby([
                "COD_MUERTE",
                "DESCRIPCION__MUERTE"
            ])

            .size()

            .reset_index(name="TOTAL")

            .sort_values(
                "TOTAL",
                ascending=False
            )

            .head(10)
        )

        return tabla



# =========================================================
# INICIALIZAR MODELO
# =========================================================

def inicializar_modelo():

    global modelo
    global controlador

    if modelo is None:

        modelo = ModeloMortalidad()

        controlador = ControladorMortalidad(
            modelo
        )

# =========================================================
# OPCIONES
# =========================================================
inicializar_modelo()

departamentos = ["TODOS"] + sorted(
    modelo.df["DES_DEPARTAMENTO"]
    .dropna()
    .unique()
)

edades = ["TODOS"] + sorted(
    modelo.df["RANGO_EDAD"]
    .dropna()
    .unique()
)

sexos = [
    "TODOS",
    "Masculino",
    "Femenino",
    "Indeterminado"
]

enfermedades = ["TODOS"] + sorted(
    modelo.df["DESCRIPCION__MUERTE"]
    .dropna()
    .unique()
)

# =========================================================
# LAYOUT
# =========================================================

app.layout = dbc.Container([

    # =====================================================
    # BANNER
    # =====================================================

    html.Div([

        html.H1(

            "Dashboard Mortalidad Colombia (2019)",

            style={
                "color":"white",
                "fontWeight":"bold"
            }
        ),

        html.H4(

            "Analítica Visual Interactiva",

            style={
                "color":"#dfe6e9"
            }
        ),

        html.H3(

            """Aplicaciones I - Maestría en Inteligencia Artificial - Grupo I
            Actividad 4: 4: Aplicación web interactiva para el análisis de mortalidad en Colombia  
            Nombre del profesor: Cristian Duney Bérmudez Quintero - Fecha: Mayo 11 de 2026""",

            style={
                "color":"#dfe6e9"
            }
        )

    ],

    style={

        "background":
            "linear-gradient(90deg,#1e3c72,#2a5298)",

        "padding":"30px",

        "borderRadius":"15px",

        "marginTop":"20px",

        "marginBottom":"25px",

        "boxShadow":
            "0 4px 15px rgba(0,0,0,0.2)"
    }),

    # =====================================================
    # KPI
    # =====================================================

    dbc.Card([

        dbc.CardBody([

            html.H4("Total Muertes"),

            html.H1(

                id="titulo_total_muertes",

                style={

                    "color":"#c0392b",

                    "fontWeight":"bold",

                    "fontSize":"45px"
                }
            )
        ])

    ],

    style={

        "borderRadius":"15px",

        "marginBottom":"25px",

        "boxShadow":
            "0 4px 12px rgba(0,0,0,0.12)"
    }),

    # =====================================================
    # FILTROS
    # =====================================================

    dbc.Card([

        dbc.CardBody([

            html.H4("Filtros"),

            dbc.Row([

                dbc.Col([

                    html.Label("Departamento"),

                    dcc.Dropdown(

                        id="filtro_departamento",

                        options=[
                            {
                                "label":d,
                                "value":d
                            }
                            for d in departamentos
                        ],

                        value="TODOS"
                    )

                ], md=3),

                dbc.Col([

                    html.Label("Edad"),

                    dcc.Dropdown(

                        id="filtro_edad",

                        options=[
                            {
                                "label":e,
                                "value":e
                            }
                            for e in edades
                        ],

                        value="TODOS"
                    )

                ], md=3),

                dbc.Col([

                    html.Label("Sexo"),

                    dcc.Dropdown(

                        id="filtro_sexo",

                        options=[
                            {
                                "label":s,
                                "value":s
                            }
                            for s in sexos
                        ],

                        value="TODOS"
                    )

                ], md=3),

                dbc.Col([

                    html.Label("Enfermedad"),

                    dcc.Dropdown(

                        id="filtro_enfermedad",

                        options=[
                            {
                                "label":e,
                                "value":e
                            }
                            for e in enfermedades
                        ],

                        value="TODOS"
                    )

                ], md=3)

            ])

        ])

    ],

    style={

        "borderRadius":"15px",

        "marginBottom":"25px",

        "boxShadow":
            "0 4px 10px rgba(0,0,0,0.1)"
    }),

    # =====================================================
    # MAPA
    # =====================================================

    dbc.Card([

        dbc.CardBody([

            dcc.Loading(

                type="circle",

                children=[
                    dcc.Graph(id="grafico_mapa")
                ]
            )

        ])

    ],

    style={

        "marginBottom":"25px",

        "borderRadius":"15px",

        "boxShadow":
            "0 4px 12px rgba(0,0,0,0.1)"
    }),

    # =====================================================
    # GRAFICOS
    # =====================================================

    dbc.Row([

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(id="grafico_linea")

                ])

            ],

            style={

                "borderRadius":"15px",

                "boxShadow":
                    "0 4px 10px rgba(0,0,0,0.1)"
            })

        ], md=6),

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(id="grafico_homicidios")

                ])

            ],

            style={

                "borderRadius":"15px",

                "boxShadow":
                    "0 4px 10px rgba(0,0,0,0.1)"
            })

        ], md=6)

    ],

    className="mb-4"),

    dbc.Row([

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(id="grafico_torta")

                ])

            ],

            style={

                "borderRadius":"15px",

                "boxShadow":
                    "0 4px 10px rgba(0,0,0,0.1)"
            })

        ], md=6),

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(id="grafico_sexo")

                ])

            ],

            style={

                "borderRadius":"15px",

                "boxShadow":
                    "0 4px 10px rgba(0,0,0,0.1)"
            })

        ], md=6)

    ],

    className="mb-4"),

    dbc.Card([

        dbc.CardBody([

            dcc.Graph(id="grafico_histograma")

        ])

    ],

    style={

        "marginBottom":"25px",

        "borderRadius":"15px",

        "boxShadow":
            "0 4px 10px rgba(0,0,0,0.1)"
    }),

    # =====================================================
    # TABLA
    # =====================================================

    dbc.Card([

        dbc.CardBody([

            html.H4(
                "Principales Causas de Muerte"
            ),

            dash_table.DataTable(

                id="tabla_causas",

                page_size=10,

                style_table={
                    "overflowX":"auto"
                },

                style_header={

                    "backgroundColor":"#1d3557",

                    "color":"white",

                    "fontWeight":"bold"
                },

                style_cell={

                    "textAlign":"left",

                    "padding":"10px"
                }
            )

        ])

    ],

    style={

        "marginBottom":"40px",

        "borderRadius":"15px",

        "boxShadow":
            "0 4px 10px rgba(0,0,0,0.1)"
    })

],

fluid=True,

style={

    "backgroundColor":"#eef2f7",

    "fontFamily":"Segoe UI"
})

# =========================================================
# CALLBACK
# =========================================================

@app.callback(

    [

        Output(
            "titulo_total_muertes",
            "children"
        ),

        Output(
            "grafico_mapa",
            "figure"
        ),

        Output(
            "grafico_linea",
            "figure"
        ),

        Output(
            "grafico_homicidios",
            "figure"
        ),

        Output(
            "grafico_torta",
            "figure"
        ),

        Output(
            "grafico_sexo",
            "figure"
        ),

        Output(
            "grafico_histograma",
            "figure"
        ),

        Output(
            "tabla_causas",
            "data"
        ),

        Output(
            "tabla_causas",
            "columns"
        )
    ],

    [

        Input(
            "filtro_departamento",
            "value"
        ),

        Input(
            "filtro_edad",
            "value"
        ),

        Input(
            "filtro_sexo",
            "value"
        ),

        Input(
            "filtro_enfermedad",
            "value"
        )
    ]
)

def actualizar_dashboard(
    departamento,
    edad,
    sexo,
    enfermedad
):
    inicializar_modelo()
    df_filtrado = controlador.filtrar_datos(

        departamento,

        edad,

        sexo,

        enfermedad
    )

    tabla = controlador.crear_tabla(df_filtrado)

    return (

        f"{len(df_filtrado):,}",

        controlador.crear_mapa(df_filtrado),

        controlador.crear_linea(df_filtrado),

        controlador.crear_homicidios(df_filtrado),

        controlador.crear_torta(df_filtrado),

        controlador.crear_sexo(df_filtrado),

        controlador.crear_histograma(df_filtrado),

        tabla.to_dict("records"),

        [
            {
                "name":c,
                "id":c
            }
            for c in tabla.columns
        ]
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app.run(debug=False)
