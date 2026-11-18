
import sqlite3
import pytest
import app as sistema


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    caminho = tmp_path / "teste.db"

    def conectar_teste():
        banco = sqlite3.connect(caminho)
        banco.row_factory = sqlite3.Row
        banco.execute("PRAGMA foreign_keys = ON")
        return banco

    monkeypatch.setattr(sistema, "conectar", conectar_teste)

    banco = conectar_teste()
    banco.executescript("""
        CREATE TABLE gatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade TEXT,
            sexo TEXT,
            observacao TEXT
        );

        CREATE TABLE cuidados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gato_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TEXT,
            FOREIGN KEY (gato_id) REFERENCES gatos(id)
        );

        CREATE TABLE doacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL
        );
    """)
    banco.commit()
    banco.close()

    sistema.app.config["TESTING"] = True

    return sistema.app.test_client()


def test_pagina_inicial(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert b"Painel inicial" in resposta.data


def test_cadastro_gato(cliente):
    resposta = cliente.post("/gatos", data={
        "nome": "Mimi",
        "idade": "2 anos",
        "sexo": "Fêmea",
        "observacao": "Saudável"
    })
    assert resposta.status_code == 302

    resposta = cliente.get("/gatos")
    assert b"Mimi" in resposta.data


def test_registro_cuidado(cliente):
    cliente.post("/gatos", data={
        "nome": "Mimi",
        "idade": "2",
        "sexo": "Fêmea",
        "observacao": ""
    })

    resposta = cliente.post("/cuidados", data={
        "gato_id": "1",
        "tipo": "Vacina",
        "descricao": "Vacina aplicada",
        "data": "2026-11-17"
    })

    assert resposta.status_code == 302


def test_registro_doacao(cliente):
    resposta = cliente.post("/doacoes", data={
        "tipo": "Financeira",
        "descricao": "Doação para os gatos",
        "valor": "100.00"
    })

    assert resposta.status_code == 302

    resposta = cliente.get("/doacoes")
    assert b"Doa" in resposta.data


def test_total_arrecadado(cliente):
    cliente.post("/doacoes", data={
        "tipo": "Financeira",
        "descricao": "Ajuda",
        "valor": "150.00"
    })

    resposta = cliente.get("/")
    assert b"150.00" in resposta.data
