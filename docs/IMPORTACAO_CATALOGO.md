# Importação de catálogo

Toda importação possui duas etapas: **prévia** e **confirmação**. Nada é gravado ao apenas enviar os dados.

## CSV ou XLSX

Limites: 5 MB e 1.000 produtos por arquivo. A primeira linha deve conter os nomes das colunas. Use `docs/modelo-catalogo.csv` ou baixe o modelo no painel.

Campos essenciais:

| Campo | Exemplo |
|---|---|
| `nome` | Gel de limpeza suave |
| `preco` | 39,90 |
| `categoria` | limpeza |
| `tipo_pele` | oleosa |

Campos opcionais: `marca`, `descricao_curta`, `imagem_url`, `conteudo`, `ativos_principais`, `estoque`, `pele_sensivel`, `indicado_para_espinha` e `ativo`.

Categorias aceitas: `limpeza`, `serum`, `hidratante`, `protetor_solar` e `outros`.

Tipos de pele aceitos: `oleosa`, `seca`, `mista`, `normal` e `todos`.

Valores booleanos podem usar `sim/não`, `true/false`, `1/0` ou `ativo/inativo`, conforme o campo.

## Texto desestruturado + IA

Cole uma lista, texto exportado ou linhas copiadas de outro sistema. A IA tenta separar até 100 produtos e normalizar os campos. Ela recebe instrução para não inventar informações; mesmo assim, a prévia deve ser revisada por uma pessoa.

Preço, categoria ou tipo de pele ausentes impedem a validação daquele item. Campos editoriais ausentes permanecem vazios.

## Duplicados

A comparação usa o nome sem diferenciar maiúsculas e minúsculas:

- **Ignorar:** mantém o registro existente;
- **Atualizar:** substitui os campos do registro existente pelos dados revisados.

O lote confirmado é processado em uma única transação. Se ocorrer uma falha inesperada, a transação é revertida.

## Imagens

A planilha pode apontar para uma URL já acessível. O importador não baixa imagens externas. Para armazenar a imagem junto da API, importe os dados e depois use o upload do formulário do produto.
