import {
  Button,
  Popconfirm,
  Space,
  Table,
  Tag,
} from 'antd'

import type { TableColumnsType } from 'antd'
import type { Produto } from '../types/produto'

interface ProductTableProps {
  produtos: Produto[]
  carregando: boolean
  produtoAlterandoStatus: number | null
  onEditar: (produto: Produto) => void
  onAlterarStatus: (produto: Produto) => void
}

const nomesCategorias = {
  limpeza: 'Limpeza',
  hidratante: 'Hidratante',
  serum: 'Sérum',
  protetor_solar: 'Protetor solar',
  outros: 'Outros',
}

const nomesTiposPele = {
  oleosa: 'Oleosa',
  seca: 'Seca',
  mista: 'Mista',
  normal: 'Normal',
  todos: 'Todos os tipos',
}

function ProductTable({
  produtos,
  carregando,
  produtoAlterandoStatus,
  onEditar,
  onAlterarStatus,
}: ProductTableProps) {
  const colunas: TableColumnsType<Produto> = [
    {
      title: 'Produto',
      dataIndex: 'nome',
      key: 'nome',
    },
    {
      title: 'Categoria',
      dataIndex: 'categoria',
      key: 'categoria',
      responsive: ['md'],
      render: (categoria: Produto['categoria']) =>
        nomesCategorias[categoria],
    },
    {
      title: 'Tipo de pele',
      dataIndex: 'tipo_pele',
      key: 'tipo_pele',
      responsive: ['lg'],
      render: (tipoPele: Produto['tipo_pele']) =>
        nomesTiposPele[tipoPele],
    },
    {
      title: 'Preço',
      dataIndex: 'preco',
      key: 'preco',
      render: (preco: number) =>
        new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL',
        }).format(preco),
    },
    {
      title: 'Estoque',
      dataIndex: 'estoque',
      key: 'estoque',
      responsive: ['md'],
      render: (estoque: number) =>
        estoque === 0 ? (
          <Tag color="warning">
            Sem estoque
          </Tag>
        ) : (
          `${estoque} un.`
        ),
    },
    {
      title: 'Status',
      dataIndex: 'ativo',
      key: 'ativo',
      render: (ativo: boolean) => (
        <Tag color={ativo ? 'success' : 'default'}>
          {ativo ? 'Ativo' : 'Inativo'}
        </Tag>
      ),
    },
    {
      title: 'Ações',
      key: 'acoes',
      width: 170,
      fixed: 'right',
      render: (_, produto) => (
        <Space size="small">
          <Button
            type="link"
            onClick={() => onEditar(produto)}
          >
            Editar
          </Button>

          <Popconfirm
            title={
              produto.ativo
                ? 'Desativar produto?'
                : 'Reativar produto?'
            }
            description={
              produto.ativo
                ? 'O produto deixará de aparecer nas recomendações.'
                : 'O produto voltará a ficar disponível no catálogo.'
            }
            okText="Confirmar"
            cancelText="Cancelar"
            onConfirm={() =>
              onAlterarStatus(produto)
            }
          >
            <Button
              type="text"
              size="small"
              danger={produto.ativo}
              loading={
                produtoAlterandoStatus === produto.id
              }
              disabled={
                produtoAlterandoStatus !== null
              }
            >
              {produto.ativo
                ? 'Desativar'
                : 'Reativar'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Table
      dataSource={produtos}
      columns={colunas}
      rowKey="id"
      loading={carregando}
      scroll={{
        x: 1050,
      }}
      locale={{
        emptyText: 'Nenhum produto encontrado.',
      }}
    />
  )
}

export default ProductTable