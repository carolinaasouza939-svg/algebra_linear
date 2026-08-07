import os
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Álgebra Linear", page_icon="🧮", layout="wide")

# ----------------------------------------------------------------------------
# ESTADO GLOBAL
# ----------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # lista de dicts {"role": ..., "content": ...}

if "api_key_manual" not in st.session_state:
    st.session_state.api_key_manual = ""

TOPICOS = [
    "1. Vetores (2D e 3D)",
    "2. Operações com Vetores",
    "3. Produto Escalar e Vetorial",
    "4. Dependência Linear (LI e LD)",
    "5. Matrizes, Determinantes e Inversa",
    "6. Sistemas de Equações Lineares",
    "7. Transformações Lineares",
    "8. Projeção Ortogonal",
    "9. Autovalores e Autovetores",
    "10. SVD (Decomposição em Valores Singulares)",
]


def get_api_key():
    """
    Procura a chave de API na seguinte ordem de prioridade:
    1. st.secrets["ANTHROPIC_API_KEY"]  -> configurada pelo dono do app (recomendado)
    2. variável de ambiente ANTHROPIC_API_KEY
    3. chave digitada manualmente pelo usuário na sessão (fallback)
    """
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"], True
    except Exception:
        pass
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if env_key:
        return env_key, True
    return st.session_state.api_key_manual, False


# ----------------------------------------------------------------------------
# BANCO DE QUESTÕES DOS QUIZZES
# Cada questão: (enunciado, [opções], índice_correto, explicação)
# ----------------------------------------------------------------------------
QUIZZES = {
    "1. Vetores (2D e 3D)": [
        (
            "O que um vetor representa, além de uma quantidade (módulo)?",
            ["Cor e textura", "Direção e sentido", "Apenas posição no espaço", "Tempo decorrido"],
            1,
            "Um vetor carrega módulo, direção e sentido — é isso que o diferencia de um escalar.",
        ),
        (
            "Qual é o módulo do vetor v = (6, 8)?",
            ["14", "10", "48", "7"],
            1,
            "||v|| = √(6² + 8²) = √(36+64) = √100 = 10.",
        ),
        (
            "Um vetor em R³ é representado por quantas componentes?",
            ["1", "2", "3", "4"],
            2,
            "Em R³ o vetor tem três componentes: x, y e z.",
        ),
    ],
    "2. Operações com Vetores": [
        (
            "Se u = (2, 3) e v = (4, -1), quanto vale u + v?",
            ["(6, 2)", "(2, 4)", "(-2, 4)", "(8, -3)"],
            0,
            "Somamos componente a componente: (2+4, 3+(-1)) = (6, 2).",
        ),
        (
            "Multiplicar um vetor por um escalar negativo faz o quê com ele?",
            ["Aumenta o módulo apenas", "Inverte o sentido", "Não muda nada", "Transforma em matriz"],
            1,
            "Um escalar negativo inverte o sentido do vetor (e também pode mudar seu tamanho).",
        ),
        (
            "Geometricamente, a soma de vetores é ilustrada pela regra:",
            ["Do determinante", "Do paralelogramo (ponta com cauda)", "Da matriz inversa", "Do produto vetorial"],
            1,
            "A regra do paralelogramo (ou 'ponta com cauda') mostra visualmente a soma de vetores.",
        ),
    ],
    "3. Produto Escalar e Vetorial": [
        (
            "Se u · v = 0, o que podemos concluir sobre u e v?",
            ["São paralelos", "São ortogonais (perpendiculares)", "Têm o mesmo módulo", "São o mesmo vetor"],
            1,
            "Produto escalar igual a zero indica que os vetores são perpendiculares entre si.",
        ),
        (
            "O produto vetorial (u × v) resulta em:",
            ["Um número (escalar)", "Um vetor perpendicular a u e v", "Uma matriz", "Um ângulo"],
            1,
            "O produto vetorial produz um novo vetor, perpendicular aos dois vetores originais.",
        ),
        (
            "O produto vetorial é definido em qual espaço?",
            ["Apenas em R²", "Apenas em R³", "Em qualquer dimensão", "Só para matrizes quadradas"],
            1,
            "O produto vetorial clássico só é definido em R³.",
        ),
    ],
    "4. Dependência Linear (LI e LD)": [
        (
            "Se det([u v]) = 0, os vetores u e v são:",
            ["Linearmente Independentes (LI)", "Linearmente Dependentes (LD)", "Ortogonais", "Unitários"],
            1,
            "Determinante zero significa que os vetores estão na mesma reta — são LD.",
        ),
        (
            "Dois vetores LI em R² formam entre si:",
            ["Uma reta", "Um plano (área diferente de zero)", "Um ponto", "Um círculo"],
            1,
            "Vetores LI 'abrem' uma área — juntos conseguem gerar todo o plano R².",
        ),
        (
            "Se v = 3u, então u e v são:",
            ["LI", "LD", "Ortogonais", "Impossível saber"],
            1,
            "Como v é múltiplo escalar de u, eles apontam na mesma reta: são LD.",
        ),
    ],
    "5. Matrizes, Determinantes e Inversa": [
        (
            "Quando uma matriz NÃO possui inversa?",
            ["Quando o determinante é diferente de zero", "Quando o determinante é igual a zero", "Quando é 2x2", "Sempre possui"],
            1,
            "Se det(A) = 0, a matriz é singular e não tem inversa.",
        ),
        (
            "O determinante de uma matriz 2x2 [[a,b],[c,d]] é calculado por:",
            ["a+d - b-c", "ad - bc", "ab - cd", "ac - bd"],
            1,
            "det = ad - bc (produto da diagonal principal menos produto da diagonal secundária).",
        ),
        (
            "Multiplicar uma matriz A pela sua inversa A⁻¹ resulta em:",
            ["A matriz nula", "A matriz identidade", "O determinante", "A transposta"],
            1,
            "Por definição, A · A⁻¹ = I, a matriz identidade.",
        ),
    ],
    "6. Sistemas de Equações Lineares": [
        (
            "Geometricamente, cada equação de um sistema linear 2x2 representa:",
            ["Um ponto", "Uma reta", "Uma parábola", "Um círculo"],
            1,
            "Cada equação linear com duas variáveis descreve uma reta no plano.",
        ),
        (
            "Quando duas retas de um sistema são paralelas e distintas, o sistema tem:",
            ["Solução única", "Infinitas soluções", "Nenhuma solução", "Duas soluções"],
            2,
            "Retas paralelas nunca se cruzam, então não há solução.",
        ),
        (
            "Se det(A) ≠ 0 no sistema Ax = b, a solução pode ser obtida por:",
            ["x = A + b", "x = A⁻¹b", "x = det(A) · b", "Não existe solução"],
            1,
            "Quando A é invertível, isolamos x multiplicando por A⁻¹: x = A⁻¹b.",
        ),
    ],
    "7. Transformações Lineares": [
        (
            "As colunas da matriz A de uma transformação linear representam:",
            ["Os autovalores", "Para onde vão os vetores da base canônica (i, j)", "O determinante", "A inversa"],
            1,
            "Aplicar A aos vetores i=(1,0) e j=(0,1) dá exatamente as colunas de A.",
        ),
        (
            "Qual matriz representa uma rotação de 90° anti-horária?",
            ["[[1,0],[0,1]]", "[[0,-1],[1,0]]", "[[1,1],[0,1]]", "[[-1,0],[0,-1]]"],
            1,
            "[[0,-1],[1,0]] leva (1,0) em (0,1) e (0,1) em (-1,0) — rotação de 90°.",
        ),
        (
            "O determinante de uma transformação linear indica:",
            ["A cor da figura", "O fator de mudança de área", "O número de dimensões", "Sempre 1"],
            1,
            "O determinante mede quanto a área (ou volume) é ampliada ou reduzida pela transformação.",
        ),
    ],
    "8. Projeção Ortogonal": [
        (
            "A projeção de v sobre u representa:",
            ["A soma dos dois vetores", "A 'sombra' de v na direção de u", "O produto vetorial", "O determinante"],
            1,
            "A projeção ortogonal é como a sombra que v projeta sobre a reta gerada por u.",
        ),
        (
            "O vetor erro (v menos sua projeção) é sempre:",
            ["Paralelo a u", "Perpendicular a u", "Igual a v", "Igual a zero"],
            1,
            "O erro ortogonal é sempre perpendicular ao vetor base u — essa é a base dos mínimos quadrados.",
        ),
        (
            "A fórmula da projeção de v sobre u é:",
            ["(v·u / u·u) · u", "(v·u) · v", "(u·u / v·v) · v", "v - u"],
            0,
            "proj_u(v) = (v·u / u·u) · u.",
        ),
    ],
    "9. Autovalores e Autovetores": [
        (
            "Um autovetor de A satisfaz qual equação?",
            ["A + v = λ", "Av = λv", "A · λ = v", "v = A⁻¹"],
            1,
            "Por definição, Av = λv, onde λ é o autovalor associado.",
        ),
        (
            "Para encontrar os autovalores, resolvemos:",
            ["det(A) = 0", "det(A - λI) = 0", "A · I = 0", "tr(A) = λ"],
            1,
            "A equação característica é det(A - λI) = 0.",
        ),
        (
            "Em uma matriz diagonal, os autovalores são:",
            ["Sempre iguais a 1", "Os próprios elementos da diagonal", "Sempre zero", "Impossíveis de calcular"],
            1,
            "Para matrizes diagonais, cada elemento da diagonal já é um autovalor.",
        ),
    ],
    "10. SVD (Decomposição em Valores Singulares)": [
        (
            "A decomposição SVD escreve A como:",
            ["A = U + Σ + V", "A = U Σ V^T", "A = Σ / U", "A = U⁻¹V"],
            1,
            "A SVD é A = U Σ V^T, onde U e V são rotações/reflexões e Σ é escalonamento.",
        ),
        (
            "Os valores singulares (em Σ) são sempre:",
            ["Negativos", "Não negativos", "Iguais a 1", "Complexos"],
            1,
            "Os valores singulares são sempre maiores ou iguais a zero, por definição.",
        ),
        (
            "O SVD pode ser aplicado a:",
            ["Apenas matrizes quadradas", "Apenas matrizes 2x2", "Qualquer matriz, quadrada ou não", "Apenas vetores"],
            2,
            "Uma das grandes vantagens do SVD é que ele existe para qualquer matriz, mesmo retangular.",
        ),
    ],
}


def renderizar_quiz(topico_nome):
    perguntas = QUIZZES.get(topico_nome, [])
    if not perguntas:
        st.info("Quiz em breve para este tópico.")
        return

    st.markdown("Responda as perguntas abaixo e clique em **Corrigir** para ver seu resultado.")
    chave_base = topico_nome.replace(" ", "_")

    with st.form(key=f"form_{chave_base}"):
        respostas = []
        for i, (pergunta, opcoes, _, _) in enumerate(perguntas):
            resp = st.radio(f"**{i+1}. {pergunta}**", opcoes, index=None, key=f"{chave_base}_q{i}")
            respostas.append(resp)
        enviado = st.form_submit_button("✅ Corrigir")

    if enviado:
        acertos = 0
        for i, (pergunta, opcoes, correta_idx, explicacao) in enumerate(perguntas):
            resposta_usuario = respostas[i]
            if resposta_usuario is None:
                st.warning(f"Questão {i+1}: você não respondeu.")
                continue
            if opcoes[correta_idx] == resposta_usuario:
                acertos += 1
                st.success(f"Questão {i+1}: correto! ✅ {explicacao}")
            else:
                st.error(f"Questão {i+1}: incorreto. A resposta certa é **{opcoes[correta_idx]}**. {explicacao}")

        total = len(perguntas)
        st.markdown(f"### Resultado: {acertos} de {total} corretas")
        if acertos == total:
            st.balloons()


# ----------------------------------------------------------------------------
# CABEÇALHO
# ----------------------------------------------------------------------------
st.title("🧮 Álgebra Linear — Professor Assistente")
st.markdown(
    "Estude Álgebra Linear com teoria, exemplos resolvidos, gráficos interativos, quizzes "
    "e um assistente de IA para tirar suas dúvidas a qualquer momento."
)

with st.expander("📖 Como usar esta ferramenta (clique para ler)"):
    st.markdown(
        """
Bem-vindo(a)! Esta ferramenta foi feita para funcionar como um **professor assistente** de
Álgebra Linear, cobrindo os 10 tópicos centrais de um curso universitário.

### 📚 Como cada tópico funciona
Cada assunto tem quatro abas:
* **📖 Teoria** — a explicação do conceito, a intuição por trás dele e as fórmulas importantes.
* **🎮 Interativo** — gráficos e controles para você mexer nos valores e ver o que acontece.
* **✅ Exemplo Resolvido** — um problema completo, resolvido passo a passo.
* **🧠 Quiz** — perguntas de múltipla escolha com correção automática, para testar o que você
  aprendeu.

### 🙋 Tirando dúvidas
No canto inferior da barra lateral existe um **chat com um assistente de IA**. Ele sabe em qual
tópico você está estudando e pode responder perguntas, explicar de outro jeito, ou propor
exercícios extras.

Para usar o chat, você vai precisar colar uma **chave de API gratuita** da Anthropic (é grátis
para criar e costuma vir com créditos de teste). A barra lateral tem um passo a passo completo
de como conseguir a sua. Isso existe porque cada pergunta ao assistente tem um custo mínimo de
processamento — usando sua própria chave, você usa por sua conta, sem depender de ninguém.

### 📱 Dicas de navegação dos gráficos
* Faça o gesto de "pinça" (ou use o scroll) para dar zoom.
* Toque e arraste para mover a visão.
* Nos gráficos 3D, toque e gire para ver o espaço por todos os ângulos!
        """
    )

# ----------------------------------------------------------------------------
# BARRA LATERAL: NAVEGAÇÃO + CHAT COM O TUTOR
# ----------------------------------------------------------------------------
st.sidebar.title("📚 Tópicos de Estudo")
topico = st.sidebar.radio("Navegação:", TOPICOS)

st.sidebar.divider()
st.sidebar.title("🙋 Tire suas dúvidas")

api_key, chave_configurada_pelo_dono = get_api_key()

if not chave_configurada_pelo_dono:
    with st.sidebar.expander("⚙️ Ativar o assistente de IA (gratuito p/ você)", expanded=True):
        st.markdown(
            """
Para conversar com o assistente, você usa a **sua própria chave de API gratuita** da
Anthropic (a empresa que faz a IA Claude). Isso não custa nada para quem criou este app —
o uso fica só na sua conta, e novas contas costumam vir com créditos de teste.

**Passo a passo (leva ~2 minutos):**
1. Acesse [console.anthropic.com](https://console.anthropic.com) e crie uma conta gratuita
   (pode usar login do Google).
2. No menu, vá em **Settings → API Keys** (ou acesse direto
   [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)).
3. Clique em **Create Key**, dê um nome (ex: "algebra-linear") e copie a chave gerada —
   ela começa com `sk-ant-...`.
4. Cole a chave no campo abaixo.

🔒 A chave fica **apenas na sua sessão do navegador** — não é salva em nenhum servidor ou
banco de dados, e some quando você fecha a aba.
            """
        )
        st.session_state.api_key_manual = st.text_input(
            "Cole sua API Key da Anthropic aqui", value=st.session_state.api_key_manual, type="password"
        )
    api_key, _ = get_api_key()

if not api_key:
    st.sidebar.info(
        "O assistente de IA ainda não está disponível nesta instância. "
        "Você ainda pode usar toda a parte de teoria, exemplos, gráficos e quizzes normalmente."
    )
else:
    chat_container = st.sidebar.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    pergunta = st.sidebar.chat_input(f"Pergunte sobre '{topico}'...")

    if pergunta:
        st.session_state.chat_history.append({"role": "user", "content": pergunta})

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = (
                "Você é um professor de Álgebra Linear, paciente e didático, ajudando um "
                "estudante universitário dentro de um aplicativo de estudos. "
                f"O aluno está atualmente estudando o tópico: '{topico}'. "
                "Responda em português do Brasil, de forma clara e objetiva. "
                "Use LaTeX entre símbolos de $ para fórmulas quando fizer sentido. "
                "Prefira explicações com intuição geométrica, e quando possível, sugira "
                "que o aluno experimente valores no gráfico interativo do aplicativo para "
                "visualizar o conceito, ou tente o quiz do tópico. Se o aluno pedir um "
                "exercício, proponha um e pergunte se ele quer a resposta ou uma dica primeiro."
            )

            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_history
            ]

            with chat_container:
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    resposta_completa = ""
                    with client.messages.stream(
                        model="claude-sonnet-4-6",
                        max_tokens=1024,
                        system=system_prompt,
                        messages=api_messages,
                    ) as stream:
                        for text in stream.text_stream:
                            resposta_completa += text
                            placeholder.markdown(resposta_completa + "▌")
                    placeholder.markdown(resposta_completa)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": resposta_completa}
            )
            st.rerun()

        except ImportError:
            st.sidebar.error(
                "A biblioteca `anthropic` não está instalada. Rode `pip install anthropic` "
                "no ambiente onde este app está sendo executado."
            )
        except Exception as e:
            st.sidebar.error(f"Não foi possível falar com o assistente: {e}")

    if st.sidebar.button("🗑️ Limpar conversa"):
        st.session_state.chat_history = []
        st.rerun()

# ----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES DE GRÁFICO
# ----------------------------------------------------------------------------
def criar_grafico_2d(max_val):
    fig = go.Figure()
    fig.update_layout(
        xaxis=dict(range=[-max_val, max_val], zeroline=True, zerolinewidth=2, zerolinecolor="black"),
        yaxis=dict(range=[-max_val, max_val], zeroline=True, zerolinewidth=2, zerolinecolor="black"),
        width=400, height=400, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
    )
    return fig


def add_vetor_2d(fig, x, y, cor, nome, tracejado=False):
    fig.add_annotation(
        x=x, y=y, ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3, arrowcolor=cor, text=nome,
    )


def teoria_intro(texto):
    st.markdown(texto)


# ----------------------------------------------------------------------------
# TÓPICO 1 — VETORES
# ----------------------------------------------------------------------------
if topico == "1. Vetores (2D e 3D)":
    st.header("1. Representação de Vetores")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
Um **vetor** é uma grandeza que possui **módulo (tamanho)**, **direção** e **sentido**.
Diferente de um número comum (escalar), um vetor não representa só "quanto", mas também
"para onde".

Representamos um vetor em $\mathbb{R}^2$ como um par ordenado:

$$\vec{v} = \begin{bmatrix} x \\ y \end{bmatrix}$$

e em $\mathbb{R}^3$ como um trio ordenado:

$$\vec{v} = \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

Geometricamente, desenhamos o vetor como uma seta que sai da origem $(0,0)$ (ou $(0,0,0)$)
e termina no ponto indicado pelas coordenadas.

### Módulo (norma) do vetor
O módulo mede o "comprimento" da seta e é calculado com o Teorema de Pitágoras generalizado:

$$||\vec{v}|| = \sqrt{x^2 + y^2} \quad \text{(2D)} \qquad ||\vec{v}|| = \sqrt{x^2 + y^2 + z^2} \quad \text{(3D)}$$

### Por que isso importa?
Vetores aparecem sempre que precisamos representar algo que tem direção: velocidade, força,
deslocamento, ou até mesmo dados em Machine Learning (um vetor de características).
            """
        )

    with aba_interativo:
        dim = st.radio("Escolha a dimensão:", ["2D (Plano)", "3D (Espaço)"])
        if dim == "2D (Plano)":
            c1, c2 = st.columns(2)
            with c1:
                x = st.slider("X", -10.0, 10.0, 3.0)
            with c2:
                y = st.slider("Y", -10.0, 10.0, 4.0)
            fig = criar_grafico_2d(10)
            add_vetor_2d(fig, x, y, "blue", "v")
            st.plotly_chart(fig, use_container_width=True)
            st.latex(rf"\vec{{v}} = \begin{{bmatrix}} {x} \\ {y} \end{{bmatrix}}, \quad ||\vec{{v}}|| = {np.sqrt(x**2+y**2):.2f}")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                x = st.slider("X", -10.0, 10.0, 3.0)
            with c2:
                y = st.slider("Y", -10.0, 10.0, 4.0)
            with c3:
                z = st.slider("Z", -10.0, 10.0, 5.0)
            fig = go.Figure(data=[go.Scatter3d(x=[0, x], y=[0, y], z=[0, z], mode="lines+markers", line=dict(color="blue", width=5))])
            fig.update_layout(scene=dict(xaxis=dict(range=[-10, 10]), yaxis=dict(range=[-10, 10]), zaxis=dict(range=[-10, 10])), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)
            st.latex(rf"\vec{{v}} = \begin{{bmatrix}} {x} \\ {y} \\ {z} \end{{bmatrix}}, \quad ||\vec{{v}}|| = {np.sqrt(x**2+y**2+z**2):.2f}")

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Calcule o módulo do vetor $\vec{v} = (3, 4)$.

**Passo 1.** Aplicamos a fórmula do módulo:
$$||\vec{v}|| = \sqrt{x^2 + y^2}$$

**Passo 2.** Substituímos os valores:
$$||\vec{v}|| = \sqrt{3^2 + 4^2} = \sqrt{9 + 16} = \sqrt{25}$$

**Resultado:**
$$||\vec{v}|| = 5$$

💡 *Dica:* Vá até a aba Interativo e coloque X = 3 e Y = 4 para conferir visualmente!
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 2 — OPERAÇÕES COM VETORES
# ----------------------------------------------------------------------------
elif topico == "2. Operações com Vetores":
    st.header("2. Soma e Subtração de Vetores")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
### Soma de vetores
Somamos vetores **componente a componente**:

$$\vec{u} + \vec{v} = \begin{bmatrix} u_x + v_x \\ u_y + v_y \end{bmatrix}$$

Geometricamente, isso corresponde à **regra do paralelogramo** (ou "regra da ponta com a
cauda"): você desenha $\vec{u}$, e a partir da ponta dele desenha $\vec{v}$; o vetor soma vai
da origem até a ponta final.

### Subtração de vetores
A subtração $\vec{u} - \vec{v}$ é o mesmo que somar $\vec{u} + (-\vec{v})$, ou seja, inverter
o sentido de $\vec{v}$ e somar:

$$\vec{u} - \vec{v} = \begin{bmatrix} u_x - v_x \\ u_y - v_y \end{bmatrix}$$

### Multiplicação por escalar
Multiplicar um vetor por um número $k$ (escalar) estica ou encolhe o vetor, e inverte o
sentido se $k$ for negativo:

$$k\vec{v} = \begin{bmatrix} k \cdot v_x \\ k \cdot v_y \end{bmatrix}$$
            """
        )

    with aba_interativo:
        c1, c2 = st.columns(2)
        with c1:
            u_x = st.number_input("u_x", value=2.0)
            u_y = st.number_input("u_y", value=3.0)
        with c2:
            v_x = st.number_input("v_x", value=4.0)
            v_y = st.number_input("v_y", value=-1.0)
        op = st.radio("Operação", ["Soma (u + v)", "Subtração (u - v)"])
        if op == "Soma (u + v)":
            r_x, r_y = u_x + v_x, u_y + v_y
        else:
            r_x, r_y = u_x - v_x, u_y - v_y
        fig = criar_grafico_2d(max(abs(u_x), abs(u_y), abs(v_x), abs(v_y), abs(r_x), abs(r_y)) + 2)
        add_vetor_2d(fig, u_x, u_y, "blue", "u")
        add_vetor_2d(fig, v_x, v_y, "orange", "v")
        add_vetor_2d(fig, r_x, r_y, "green", "Resultado")
        st.plotly_chart(fig, use_container_width=True)
        st.latex(rf"\text{{Resultado}} = \begin{{bmatrix}} {r_x} \\ {r_y} \end{{bmatrix}}")

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Dados $\vec{u} = (2, 3)$ e $\vec{v} = (4, -1)$, calcule $\vec{u} + \vec{v}$.

**Passo 1.** Somamos as componentes x:
$$2 + 4 = 6$$

**Passo 2.** Somamos as componentes y:
$$3 + (-1) = 2$$

**Resultado:**
$$\vec{u} + \vec{v} = (6, 2)$$
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 3 — PRODUTO ESCALAR E VETORIAL
# ----------------------------------------------------------------------------
elif topico == "3. Produto Escalar e Vetorial":
    st.header("3. Produtos de Vetores")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
### Produto escalar (produto interno)
O produto escalar entre dois vetores retorna um **número** (escalar), não um vetor:

$$\vec{u} \cdot \vec{v} = u_x v_x + u_y v_y$$

Ele está relacionado ao ângulo $\theta$ entre os vetores por:

$$\vec{u} \cdot \vec{v} = ||\vec{u}|| \, ||\vec{v}|| \cos\theta$$

Isso significa que podemos usar o produto escalar para **descobrir o ângulo** entre dois
vetores, e também para saber se são perpendiculares: se $\vec{u} \cdot \vec{v} = 0$, os
vetores são ortogonais.

### Produto vetorial (produto cruz)
Só é definido em $\mathbb{R}^3$, e o resultado é **um novo vetor**, perpendicular aos dois
vetores originais:

$$\vec{u} \times \vec{v} = \begin{bmatrix} u_y v_z - u_z v_y \\ u_z v_x - u_x v_z \\ u_x v_y - u_y v_x \end{bmatrix}$$

O módulo desse vetor resultante é igual à área do paralelogramo formado por $\vec{u}$ e
$\vec{v}$.
            """
        )

    with aba_interativo:
        tipo = st.radio("Escolha:", ["Produto Escalar (Ângulos 2D)", "Produto Vetorial (Ortogonal 3D)"])
        if tipo == "Produto Escalar (Ângulos 2D)":
            c1, c2 = st.columns(2)
            with c1:
                u = np.array([st.number_input("u_x", value=3.0), st.number_input("u_y", value=1.0)])
            with c2:
                v = np.array([st.number_input("v_x", value=1.0), st.number_input("v_y", value=4.0)])
            dot = np.dot(u, v)
            ang = np.degrees(np.arccos(np.clip(dot / (np.linalg.norm(u) * np.linalg.norm(v)), -1.0, 1.0)))
            st.latex(rf"\vec{{u}} \cdot \vec{{v}} = {dot:.2f} \quad | \quad \theta \approx {ang:.2f}^\circ")
            fig = criar_grafico_2d(max(abs(u).max(), abs(v).max()) + 2)
            add_vetor_2d(fig, u[0], u[1], "blue", "u")
            add_vetor_2d(fig, v[0], v[1], "orange", "v")
            st.plotly_chart(fig, use_container_width=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                u_3d = np.array([st.number_input("u_x", value=2.0), st.number_input("u_y", value=0.0), st.number_input("u_z", value=0.0)])
            with c2:
                v_3d = np.array([st.number_input("v_x", value=0.0), st.number_input("v_y", value=3.0), st.number_input("v_z", value=0.0)])
            cross = np.cross(u_3d, v_3d)
            st.latex(rf"\vec{{u}} \times \vec{{v}} = \begin{{bmatrix}} {cross[0]} \\ {cross[1]} \\ {cross[2]} \end{{bmatrix}}")
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(x=[0, u_3d[0]], y=[0, u_3d[1]], z=[0, u_3d[2]], mode="lines", line=dict(color="blue", width=4), name="u"))
            fig.add_trace(go.Scatter3d(x=[0, v_3d[0]], y=[0, v_3d[1]], z=[0, v_3d[2]], mode="lines", line=dict(color="orange", width=4), name="v"))
            fig.add_trace(go.Scatter3d(x=[0, cross[0]], y=[0, cross[1]], z=[0, cross[2]], mode="lines", line=dict(color="green", width=6), name="u x v"))
            st.plotly_chart(fig, use_container_width=True)

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Calcule o produto escalar entre $\vec{u} = (3, 1)$ e $\vec{v} = (1, 4)$ e o
ângulo entre eles.

**Passo 1.** Multiplicamos as componentes correspondentes e somamos:
$$\vec{u} \cdot \vec{v} = (3)(1) + (1)(4) = 3 + 4 = 7$$

**Passo 2.** Calculamos os módulos:
$$||\vec{u}|| = \sqrt{3^2+1^2} = \sqrt{10}, \qquad ||\vec{v}|| = \sqrt{1^2+4^2} = \sqrt{17}$$

**Passo 3.** Isolamos $\cos\theta$ na fórmula:
$$\cos\theta = \frac{\vec{u}\cdot\vec{v}}{||\vec{u}||\,||\vec{v}||} = \frac{7}{\sqrt{10}\sqrt{17}} \approx 0.537$$

**Resultado:**
$$\theta = \arccos(0.537) \approx 57.5^\circ$$
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 4 — DEPENDÊNCIA LINEAR
# ----------------------------------------------------------------------------
elif topico == "4. Dependência Linear (LI e LD)":
    st.header("4. Combinação e Dependência Linear")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
### Combinação linear
Uma **combinação linear** de vetores $\vec{u}$ e $\vec{v}$ é qualquer vetor da forma:

$$a\vec{u} + b\vec{v}, \qquad a, b \in \mathbb{R}$$

### Dependência e independência linear
* Dois vetores são **linearmente dependentes (LD)** se um deles é múltiplo do outro — ou
  seja, eles apontam na mesma reta (mesma direção, sentido igual ou oposto).
* Dois vetores são **linearmente independentes (LI)** se nenhum é múltiplo do outro — juntos,
  eles conseguem "cobrir" todo o plano através de combinações lineares.

Uma forma prática de testar isso em 2D é calcular o **determinante** da matriz formada pelos
dois vetores como colunas:

$$\det \begin{bmatrix} u_x & v_x \\ u_y & v_y \end{bmatrix} = u_x v_y - u_y v_x$$

* Se o determinante for **0** → os vetores são **LD**.
* Se o determinante for **diferente de 0** → os vetores são **LI**.

Isso faz sentido geometricamente: o determinante é a área do paralelogramo formado pelos
vetores. Se a área é zero, os vetores "colapsaram" numa mesma reta.
            """
        )

    with aba_interativo:
        c1, c2 = st.columns(2)
        with c1:
            u = np.array([st.number_input("u_x", value=2.0), st.number_input("u_y", value=1.0)])
        with c2:
            v = np.array([st.number_input("v_x", value=4.0), st.number_input("v_y", value=2.0)])

        det = np.linalg.det(np.column_stack((u, v)))
        if abs(det) < 1e-9:
            st.error("Os vetores são Linearmente Dependentes (LD) — eles estão na mesma reta!")
        else:
            st.success("Os vetores são Linearmente Independentes (LI) — eles formam um plano (área > 0)!")

        st.latex(rf"\det = {det:.2f}")
        fig = criar_grafico_2d(max(abs(u).max(), abs(v).max()) + 2)
        add_vetor_2d(fig, u[0], u[1], "blue", "u")
        add_vetor_2d(fig, v[0], v[1], "orange", "v")
        st.plotly_chart(fig, use_container_width=True)

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Verifique se $\vec{u} = (2, 1)$ e $\vec{v} = (4, 2)$ são LI ou LD.

**Passo 1.** Montamos o determinante:
$$\det \begin{bmatrix} 2 & 4 \\ 1 & 2 \end{bmatrix} = (2)(2) - (1)(4) = 4 - 4 = 0$$

**Resultado:** Como o determinante é zero, os vetores são **Linearmente Dependentes**.
De fato, note que $\vec{v} = 2\vec{u}$ — são paralelos!
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 5 — MATRIZES, DETERMINANTES E INVERSA
# ----------------------------------------------------------------------------
elif topico == "5. Matrizes, Determinantes e Inversa":
    st.header("5. Matrizes 2x2")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
### O que é uma matriz?
Uma matriz é uma tabela de números organizados em linhas e colunas. Uma matriz $2\times 2$
tem a forma:

$$A = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$$

### Determinante
O determinante de uma matriz $2\times 2$ é:

$$\det(A) = a_{11}a_{22} - a_{12}a_{21}$$

Geometricamente, o determinante representa **o fator de escala de área** que a matriz aplica
ao transformar o plano (veremos isso melhor no tópico de Transformações Lineares). Se
$\det(A) = 0$, a matriz "achata" o plano em uma linha (ou ponto), e por isso não é possível
"desfazer" a transformação — ou seja, **a matriz não tem inversa**.

### Matriz inversa
Quando $\det(A) \neq 0$, existe uma matriz $A^{-1}$ tal que $A A^{-1} = I$ (matriz identidade).
Para matrizes $2\times 2$:

$$A^{-1} = \frac{1}{\det(A)} \begin{bmatrix} a_{22} & -a_{12} \\ -a_{21} & a_{11} \end{bmatrix}$$

A inversa é extremamente útil para **resolver sistemas lineares**: se $A\vec{x} = \vec{b}$,
então $\vec{x} = A^{-1}\vec{b}$.
            """
        )

    with aba_interativo:
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("a11", value=2.0)
            c = st.number_input("a21", value=1.0)
        with col2:
            b = st.number_input("a12", value=1.0)
            d = st.number_input("a22", value=2.0)
        A = np.array([[a, b], [c, d]])
        det = np.linalg.det(A)
        st.latex(rf"\det(A) = {det:.2f}")
        if abs(det) > 1e-9:
            inv = np.linalg.inv(A)
            st.latex(rf"A^{{-1}} = \begin{{bmatrix}} {inv[0,0]:.2f} & {inv[0,1]:.2f} \\ {inv[1,0]:.2f} & {inv[1,1]:.2f} \end{{bmatrix}}")
        else:
            st.error("Matriz singular (sem inversa).")

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Calcule $\det(A)$ e $A^{-1}$ para $A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$.

**Passo 1.** Determinante:
$$\det(A) = (2)(2) - (1)(1) = 4 - 1 = 3$$

**Passo 2.** Como $\det(A) \neq 0$, a inversa existe. Aplicamos a fórmula:
$$A^{-1} = \frac{1}{3}\begin{bmatrix} 2 & -1 \\ -1 & 2 \end{bmatrix} = \begin{bmatrix} 0.67 & -0.33 \\ -0.33 & 0.67 \end{bmatrix}$$

**Verificação:** multiplicando $A \cdot A^{-1}$ devemos obter a matriz identidade $I$.
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 6 — SISTEMAS DE EQUAÇÕES LINEARES
# ----------------------------------------------------------------------------
elif topico == "6. Sistemas de Equações Lineares":
    st.header("6. Sistemas 2x2 Geométricos")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
Um sistema de duas equações lineares com duas incógnitas tem a forma:

$$\begin{cases} a_1 x + b_1 y = c_1 \\ a_2 x + b_2 y = c_2 \end{cases}$$

Cada equação representa **uma reta** no plano. Resolver o sistema significa encontrar o(s)
ponto(s) onde essas retas se cruzam.

### Os três casos possíveis
1. **Solução única** — as retas se cruzam em exatamente um ponto (o caso mais comum).
2. **Nenhuma solução** — as retas são paralelas e nunca se cruzam.
3. **Infinitas soluções** — as retas são coincidentes (são a mesma reta).

### Forma matricial
Podemos escrever o sistema como $A\vec{x} = \vec{b}$:

$$\begin{bmatrix} a_1 & b_1 \\ a_2 & b_2 \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} c_1 \\ c_2 \end{bmatrix}$$

Se $\det(A) \neq 0$, a solução única é dada por $\vec{x} = A^{-1}\vec{b}$.
            """
        )

    with aba_interativo:
        c1, c2 = st.columns(2)
        with c1:
            a1 = st.number_input("a1", value=1.0)
            b1 = st.number_input("b1", value=1.0)
            c_1 = st.number_input("c1", value=5.0)
        with c2:
            a2 = st.number_input("a2", value=2.0)
            b2 = st.number_input("b2", value=-1.0)
            c_2 = st.number_input("c2", value=4.0)
        try:
            sol = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c_1, c_2]))
            st.success(f"Solução única: x = {sol[0]:.2f}, y = {sol[1]:.2f}")
            x_vals = np.linspace(-10, 10, 100)
            fig = criar_grafico_2d(10)
            fig.add_trace(go.Scatter(x=x_vals, y=(c_1 - a1 * x_vals) / b1, name="Eq 1"))
            fig.add_trace(go.Scatter(x=x_vals, y=(c_2 - a2 * x_vals) / b2, name="Eq 2"))
            fig.add_trace(go.Scatter(x=[sol[0]], y=[sol[1]], mode="markers", marker=dict(color="red", size=10), name="Interseção"))
            st.plotly_chart(fig, use_container_width=True)
        except np.linalg.LinAlgError:
            st.error("Retas paralelas ou coincidentes — não há solução única.")

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Resolva o sistema:
$$\begin{cases} x + y = 5 \\ 2x - y = 4 \end{cases}$$

**Passo 1.** Da primeira equação, isolamos $y$: $y = 5 - x$.

**Passo 2.** Substituímos na segunda equação:
$$2x - (5-x) = 4 \;\Rightarrow\; 3x - 5 = 4 \;\Rightarrow\; 3x = 9 \;\Rightarrow\; x = 3$$

**Passo 3.** Voltamos para achar $y$:
$$y = 5 - 3 = 2$$

**Resultado:** $x = 3,\; y = 2$ — o ponto onde as duas retas se cruzam.
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 7 — TRANSFORMAÇÕES LINEARES
# ----------------------------------------------------------------------------
elif topico == "7. Transformações Lineares":
    st.header("7. Transformações Lineares Geométricas")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
Uma **transformação linear** é uma função que leva vetores a outros vetores, preservando
somas e multiplicação por escalar. Toda transformação linear de $\mathbb{R}^2$ para
$\mathbb{R}^2$ pode ser representada por uma matriz $A$:

$$T(\vec{v}) = A\vec{v}$$

### Exemplos famosos de transformações (matriz 2x2)
* **Escala:** $\begin{bmatrix} k & 0 \\ 0 & k \end{bmatrix}$ — aumenta ou diminui o tamanho.
* **Rotação por ângulo $\theta$:** $\begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$
* **Cisalhamento (shear):** $\begin{bmatrix} 1 & k \\ 0 & 1 \end{bmatrix}$ — "inclina" a figura.
* **Reflexão no eixo x:** $\begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}$

### Como visualizar
Uma boa forma de entender uma transformação é aplicá-la aos vetores $\vec{i}=(1,0)$ e
$\vec{j}=(0,1)$ (a base canônica) — eles viram exatamente as colunas da matriz $A$! Por isso,
transformar um quadrado unitário mostra visualmente o que a matriz faz com o espaço inteiro.
            """
        )

    with aba_interativo:
        A = np.array(
            [
                [st.number_input("a11", value=1.0), st.number_input("a12", value=1.0)],
                [st.number_input("a21", value=0.0), st.number_input("a22", value=1.0)],
            ]
        )
        q_orig = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        q_trans = (A @ q_orig.T).T
        fig = criar_grafico_2d(5)
        fig.add_trace(go.Scatter(x=q_orig[:, 0], y=q_orig[:, 1], fill="toself", name="Original"))
        fig.add_trace(go.Scatter(x=q_trans[:, 0], y=q_trans[:, 1], fill="toself", name="Transformado"))
        st.plotly_chart(fig, use_container_width=True)
        st.latex(rf"\det(A) = {np.linalg.det(A):.2f} \; \text{{(fator de mudança de área)}}")

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Qual o efeito da matriz $A = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix}$ sobre
o vetor $\vec{v} = (1, 0)$?

**Passo 1.** Aplicamos $A\vec{v}$:
$$\begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix}\begin{bmatrix} 1 \\ 0 \end{bmatrix} = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

**Resultado:** o vetor $(1,0)$ virou $(0,1)$ — essa matriz é justamente a **rotação de 90°**
no sentido anti-horário! Experimente colocar a11=0, a12=-1, a21=1, a22=0 na aba Interativo.
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 8 — PROJEÇÃO ORTOGONAL
# ----------------------------------------------------------------------------
elif topico == "8. Projeção Ortogonal":
    st.header("8. Projeção Ortogonal")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
A **projeção ortogonal** de um vetor $\vec{v}$ sobre a reta gerada por um vetor $\vec{u}$ é a
"sombra" que $\vec{v}$ projeta sobre essa reta, como se uma luz caísse perpendicularmente
sobre ela.

A fórmula é:

$$\text{proj}_{\vec{u}}(\vec{v}) = \frac{\vec{v}\cdot\vec{u}}{\vec{u}\cdot\vec{u}}\,\vec{u}$$

### Intuição
* O numerador $\vec{v}\cdot\vec{u}$ mede "o quanto" $\vec{v}$ aponta na direção de $\vec{u}$.
* Dividir por $\vec{u}\cdot\vec{u} = ||\vec{u}||^2$ normaliza esse valor pelo tamanho de
  $\vec{u}$.
* O resultado final é multiplicado de volta por $\vec{u}$ para devolver um vetor na direção
  correta.

O vetor "erro" — a diferença entre $\vec{v}$ e sua projeção — é sempre **perpendicular** a
$\vec{u}$. Essa ideia é a base do **método dos mínimos quadrados**, usado para ajustar retas
a conjuntos de dados.
            """
        )

    with aba_interativo:
        c1, c2 = st.columns(2)
        with c1:
            u = np.array([st.number_input("u_x", value=4.0), st.number_input("u_y", value=1.0)])
        with c2:
            v = np.array([st.number_input("v_x", value=2.0), st.number_input("v_y", value=4.0)])

        proj = (np.dot(v, u) / np.dot(u, u)) * u
        st.latex(rf"\text{{Proj}}_{{\vec{{u}}}}(\vec{{v}}) = \begin{{bmatrix}} {proj[0]:.2f} \\ {proj[1]:.2f} \end{{bmatrix}}")

        fig = criar_grafico_2d(max(abs(u).max(), abs(v).max()) + 2)
        add_vetor_2d(fig, u[0], u[1], "blue", "u (Base)")
        add_vetor_2d(fig, v[0], v[1], "orange", "v")
        add_vetor_2d(fig, proj[0], proj[1], "green", "Projeção")
        fig.add_trace(go.Scatter(x=[proj[0], v[0]], y=[proj[1], v[1]], mode="lines", line=dict(dash="dash", color="gray"), name="Erro ortogonal"))
        st.plotly_chart(fig, use_container_width=True)

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Projete $\vec{v} = (2, 4)$ sobre $\vec{u} = (4, 1)$.

**Passo 1.** Calculamos $\vec{v}\cdot\vec{u}$:
$$(2)(4) + (4)(1) = 8 + 4 = 12$$

**Passo 2.** Calculamos $\vec{u}\cdot\vec{u}$:
$$(4)(4) + (1)(1) = 16 + 1 = 17$$

**Passo 3.** Multiplicamos a razão por $\vec{u}$:
$$\text{proj}_{\vec{u}}(\vec{v}) = \frac{12}{17}\begin{bmatrix}4\\1\end{bmatrix} \approx \begin{bmatrix}2.82\\0.71\end{bmatrix}$$
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 9 — AUTOVALORES E AUTOVETORES
# ----------------------------------------------------------------------------
elif topico == "9. Autovalores e Autovetores":
    st.header("9. Autovalores e Autovetores")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
Dada uma matriz $A$, um **autovetor** é um vetor $\vec{v} \neq \vec{0}$ que, ao ser
transformado por $A$, **não muda de direção** — apenas é esticado ou encolhido por um fator
$\lambda$, chamado **autovalor**:

$$A\vec{v} = \lambda\vec{v}$$

### Como encontrar autovalores
Reescrevendo a equação: $(A - \lambda I)\vec{v} = \vec{0}$. Para que essa equação tenha
solução não trivial, precisamos que:

$$\det(A - \lambda I) = 0$$

Essa é a chamada **equação característica**. Para uma matriz $2\times2$, ela resulta em uma
equação do segundo grau em $\lambda$, cujas raízes são os autovalores.

### Por que isso importa?
Autovalores e autovetores revelam as **direções especiais** de uma transformação — os "eixos
naturais" ao redor dos quais o espaço se estica ou encolhe. Eles são fundamentais em: análise
de estabilidade de sistemas, compressão de dados (PCA), Google PageRank, entre outros.
            """
        )

    with aba_interativo:
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("a11", value=2.0)
            c = st.number_input("a21", value=0.0)
        with col2:
            b = st.number_input("a12", value=1.0)
            d = st.number_input("a22", value=3.0)
        A = np.array([[a, b], [c, d]])
        val, vet = np.linalg.eig(A)

        if np.iscomplexobj(val) and np.any(np.abs(val.imag) > 1e-9):
            st.warning(
                "Essa matriz tem **autovalores complexos** — ou seja, não existem "
                "autovetores reais (visualizáveis como setas no plano). Isso costuma "
                "acontecer com matrizes de rotação, onde nenhum vetor mantém sua direção "
                "original. Experimente outros valores, por exemplo uma matriz diagonal "
                "(a12 = 0, a21 = 0), para ver autovalores reais."
            )
            st.latex(rf"\lambda_1 = {val[0].real:.2f} {'+' if val[0].imag >= 0 else '-'} {abs(val[0].imag):.2f}i")
            st.latex(rf"\lambda_2 = {val[1].real:.2f} {'+' if val[1].imag >= 0 else '-'} {abs(val[1].imag):.2f}i")
        else:
            val = val.real
            vet = vet.real
            for i in range(len(val)):
                st.latex(rf"\lambda_{i+1} = {val[i]:.2f} \quad \vec{{v}}_{i+1} = \begin{{bmatrix}} {vet[0,i]:.2f} \\ {vet[1,i]:.2f} \end{{bmatrix}}")
            fig = criar_grafico_2d(5)
            add_vetor_2d(fig, vet[0, 0], vet[1, 0], "purple", f"λ={val[0]:.1f}")
            if len(val) > 1:
                add_vetor_2d(fig, vet[0, 1], vet[1, 1], "red", f"λ={val[1]:.1f}")
            st.plotly_chart(fig, use_container_width=True)

    with aba_exemplo:
        st.subheader("📝 Exemplo Resolvido Passo a Passo")
        st.markdown(
            r"""
Dada a matriz $A = \begin{bmatrix} 2 & 1 \\ 0 & 3 \end{bmatrix}$, vamos encontrar seus autovalores e autovetores:

### 1. Equação Característica
Calculamos $\det(A - \lambda I) = 0$:
$$\det\begin{bmatrix} 2-\lambda & 1 \\ 0 & 3-\lambda \end{bmatrix} = (2-\lambda)(3-\lambda) = 0$$
Portanto, os autovalores são **$\lambda_1 = 2$** e **$\lambda_2 = 3$**.

### 2. Determinando os Autovetores
* **Para $\lambda_1 = 2$:**
  Substituindo na matriz $(A - 2I)\vec{v} = 0$, obtemos o autovetor:
  $$\vec{v}_1 = \begin{bmatrix} 1 \\ 0 \end{bmatrix}$$
* **Para $\lambda_2 = 3$:**
  Substituindo na matriz $(A - 3I)\vec{v} = 0$, obtemos o autovetor:
  $$\vec{v}_2 = \begin{bmatrix} 1 \\ 1 \end{bmatrix}$$
            """
    )
    st.info("💡 Dica: Vá até a aba Interativo e configure a matriz com $a_{11} = 2$, $a_{12} = 1$, $a_{21} = 0$ e $a_{22} = 3$ para conferir visualmente!")

    with aba_quiz:
        renderizar_quiz(topico)

# ----------------------------------------------------------------------------
# TÓPICO 10 — SVD
# ----------------------------------------------------------------------------
elif topico == "10. SVD (Decomposição em Valores Singulares)":
    st.header("10. Decomposição SVD")
    aba_teoria, aba_interativo, aba_exemplo, aba_quiz = st.tabs(
        ["📖 Teoria", "🎮 Interativo", "✅ Exemplo Resolvido", "🧠 Quiz"]
    )

    with aba_teoria:
        teoria_intro(
            r"""
A **Decomposição em Valores Singulares (SVD)** é uma das ferramentas mais poderosas da
Álgebra Linear. Ela afirma que **qualquer** matriz $A$ (mesmo não quadrada) pode ser escrita
como o produto de três matrizes:

$$A = U \Sigma V^T$$

* $V^T$ — uma **rotação/reflexão** no espaço de entrada.
* $\Sigma$ — um **escalonamento** puro ao longo dos eixos (os "valores singulares", sempre
  não negativos, geralmente ordenados do maior para o menor).
* $U$ — outra **rotação/reflexão**, agora no espaço de saída.

### Intuição geométrica
Pense em qualquer transformação linear complexa como três passos simples em sequência: gire,
depois estique/encolha ao longo de eixos perpendiculares, depois gire de novo. É exatamente
isso que o SVD revela.

### Aplicações
O SVD é a base de técnicas como **compressão de imagens**, **redução de dimensionalidade
(PCA)**, **sistemas de recomendação** e **remoção de ruído** em dados.
            """
        )

    with aba_interativo:
        c1, c2 = st.columns(2)
        with c1:
            a = st.number_input("a11 ", value=2.0)
            c = st.number_input("a21 ", value=0.0)
        with c2:
            b = st.number_input("a12 ", value=1.0)
            d = st.number_input("a22 ", value=2.0)
        A = np.array([[a, b], [c, d]])
        U, S, VT = np.linalg.svd(A)
        st.latex(r"A = U \Sigma V^T")
        st.latex(rf"\Sigma = \begin{{bmatrix}} {S[0]:.2f} & 0 \\ 0 & {S[1]:.2f} \end{{bmatrix}}")
        st.info(
            "O SVD mostra os 'eixos principais' de distorção criados pela matriz. Estes "
            "valores em Sigma indicam o quanto o espaço foi esticado nessas direções."
        )

        q_orig = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        q_trans = (A @ q_orig.T).T
        fig = criar_grafico_2d(max(3, np.abs(q_trans).max() + 1))
        fig.add_trace(go.Scatter(x=q_orig[:, 0], y=q_orig[:, 1], fill="toself", name="Original"))
        fig.add_trace(go.Scatter(x=q_trans[:, 0], y=q_trans[:, 1], fill="toself", name="Transformado por A"))
        st.plotly_chart(fig, use_container_width=True)

    with aba_exemplo:
        st.markdown(
            r"""
**Problema:** Interprete o SVD de $A = \begin{bmatrix} 2 & 0 \\ 0 & 2 \end{bmatrix}$.

**Passo 1.** Como a matriz já é diagonal e escala igualmente em x e y, não há rotação
envolvida: $U$ e $V^T$ são a identidade.

**Passo 2.** Os valores singulares são simplesmente os elementos da diagonal:
$$\Sigma = \begin{bmatrix} 2 & 0 \\ 0 & 2 \end{bmatrix}$$

**Resultado:** essa matriz apenas **duplica o tamanho** de qualquer vetor, sem girar nem
distorcer proporções — um caso particular bem simples de entender antes de ir para casos com
rotação!
            """
        )

    with aba_quiz:
        renderizar_quiz(topico)

st.divider()
st.caption(
    "💡 Dúvidas? Use o assistente de IA na barra lateral — ele conhece o tópico que você está "
    "estudando agora e pode te ajudar com exemplos, dicas e exercícios."
)
