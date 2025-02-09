import streamlit as st
import plotly.graph_objects as go
from sympy import mod_inverse, isprime
from streamlit_plotly_events import plotly_events


def elliptic_curve_points(a, b, p):
    points = []
    for x in range(p):
        y2 = (x**3 + a*x + b) % p
        for y in range(p):
            if (y * y) % p == y2:
                points.append((x, y))
    return points


def point_addition(P, Q, a, p):
    if P == Q:
        if P[1] == 0:
            return None
        lam = ((3 * P[0] ** 2 + a) * mod_inverse(2 * P[1], p)) % p
    else:
        if P[0] == Q[0]:
            return None
        lam = ((Q[1] - P[1]) * mod_inverse(Q[0] - P[0], p)) % p

    x_r = (lam ** 2 - P[0] - Q[0]) % p
    y_r = (lam * (P[0] - x_r) - P[1]) % p
    return x_r, y_r


def scalar_multiplication(G, n, a, p):
    R = G
    steps = [(None, G, "G")]
    for _ in range(n - 1):
        prev_R = R
        R = point_addition(R, G, a, p)
        if R is None:
            break
        steps.append((prev_R, R, "Adição"))
    return steps


st.title("ECC - Visualização")

st.text("Fórmula: y^2 = x^3 + ax + b mod p")

a = st.number_input("Insira 'a'", value=2, step=1)
b = st.number_input("Insira 'b'", value=2, step=1)
p = st.number_input("Insira um primo 'p'", value=17, step=1)

if not isprime(p):
    st.warning("O valor de 'p' deve ser um número primo!")
else:
    if st.button("Gerar Curva"):
        points = elliptic_curve_points(a, b, p)
        st.session_state.points = points
        st.session_state.step = 0
        st.session_state.G = None
        st.session_state.steps = []
        st.session_state.lines = []

    if "points" in st.session_state:
        fig = go.Figure()
        x_vals, y_vals = zip(*st.session_state.points)
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers',
                      marker=dict(color='blue'), name='Pontos'))
        fig.update_layout(title=f"Curva Elíptica: y^2 = x^3 + {a}x + {b} mod {p}", xaxis=dict(range=[0, p]), yaxis=dict(range=[0, p]),
                          clickmode='event+select')

        selected_points = plotly_events(fig, click_event=True)

        if selected_points:
            x_click, y_click = selected_points[0]['x'], selected_points[0]['y']
            st.session_state.G = (int(x_click), int(y_click))

        if st.session_state.G:
            st.write(f"Ponto G selecionado: {st.session_state.G}")
            n = st.number_input("Insira o valor de 'n'", value=2, step=1)

            if n >= p:
                st.warning("O valor de 'n' deve ser menor que 'p'!")
            else:
                if st.button("Começar multiplicação"):
                    st.session_state.steps = scalar_multiplication(
                        st.session_state.G, n, a, p)
                    st.session_state.step = 0
                    st.session_state.lines = []

                if "steps" in st.session_state and st.session_state.steps:
                    step = st.session_state.step
                    if step < len(st.session_state.steps):
                        prev_point, current_point, operation = st.session_state.steps[step]
                        st.write(
                            f"Passo {step + 1}: {operation} -> {current_point}")

                        if prev_point:
                            st.session_state.lines.append(
                                (prev_point, current_point, operation))

                    else:
                        st.write("Resultado final: " +
                                 str(st.session_state.steps[-1][1]) + ".")

                for prev_point, current_point, operation in st.session_state.lines:
                    fig.add_trace(go.Scatter(x=[prev_point[0], current_point[0]], y=[prev_point[1], current_point[1]],
                                             mode='lines', line=dict(color='red', width=2), name=operation))

                if "steps" in st.session_state and len(st.session_state.steps) > 0 and st.session_state.step >= len(st.session_state.steps) - 1:
                    final_point = st.session_state.steps[-1][1]
                    fig.add_trace(go.Scatter(x=[final_point[0]], y=[final_point[1]], mode='markers',
                                             marker=dict(color='green', size=10), name='Final Point'))

                if st.button("Próximo passo") and "steps" in st.session_state and st.session_state.step < len(st.session_state.steps) - 1:
                    st.session_state.step += 1
                    st.rerun()

        st.plotly_chart(fig, use_container_width=True)
