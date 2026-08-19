import { useState } from 'react'

import {
  Alert,
  Button,
  Card,
  Input,
  Radio,
  Space,
  Table,
  Tabs,
  Tag,
  Upload,
} from 'antd'

import type { TableColumnsType } from 'antd'
import type {
  NovoProduto,
  PoliticaDuplicados,
  PreviaImportacao,
} from '../types/produto'

import {
  confirmarImportacao,
  criarPreviaArquivo,
  criarPreviaComIa,
  ErroApi,
} from '../services/api'


interface BulkImportProps {
  onConcluido: () => Promise<void>
}


function mensagemErro(erro: unknown): string {
  if (erro instanceof ErroApi || erro instanceof Error) {
    return erro.message
  }

  return 'Não foi possível processar o catálogo.'
}


function baixarModelo() {
  const cabecalho = [
    'nome',
    'marca',
    'descricao_curta',
    'preco',
    'estoque',
    'categoria',
    'tipo_pele',
    'pele_sensivel',
    'indicado_para_espinha',
    'conteudo',
    'ativos_principais',
    'imagem_url',
    'ativo',
  ].join(';')

  const exemplo = [
    'Gel de limpeza exemplo',
    'Minha marca',
    'Limpeza suave para a rotina diária',
    '39,90',
    '10',
    'limpeza',
    'oleosa',
    'sim',
    'sim',
    '150 ml',
    'Niacinamida e pantenol',
    '',
    'sim',
  ].join(';')

  const blob = new Blob(
    [`\uFEFF${cabecalho}\n${exemplo}\n`],
    { type: 'text/csv;charset=utf-8' },
  )
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'modelo-catalogo.csv'
  link.click()
  URL.revokeObjectURL(url)
}


function BulkImport({
  onConcluido,
}: BulkImportProps) {
  const [arquivo, setArquivo] =
    useState<File | null>(null)
  const [texto, setTexto] = useState('')
  const [previa, setPrevia] =
    useState<PreviaImportacao | null>(null)
  const [erro, setErro] =
    useState<string | null>(null)
  const [processando, setProcessando] =
    useState(false)
  const [importando, setImportando] =
    useState(false)
  const [duplicados, setDuplicados] =
    useState<PoliticaDuplicados>('ignorar')

  const colunas: TableColumnsType<NovoProduto> = [
    {
      title: 'Produto',
      dataIndex: 'nome',
      key: 'nome',
    },
    {
      title: 'Preço',
      dataIndex: 'preco',
      key: 'preco',
      width: 120,
      render: (valor: number) =>
        new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL',
        }).format(valor),
    },
    {
      title: 'Categoria',
      dataIndex: 'categoria',
      key: 'categoria',
      width: 150,
    },
    {
      title: 'Pele',
      dataIndex: 'tipo_pele',
      key: 'tipo_pele',
      width: 120,
    },
    {
      title: 'Estoque',
      dataIndex: 'estoque',
      key: 'estoque',
      width: 100,
    },
  ]

  async function processarArquivo() {
    if (!arquivo) {
      setErro('Escolha um arquivo CSV ou XLSX.')
      return
    }

    try {
      setProcessando(true)
      setErro(null)
      setPrevia(await criarPreviaArquivo(arquivo))
    } catch (erroRecebido) {
      setErro(mensagemErro(erroRecebido))
    } finally {
      setProcessando(false)
    }
  }

  async function organizarComIa() {
    if (texto.trim().length < 5) {
      setErro('Cole os dados de pelo menos um produto.')
      return
    }

    try {
      setProcessando(true)
      setErro(null)
      setPrevia(await criarPreviaComIa(texto.trim()))
    } catch (erroRecebido) {
      setErro(mensagemErro(erroRecebido))
    } finally {
      setProcessando(false)
    }
  }

  async function importar() {
    if (!previa?.produtos.length) {
      return
    }

    try {
      setImportando(true)
      setErro(null)
      const resultado = await confirmarImportacao(
        previa.produtos,
        duplicados,
      )

      await onConcluido()
      setPrevia(null)
      setArquivo(null)
      setTexto('')
      setErro(
        `Concluído: ${resultado.criados} criados, ${resultado.atualizados} atualizados e ${resultado.ignorados} ignorados.`,
      )
    } catch (erroRecebido) {
      setErro(mensagemErro(erroRecebido))
    } finally {
      setImportando(false)
    }
  }

  return (
    <div className="import-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Importar catálogo
          </h1>
          <p className="page-description">
            Cadastre muitos produtos com planilha ou organize dados soltos com IA.
          </p>
        </div>

        <Button onClick={baixarModelo}>
          Baixar modelo CSV
        </Button>
      </div>

      <Alert
        type="info"
        showIcon
        title="Você sempre revisa antes de gravar"
        description="A IA organiza os dados, mas não publica nada automaticamente. Campos essenciais ausentes aparecem como erro para correção."
        className="import-guidance"
      />

      <Card>
        <Tabs
          items={[
            {
              key: 'arquivo',
              label: 'CSV ou Excel',
              children: (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Upload.Dragger
                    accept=".csv,.xlsx"
                    maxCount={1}
                    beforeUpload={(novoArquivo) => {
                      setArquivo(novoArquivo)
                      setPrevia(null)
                      setErro(null)
                      return false
                    }}
                    onRemove={() => {
                      setArquivo(null)
                      setPrevia(null)
                    }}
                  >
                    <p className="ant-upload-text">
                      Arraste a planilha ou clique para escolher
                    </p>
                    <p className="ant-upload-hint">
                      Até 1.000 produtos em CSV ou XLSX, máximo de 5 MB.
                    </p>
                  </Upload.Dragger>

                  <Button
                    type="primary"
                    onClick={processarArquivo}
                    loading={processando}
                    disabled={!arquivo}
                  >
                    Preparar prévia
                  </Button>
                </Space>
              ),
            },
            {
              key: 'ia',
              label: 'Dados bagunçados + IA',
              children: (
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <p className="import-helper">
                    Cole texto, linhas copiadas de outro sistema ou uma lista informal. A IA usa o provedor configurado na API e não inventa dados ausentes.
                  </p>
                  <Input.TextArea
                    value={texto}
                    onChange={(evento) => {
                      setTexto(evento.target.value)
                      setPrevia(null)
                    }}
                    rows={9}
                    maxLength={50000}
                    showCount
                    placeholder={'Ex.:\nGel Calmante, marca Aurora, R$ 42,90, limpeza, pele sensível, estoque 8\nSérum C 10%, 30 ml, R$ 69,90, pele mista'}
                  />
                  <Button
                    type="primary"
                    onClick={organizarComIa}
                    loading={processando}
                    disabled={texto.trim().length < 5}
                  >
                    Organizar e revisar
                  </Button>
                </Space>
              ),
            },
          ]}
        />
      </Card>

      {erro && (
        <Alert
          className="import-feedback"
          type={erro.startsWith('Concluído:') ? 'success' : 'error'}
          showIcon
          title={erro}
        />
      )}

      {previa && (
        <Card className="import-preview" title="Prévia da importação">
          <Space wrap className="import-summary">
            <Tag color="blue">{previa.total_linhas} linhas</Tag>
            <Tag color="success">{previa.total_validos} válidos</Tag>
            <Tag color={previa.total_erros ? 'error' : 'default'}>
              {previa.total_erros} erros
            </Tag>
          </Space>

          <Table
            dataSource={previa.produtos}
            columns={colunas}
            rowKey={(produto) => produto.nome}
            pagination={{ pageSize: 8 }}
            scroll={{ x: 760 }}
            locale={{ emptyText: 'Nenhum produto válido para importar.' }}
          />

          {previa.erros.length > 0 && (
            <div className="import-errors">
              <strong>Linhas que precisam de correção</strong>
              <ul>
                {previa.erros.slice(0, 50).map((item, indice) => (
                  <li key={`${item.linha}-${item.campo}-${indice}`}>
                    Linha {item.linha}, {item.campo}: {item.mensagem}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="import-confirmation">
            <div>
              <strong>Quando um nome já existir:</strong>
              <Radio.Group
                value={duplicados}
                onChange={(evento) => setDuplicados(evento.target.value)}
                className="import-duplicate-choice"
              >
                <Radio value="ignorar">Manter o atual</Radio>
                <Radio value="atualizar">Atualizar com a planilha</Radio>
              </Radio.Group>
            </div>

            <Button
              type="primary"
              size="large"
              loading={importando}
              disabled={previa.produtos.length === 0}
              onClick={importar}
            >
              Importar {previa.produtos.length} produtos
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}

export default BulkImport
