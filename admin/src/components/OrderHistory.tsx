import { useEffect, useState } from 'react'

import {
  Alert,
  Button,
  Empty,
  Table,
  Tag,
} from 'antd'

import type { TableColumnsType } from 'antd'
import type { Pedido } from '../types/produto'
import { buscarPedidos, ErroApi } from '../services/api'


function formatarMoeda(valor: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(valor)
}


function formatarData(valor: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(valor))
}


function OrderHistory() {
  const [pedidos, setPedidos] = useState<Pedido[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  async function carregar() {
    try {
      setCarregando(true)
      setErro(null)
      setPedidos(await buscarPedidos())
    } catch (erroRecebido) {
      setErro(
        erroRecebido instanceof ErroApi
          ? erroRecebido.message
          : 'Não foi possível carregar os pedidos.',
      )
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    let ignorar = false

    buscarPedidos()
      .then((encontrados) => {
        if (!ignorar) {
          setPedidos(encontrados)
        }
      })
      .catch((erroRecebido) => {
        if (!ignorar) {
          setErro(
            erroRecebido instanceof ErroApi
              ? erroRecebido.message
              : 'Não foi possível carregar os pedidos.',
          )
        }
      })
      .finally(() => {
        if (!ignorar) {
          setCarregando(false)
        }
      })

    return () => {
      ignorar = true
    }
  }, [])

  const colunas: TableColumnsType<Pedido> = [
    {
      title: 'Código',
      dataIndex: 'codigo',
      key: 'codigo',
    },
    {
      title: 'Cliente',
      key: 'cliente',
      render: (_, pedido) => (
        <div>
          <strong>{pedido.cliente_nome}</strong>
          <div className="order-email">{pedido.cliente_email}</div>
        </div>
      ),
    },
    {
      title: 'Data',
      dataIndex: 'criado_em',
      key: 'criado_em',
      render: formatarData,
    },
    {
      title: 'Itens',
      key: 'itens',
      render: (_, pedido) => pedido.itens.reduce(
        (total, item) => total + item.quantidade,
        0,
      ),
    },
    {
      title: 'Total',
      dataIndex: 'total',
      key: 'total',
      render: formatarMoeda,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: Pedido['status']) => (
        <Tag color={status === 'registrado' ? 'success' : 'default'}>
          {status === 'registrado' ? 'Registrado' : 'Cancelado'}
        </Tag>
      ),
    },
  ]

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Pedidos demonstrativos</h1>
          <p className="page-description">
            Histórico sem pagamento, mantido por até 365 dias mediante consentimento.
          </p>
        </div>
        <Button onClick={carregar} loading={carregando}>
          Atualizar
        </Button>
      </div>

      <Alert
        type="warning"
        showIcon
        title="Este módulo não processa pagamentos"
        description="Ele registra uma simulação de pedido e uma fotografia dos produtos e preços no momento da escolha. Não armazene dados de cartão."
        className="orders-guidance"
      />

      {erro && (
        <Alert type="error" showIcon title={erro} className="products-alert" />
      )}

      <div className="products-panel">
        <Table
          dataSource={pedidos}
          columns={colunas}
          rowKey="codigo"
          loading={carregando}
          scroll={{ x: 900 }}
          locale={{
            emptyText: (
              <Empty description="Nenhum pedido registrado." />
            ),
          }}
          expandable={{
            expandedRowRender: (pedido) => (
              <div className="order-items">
                {pedido.itens.map((item) => (
                  <div key={`${pedido.codigo}-${item.produto_id}-${item.nome_produto}`}>
                    <span>{item.quantidade}× {item.nome_produto}</span>
                    <strong>{formatarMoeda(item.subtotal)}</strong>
                  </div>
                ))}
                <p>Expira em {formatarData(pedido.expira_em)}</p>
              </div>
            ),
          }}
        />
      </div>
    </div>
  )
}

export default OrderHistory
