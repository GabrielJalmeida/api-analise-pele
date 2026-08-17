from database import gerenciar_banco

def obter_mensagem_inadequacao(motivo):
    mensagens = {
        "sem_rosto_visivel": "Não foi possível identificar o rosto na imagem. Envie uma foto com o rosto bem visível.",
        "rosto_distante": "O rosto está muito distante. Envie uma foto mais aproximada.",
        "imagem_escura": "A imagem está muito escura. Tente tirar a foto em um local mais iluminado.",
        "imagem_desfocada": "A imagem está desfocada. Tente novamente com mais nitidez.",
        "pele_molhada": "A pele parece estar molhada. Seque o rosto e envie uma nova foto.",
        "interferencia_visual": "Há uma interferência visual que dificulta a análise da pele. Envie uma foto natural, sem filtros, efeitos ou produtos visíveis.",
        "iluminacao_irregular": "A iluminação dificulta a análise da pele. Envie uma nova foto com luz uniforme, evitando sombras fortes ou luz direta intensa."
    }

    return mensagens.get(
        motivo,
        "A imagem não está adequada para análise. Tente enviar outra foto."
    )

def produto_para_dict(produto):
    return {
        "id": produto["id"],
        "nome": produto["nome"],
        "marca": produto["marca"],
        "descricao_curta": produto["descricao_curta"],
        "imagem_url": produto["imagem_url"],
        "conteudo": produto["conteudo"],
        "ativos_principais": produto["ativos_principais"],
        "preco": produto["preco"],
        "estoque": produto["estoque"],
        "tipo_pele": produto["tipo_pele"],
        "pele_sensivel": bool(produto["pele_sensivel"]),
        "indicado_para_espinha": bool(
            produto["indicado_para_espinha"]
        ),
        "ativo": bool(produto["ativo"]),
        "categoria": produto["categoria"],
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

def obter_motivos_compatibilidade(produto, perfil):
    motivos = []

    if produto["tipo_pele"] == perfil.tipo_pele:
        motivos.append(
            "Compatível com o tipo de pele identificado"
        )

    elif produto["tipo_pele"] == "todos":
        motivos.append(
            "Indicado para diferentes tipos de pele"
        )

    if perfil.sensivel is True and produto["pele_sensivel"]:
        motivos.append(
            "Adequado para pele sensível"
        )

    if perfil.tem_espinha is True and produto["indicado_para_espinha"]:
        motivos.append(
            "Indicado para pele com espinhas"
        )

    return motivos

def agrupar_por_categoria(produtos):
    recomendacoes_por_categoria = {}

    for produto in produtos:
        categoria = produto["categoria"]

        if categoria not in recomendacoes_por_categoria:
            recomendacoes_por_categoria[categoria] = []

        recomendacoes_por_categoria[categoria].append(produto)

    return recomendacoes_por_categoria

def buscar_produtos_compativeis(tipo_pele):
    with gerenciar_banco() as (conexao, cursor):
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

    return produtos

def gerar_recomendacoes(perfil):

    recomendacoes = buscar_produtos_compativeis(perfil.tipo_pele)

    lista_recomendacoes = []

    for recomendacao in recomendacoes:

        score = calcular_score(recomendacao, perfil)

        recomendacoes_atualizadas = produto_para_dict(recomendacao)

        motivos = obter_motivos_compatibilidade(
            recomendacao,
            perfil
        )

        recomendacoes_atualizadas["score"] = score
        
        recomendacoes_atualizadas["motivos_compatibilidade"] = motivos

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
