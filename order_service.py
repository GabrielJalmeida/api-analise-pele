from __future__ import annotations

import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from config import pedidos_atualizam_estoque
from database import gerenciar_banco, gerenciar_transacao
from models import NovoPedido


RETENCAO_DIAS = 365
CENTAVOS = Decimal("0.01")


class PedidoInvalido(ValueError):
    pass


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _iso(data: datetime) -> str:
    return data.isoformat(timespec="seconds")


def _dinheiro(valor: object) -> Decimal:
    return Decimal(str(valor)).quantize(
        CENTAVOS,
        rounding=ROUND_HALF_UP,
    )


def _hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def limpar_pedidos_expirados(
    agora: datetime | None = None,
) -> int:
    momento = agora or _agora_utc()

    with gerenciar_transacao() as (_, cursor):
        cursor.execute(
            "DELETE FROM pedidos WHERE expira_em <= ?",
            (_iso(momento),),
        )
        return cursor.rowcount


def _codigo_pedido(agora: datetime) -> str:
    return (
        f"LUM-{agora:%Y%m%d}-"
        f"{secrets.token_hex(4).upper()}"
    )


def _pedido_por_id(
    cursor,
    pedido_id: int,
) -> dict:
    cursor.execute(
        "SELECT * FROM pedidos WHERE id = ?",
        (pedido_id,),
    )
    pedido = cursor.fetchone()

    if pedido is None:
        raise PedidoInvalido(
            "Pedido não encontrado"
        )

    cursor.execute(
        """
        SELECT
            produto_id,
            nome_produto,
            marca,
            imagem_url,
            preco_unitario,
            quantidade,
            subtotal
        FROM itens_pedido
        WHERE pedido_id = ?
        ORDER BY id
        """,
        (pedido_id,),
    )

    itens = [
        {
            "produto_id": item["produto_id"],
            "nome_produto": item["nome_produto"],
            "marca": item["marca"],
            "imagem_url": item["imagem_url"],
            "preco_unitario": item["preco_unitario"],
            "quantidade": item["quantidade"],
            "subtotal": item["subtotal"],
        }
        for item in cursor.fetchall()
    ]

    return {
        "codigo": pedido["codigo"],
        "cliente_nome": pedido["cliente_nome"],
        "cliente_email": pedido["cliente_email"],
        "total": pedido["total"],
        "status": pedido["status"],
        "criado_em": pedido["criado_em"],
        "expira_em": pedido["expira_em"],
        "modo": "demonstracao",
        "itens": itens,
    }


def criar_pedido(dados: NovoPedido) -> dict:
    agora = _agora_utc()
    expira_em = agora + timedelta(
        days=RETENCAO_DIAS
    )

    with gerenciar_transacao() as (_, cursor):
        ids = [
            item.produto_id
            for item in dados.itens
        ]
        marcadores = ",".join("?" for _ in ids)

        cursor.execute(
            f"""
            SELECT * FROM produtos
            WHERE id IN ({marcadores})
            """,
            ids,
        )

        produtos = {
            produto["id"]: produto
            for produto in cursor.fetchall()
        }

        if len(produtos) != len(ids):
            raise PedidoInvalido(
                "Um ou mais produtos não foram encontrados"
            )

        itens_preparados = []
        total = Decimal("0")

        for item in dados.itens:
            produto = produtos[item.produto_id]

            if not bool(produto["ativo"]):
                raise PedidoInvalido(
                    f"O produto '{produto['nome']}' não está disponível"
                )

            if produto["estoque"] < item.quantidade:
                raise PedidoInvalido(
                    f"Estoque insuficiente para '{produto['nome']}'"
                )

            preco = _dinheiro(produto["preco"])
            subtotal = _dinheiro(
                preco * item.quantidade
            )
            total += subtotal

            itens_preparados.append(
                (
                    produto,
                    item.quantidade,
                    preco,
                    subtotal,
                )
            )

        codigo = _codigo_pedido(agora)

        cursor.execute(
            """
            INSERT INTO pedidos (
                codigo,
                cliente_token_hash,
                cliente_nome,
                cliente_email,
                total,
                status,
                criado_em,
                expira_em,
                consentimento_retencao
            ) VALUES (?, ?, ?, ?, ?, 'registrado', ?, ?, 1)
            """,
            (
                codigo,
                _hash_token(dados.cliente_token),
                dados.cliente_nome,
                dados.cliente_email,
                float(_dinheiro(total)),
                _iso(agora),
                _iso(expira_em),
            ),
        )

        pedido_id = cursor.lastrowid

        for (
            produto,
            quantidade,
            preco,
            subtotal,
        ) in itens_preparados:
            cursor.execute(
                """
                INSERT INTO itens_pedido (
                    pedido_id,
                    produto_id,
                    nome_produto,
                    marca,
                    imagem_url,
                    preco_unitario,
                    quantidade,
                    subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pedido_id,
                    produto["id"],
                    produto["nome"],
                    produto["marca"],
                    produto["imagem_url"],
                    float(preco),
                    quantidade,
                    float(subtotal),
                ),
            )

            if pedidos_atualizam_estoque():
                cursor.execute(
                    """
                    UPDATE produtos
                    SET estoque = estoque - ?
                    WHERE id = ?
                    """,
                    (
                        quantidade,
                        produto["id"],
                    ),
                )

        return _pedido_por_id(
            cursor,
            pedido_id,
        )


def listar_historico(token: str) -> list[dict]:
    limpar_pedidos_expirados()
    token_hash = _hash_token(token)

    with gerenciar_banco() as (_, cursor):
        cursor.execute(
            """
            SELECT id FROM pedidos
            WHERE cliente_token_hash = ?
            ORDER BY criado_em DESC
            """,
            (token_hash,),
        )
        ids = [
            linha["id"]
            for linha in cursor.fetchall()
        ]

        return [
            _pedido_por_id(cursor, pedido_id)
            for pedido_id in ids
        ]


def excluir_historico(token: str) -> int:
    with gerenciar_transacao() as (_, cursor):
        cursor.execute(
            """
            DELETE FROM pedidos
            WHERE cliente_token_hash = ?
            """,
            (_hash_token(token),),
        )
        return cursor.rowcount


def listar_pedidos_admin(
    limite: int = 200,
) -> list[dict]:
    limpar_pedidos_expirados()

    with gerenciar_banco() as (_, cursor):
        cursor.execute(
            """
            SELECT id FROM pedidos
            ORDER BY criado_em DESC
            LIMIT ?
            """,
            (limite,),
        )
        ids = [
            linha["id"]
            for linha in cursor.fetchall()
        ]

        return [
            _pedido_por_id(cursor, pedido_id)
            for pedido_id in ids
        ]
