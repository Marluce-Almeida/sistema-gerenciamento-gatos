
from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def conectar():
    banco = sqlite3.connect("animais.db")
    banco.row_factory = sqlite3.Row
    return banco

def criar_banco():
    banco = conectar()
    banco.execute("""
        CREATE TABLE IF NOT EXISTS gatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade TEXT,
            sexo TEXT,
            observacao TEXT
        )
    """)
    banco.execute("""
        CREATE TABLE IF NOT EXISTS cuidados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gato_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TEXT,
            FOREIGN KEY (gato_id) REFERENCES gatos(id)
        )
    """)
    banco.execute("""
        CREATE TABLE IF NOT EXISTS doacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL
        )
    """)
    banco.commit()
    banco.close()

criar_banco()

MODELO = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Cuidado Animal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f7f4;
            margin: 0;
            color: #263b31;
        }
        header {
            background: #245b49;
            color: white;
            padding: 22px;
            text-align: center;
        }
        nav {
            background: #dcebe1;
            padding: 15px;
            text-align: center;
        }
        nav a {
            margin: 10px;
            color: #245b49;
            text-decoration: none;
            font-weight: bold;
        }
        main {
            max-width: 900px;
            margin: 30px auto;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 12px;
            box-shadow: 0 2px 6px #0001;
        }
        input, select, button {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            box-sizing: border-box;
        }
        button {
            background: #245b49;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        table {
            width: 100%;
            background: white;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        .indicadores {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .indicadores .card {
            flex: 1;
            min-width: 150px;
        }
    </style>
</head>
<body>

<header>
    <h1>🐾 Cuidado Animal</h1>
    <p>Organização e cuidado dos animais resgatados</p>
</header>

<nav>
    <a href="/">Início</a>
    <a href="/gatos">Gatos</a>
    <a href="/cuidados">Cuidados</a>
    <a href="/doacoes">Doações</a>
</nav>

<main>
    {{ conteudo|safe }}
</main>

</body>
</html>
"""

@app.route("/")
def inicio():
    banco = conectar()

    total = banco.execute(
        "SELECT COUNT(*) FROM gatos"
    ).fetchone()[0]

    cuidados = banco.execute(
        "SELECT COUNT(*) FROM cuidados"
    ).fetchone()[0]

   doacoes = banco.execute(
    "SELECT COUNT(*) FROM doacoes"
).fetchone()[0]

total_arrecadado = banco.execute(
    "SELECT COALESCE(SUM(valor), 0) FROM doacoes"
).fetchone()[0]

banco.close()

    conteudo = f"""
    <h2>Painel inicial</h2>
    <p>Bem-vinda ao sistema de organização da proteção animal!</p>

    <div class="indicadores">
        <div class="card">
            <h3>🐱 Gatos cadastrados</h3>
            <h2>{total}</h2>
        </div>
        <div class="card">
            <h3>🩺 Cuidados registrados</h3>
            <h2>{cuidados}</h2>
        </div>
        <div class="card">
            <h3>🎁 Doações registradas</h3>
            <h2>{doacoes}</h2>
        </div>
        <div class="card">
    <h3>💰 Total arrecadado</h3>
    <h2>R$ {total_arrecadado:.2f}</h2>
</div>
    </div>

    <div class="card">
        <h3>Organize suas atividades</h3>
        <p>Cadastre animais, acompanhe cuidados e registre doações.</p>
    </div>
    """

    return render_template_string(MODELO, conteudo=conteudo)


@app.route("/gatos", methods=["GET", "POST"])
def gatos():
    banco = conectar()

    if request.method == "POST":
        nome = request.form["nome"].strip()
        idade = request.form["idade"]
        sexo = request.form["sexo"]
        observacao = request.form["observacao"]

        if nome:
            banco.execute("""
                INSERT INTO gatos
                (nome, idade, sexo, observacao)
                VALUES (?, ?, ?, ?)
            """, (nome, idade, sexo, observacao))

            banco.commit()

        banco.close()
        return redirect(url_for("gatos"))

    lista = banco.execute(
        "SELECT * FROM gatos ORDER BY nome"
    ).fetchall()

    banco.close()

    conteudo = """
    <h2>Cadastro de animais</h2>

    <div class="card">
        <form method="POST">
            <label>Nome do gato</label>
            <input name="nome" required>

            <label>Idade aproximada</label>
            <input name="idade">

            <label>Sexo</label>
            <select name="sexo">
                <option>Não informado</option>
                <option>Fêmea</option>
                <option>Macho</option>
            </select>

            <label>Observações sobre a saúde</label>
            <input name="observacao">

            <button type="submit">Cadastrar animal</button>
        </form>
    </div>

    <h3>Animais cadastrados</h3>
    <table>
        <tr>
            <th>Nome</th>
            <th>Idade</th>
            <th>Sexo</th>
            <th>Observações</th>
        </tr>
    """

    for gato in lista:
        conteudo += f"""
        <tr>
            <td>{gato['nome']}</td>
            <td>{gato['idade'] or '-'}</td>
            <td>{gato['sexo'] or '-'}</td>
            <td>{gato['observacao'] or '-'}</td>
        </tr>
        """

    conteudo += "</table>"

    return render_template_string(MODELO, conteudo=conteudo)


@app.route("/cuidados", methods=["GET", "POST"])
def cuidados():
    banco = conectar()

    if request.method == "POST":
        gato_id = request.form["gato_id"]
        tipo = request.form["tipo"]
        descricao = request.form["descricao"]
        data = request.form["data"]

        banco.execute("""
            INSERT INTO cuidados
            (gato_id, tipo, descricao, data)
            VALUES (?, ?, ?, ?)
        """, (gato_id, tipo, descricao, data))

        banco.commit()
        banco.close()

        return redirect(url_for("cuidados"))

    gatos = banco.execute(
        "SELECT * FROM gatos ORDER BY nome"
    ).fetchall()

    registros = banco.execute("""
        SELECT cuidados.*, gatos.nome
        FROM cuidados
        JOIN gatos ON gatos.id = cuidados.gato_id
        ORDER BY cuidados.id DESC
    """).fetchall()

    banco.close()

    opcoes = "".join(
        f"<option value='{gato['id']}'>{gato['nome']}</option>"
        for gato in gatos
    )

    conteudo = f"""
    <h2>Cuidados veterinários</h2>

    <div class="card">
        <form method="POST">
            <label>Animal</label>
            <select name="gato_id" required>
                {opcoes}
            </select>

            <label>Tipo de cuidado</label>
            <select name="tipo">
                <option>Consulta</option>
                <option>Vacina</option>
                <option>Medicamento</option>
                <option>Outro</option>
            </select>

            <label>Descrição</label>
            <input name="descricao" required>

            <label>Data</label>
            <input type="date" name="data">

            <button type="submit">Registrar cuidado</button>
        </form>
    </div>

    <h3>Histórico de cuidados</h3>
    <table>
        <tr>
            <th>Animal</th>
            <th>Tipo</th>
            <th>Descrição</th>
            <th>Data</th>
        </tr>
    """

    for registro in registros:
        conteudo += f"""
        <tr>
            <td>{registro['nome']}</td>
            <td>{registro['tipo']}</td>
            <td>{registro['descricao']}</td>
            <td>{registro['data'] or '-'}</td>
        </tr>
        """

    conteudo += "</table>"

    return render_template_string(MODELO, conteudo=conteudo)


@app.route("/doacoes", methods=["GET", "POST"])
def doacoes():
    banco = conectar()

    if request.method == "POST":
        tipo = request.form["tipo"]
        descricao = request.form["descricao"]
        valor = request.form.get("valor") or None

        banco.execute("""
            INSERT INTO doacoes (tipo, descricao, valor)
            VALUES (?, ?, ?)
        """, (tipo, descricao, valor))

        banco.commit()
        banco.close()

        return redirect(url_for("doacoes"))

    lista = banco.execute(
        "SELECT * FROM doacoes ORDER BY id DESC"
    ).fetchall()

    banco.close()

    conteudo = """
    <h2>Registro de doações</h2>

    <div class="card">
        <form method="POST">
            <label>Tipo de doação</label>
            <select name="tipo">
                <option>Financeira</option>
                <option>Material</option>
            </select>

            <label>Descrição</label>
            <input name="descricao" required>

            <label>Valor em reais (se houver)</label>
            <input type="number" step="0.01" min="0" name="valor">

            <button type="submit">Registrar doação</button>
        </form>
    </div>

    <h3>Doações registradas</h3>
    <table>
        <tr>
            <th>Tipo</th>
            <th>Descrição</th>
            <th>Valor</th>
        </tr>
    """

    for doacao in lista:
        valor = (
            f"R$ {doacao['valor']:.2f}"
            if doacao['valor'] is not None
            else "-"
        )

        conteudo += f"""
        <tr>
            <td>{doacao['tipo']}</td>
            <td>{doacao['descricao']}</td>
            <td>{valor}</td>
        </tr>
        """

    conteudo += "</table>"

    return render_template_string(MODELO, conteudo=conteudo)


if __name__ == "__main__":
    app.run(debug=True)