from database import conectar_banco


def produto_para_dict(produto):
    return {
        "id": produto["id"],
        "nome": produto["nome"],
        "preco": produto["preco"],
        "estoque": produto["estoque"],
        "tipo_pele": produto["tipo_pele"],
        "pele_sensivel": bool(produto["pele_sensivel"]),
        "indicado_para_espinha": bool(produto["indicado_para_espinha"]),
        "ativo": bool(produto["ativo"]),
        "categoria": produto["categoria"]
    }

def calcular_score(produto, perfil):
    score = 0

    if produto["tipo_pele"] == perfil.tipo_pele:
        score += 3
    elif produto["tipo_pele"] == "todos":
        score += 1

    if perfil.sensivel and produto["pele_sensivel"]:
        score += 2

    if perfil.tem_espinha and produto["indicado_para_espinha"]:
        score += 2

    return score

def agrupar_por_categoria(produtos):
    recomendacoes_por_categoria = {}

    for produto in produtos:
        categoria = produto["categoria"]

        if categoria not in recomendacoes_por_categoria:
            recomendacoes_por_categoria[categoria] = []

        recomendacoes_por_categoria[categoria].append(produto)

    return recomendacoes_por_categoria

def buscar_produtos_compativeis(tipo_pele):
    conexao, cursor = conectar_banco()

    cursor.execute(
        """
SELECT * FROM produtos
WHERE (tipo_pele = ? OR tipo_pele = 'todos')
AND estoque > 0
AND ativo = 1
""",
(tipo_pele,)
    )

    produtos = cursor.fetchall()
    conexao.close()

    return produtos

def gerar_recomendacoes(perfil):

    recomendacoes = buscar_produtos_compativeis(perfil.tipo_pele)

    lista_recomendacoes = []

    for recomendacao in recomendacoes:

        score = calcular_score(recomendacao, perfil)

        recomendacoes_atualizadas = produto_para_dict(recomendacao)

        recomendacoes_atualizadas["score"] = score

        lista_recomendacoes.append(recomendacoes_atualizadas)

    lista_recomendacoes.sort(key=lambda produto: produto["score"], reverse=True)

    recomendacoes_por_categoria = agrupar_por_categoria(lista_recomendacoes)

    return {
        "perfil": {
        "tipo_pele": perfil.tipo_pele,
        "sensivel": perfil.sensivel,
        "tem_espinha": perfil.tem_espinha
    },
    "total_recomendacoes": len(lista_recomendacoes), 
    "recomendacoes": recomendacoes_por_categoria
    }
