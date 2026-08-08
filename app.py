```python
import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------

st.set_page_config(
    page_title="Ensayos Danzas – Economía",
    page_icon="💃",
    layout="wide"
)

# ---------------------------------------------------------
# DÍAS Y HORARIOS
# ---------------------------------------------------------

DAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado"
]

TIMES = []

for h in range(7, 22):
    for m in (0, 30):

        start = f"{h:02d}:{m:02d}"

        if m == 0:
            end_h = h
            end_m = 30
        else:
            end_h = h + 1
            end_m = 0

        end = f"{end_h:02d}:{end_m:02d}"

        TIMES.append(f"{start} - {end}")


# ---------------------------------------------------------
# GUARDAR RESPUESTAS TEMPORALMENTE
# ---------------------------------------------------------

if "responses" not in st.session_state:
    st.session_state.responses = []


# ---------------------------------------------------------
# TÍTULO
# ---------------------------------------------------------

st.title("💃 Ensayos Danzas – Economía")

st.markdown(
    """
    ### 📅 Encuesta de horas ocupadas

    Marca **únicamente las horas en las que estás OCUPADO/A
    y NO puedes asistir a un ensayo**.

    💡 Las horas que dejes sin marcar son horarios en los que
    no has indicado que estés ocupado/a.
    """
)


# ---------------------------------------------------------
# PESTAÑAS
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "📝 Registrar mis horarios",
        "🔥 Mapa de ocupación",
        "📊 Resultados"
    ]
)


# =========================================================
# TAB 1 — REGISTRAR HORARIOS
# =========================================================

with tab1:

    st.subheader("👤 Datos del participante")

    name = st.text_input(
        "Tu nombre completo",
        placeholder="Ej. Valeria Fernanda"
    )

    st.subheader("⏰ Marca tus horas OCUPADAS")

    st.info(
        "❌ Marca las casillas de los horarios en los que "
        "NO puedes ensayar."
    )

    st.caption(
        "No marques las horas en las que sí podrías ensayar."
    )

    # -----------------------------------------------------
    # TABLA DE HORARIOS
    # -----------------------------------------------------

    selected = {}

    header = st.columns([1.5] + [1] * len(DAYS))

    header[0].write("**Hora**")

    for i, day in enumerate(DAYS):
        header[i + 1].write(f"**{day}**")

    for time in TIMES:

        cols = st.columns([1.5] + [1] * len(DAYS))

        cols[0].write(time)

        for i, day in enumerate(DAYS):

            selected[(day, time)] = cols[i + 1].checkbox(
                "",
                key=f"ocupado_{day}_{time}"
            )


    # -----------------------------------------------------
    # BOTÓN ENVIAR
    # -----------------------------------------------------

    if st.button(
        "🚀 Enviar mis horarios",
        type="primary",
        use_container_width=True
    ):

        # Verificar nombre

        if not name.strip():

            st.error(
                "Por favor, ingresa tu nombre."
            )

        else:

            # Eliminar respuesta anterior de la misma persona

            st.session_state.responses = [
                r
                for r in st.session_state.responses
                if r["Nombre"].strip().lower()
                != name.strip().lower()
            ]

            # Registrar solamente las horas ocupadas

            occupied_count = 0

            for (day, time), occupied in selected.items():

                if occupied:

                    st.session_state.responses.append(
                        {
                            "Nombre": name.strip(),
                            "Día": day,
                            "Hora": time,
                            "Estado": "Ocupado",
                            "Fecha": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        }
                    )

                    occupied_count += 1

            st.success(
                f"✅ ¡Listo, {name.strip()}! "
                f"Se registraron {occupied_count} horarios ocupados."
            )

            st.info(
                "Puedes volver a enviar tus horarios si necesitas modificarlos."
            )


# =========================================================
# TAB 2 — MAPA DE OCUPACIÓN
# =========================================================

with tab2:

    st.subheader("🔥 Mapa de ocupación")

    if not st.session_state.responses:

        st.info(
            "Todavía no hay respuestas registradas."
        )

    else:

        df = pd.DataFrame(
            st.session_state.responses
        )

        # Contar personas ocupadas

        counts = (
            df.groupby(["Hora", "Día"])
            .size()
            .unstack(fill_value=0)
        )

        # Asegurar orden correcto

        counts = counts.reindex(
            index=TIMES,
            columns=DAYS,
            fill_value=0
        )

        st.caption(
            "Cada número representa cuántas personas están "
            "ocupadas en ese horario."
        )

        st.dataframe(
            counts,
            use_container_width=True
        )


# =========================================================
# TAB 3 — RESULTADOS
# =========================================================

with tab3:

    st.subheader("📊 Resultados")

    if not st.session_state.responses:

        st.info(
            "Todavía no hay respuestas registradas."
        )

    else:

        df = pd.DataFrame(
            st.session_state.responses
        )

        # -------------------------------------------------
        # TOTAL DE PARTICIPANTES
        # -------------------------------------------------

        total_participantes = df["Nombre"].nunique()

        st.metric(
            "👥 Participantes registrados",
            total_participantes
        )

        st.divider()

        # -------------------------------------------------
        # RANKING DE HORARIOS
        # -------------------------------------------------

        st.subheader(
            "🟢 Horarios con menos personas ocupadas"
        )

        ranking = (
            df.groupby(["Día", "Hora"])
            .size()
            .reset_index(
                name="Personas ocupadas"
            )
        )

        # Crear todas las combinaciones
        # para que también aparezcan horarios
        # con CERO personas ocupadas.

        all_slots = pd.MultiIndex.from_product(
            [DAYS, TIMES],
            names=["Día", "Hora"]
        ).to_frame(index=False)

        ranking = all_slots.merge(
            ranking,
            on=["Día", "Hora"],
            how="left"
        )

        ranking["Personas ocupadas"] = (
            ranking["Personas ocupadas"]
            .fillna(0)
            .astype(int)
        )

        # Ordenar de MENOS ocupados
        # a MÁS ocupados

        ranking = ranking.sort_values(
            by="Personas ocupadas",
            ascending=True
        )

        st.dataframe(
            ranking.head(30),
            use_container_width=True,
            hide_index=True
        )

        st.success(
            "💡 Los primeros horarios son los que tienen "
            "menos personas ocupadas."
        )

        st.divider()

        # -------------------------------------------------
        # PERSONAS OCUPADAS POR HORARIO
        # -------------------------------------------------

        st.subheader(
            "👥 ¿Quiénes están ocupados?"
        )

        selected_day = st.selectbox(
            "Selecciona un día",
            DAYS
        )

        selected_time = st.selectbox(
            "Selecciona un horario",
            TIMES
        )

        occupied_people = df[
            (df["Día"] == selected_day)
            &
            (df["Hora"] == selected_time)
        ]["Nombre"].unique()

        if len(occupied_people) == 0:

            st.success(
                "🎉 Nadie indicó estar ocupado en este horario."
            )

        else:

            st.warning(
                f"Hay {len(occupied_people)} persona(s) "
                "ocupada(s):"
            )

            for person in occupied_people:

                st.write(
                    f"❌ {person}"
                )
```
