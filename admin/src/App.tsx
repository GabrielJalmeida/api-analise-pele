import { useEffect, useState } from 'react'

import {
  Alert,
  Button,
  Drawer,
  Layout,
  Menu,
  message,
} from 'antd'

import {
  atualizarProduto,
  buscarProdutos,
  criarProduto,
  desativarProduto,
  ErroApi,
  reativarProduto,
  aguardarApiLocal,
} from './services/api'

import type {
  FiltrosProdutos,
  NovoProduto,
  Produto,
} from './types/produto'

import BulkImport from './components/BulkImport'
import AiSettings from './components/AiSettings'
import OrderHistory from './components/OrderHistory'
import ProductFilters from './components/ProductFilters'
import ProductForm from './components/ProductForm'
import ProductTable from './components/ProductTable'

import './App.css'


const { Sider, Content } = Layout

type SecaoPainel = 'produtos' | 'importar' | 'pedidos' | 'ia'


function obterMensagemErro(
  erro: unknown,
  mensagemPadrao: string,
) {
  if (erro instanceof ErroApi) {
    return erro.message
  }

  if (erro instanceof TypeError) {
    return 'Não foi possível conectar ao servidor.'
  }

  return mensagemPadrao
}


function App() {
  const [messageApi, contextHolder] = message.useMessage()
  const [secao, setSecao] =
    useState<SecaoPainel>('produtos')
  const [drawerAberto, setDrawerAberto] =
    useState(false)
  const [produtoEmEdicao, setProdutoEmEdicao] =
    useState<Produto | null>(null)
  const [salvandoProduto, setSalvandoProduto] =
    useState(false)
  const [produtoAlterandoStatus, setProdutoAlterandoStatus] =
    useState<number | null>(null)
  const [produtos, setProdutos] =
    useState<Produto[]>([])
  const [carregandoProdutos, setCarregandoProdutos] =
    useState(true)
  const [erroProdutos, setErroProdutos] =
    useState<string | null>(null)
  const [filtrosAtuais, setFiltrosAtuais] =
    useState<FiltrosProdutos>({ ativo: true })

  async function carregarProdutos(
    filtros: FiltrosProdutos = filtrosAtuais,
  ) {
    try {
      setCarregandoProdutos(true)
      setErroProdutos(null)
      setProdutos(await buscarProdutos(filtros))
    } catch {
      setErroProdutos('Não foi possível carregar os produtos.')
    } finally {
      setCarregandoProdutos(false)
    }
  }

  useEffect(() => {
    let ignorar = false

    aguardarApiLocal()
      .then(() => buscarProdutos({ ativo: true }))
      .then((encontrados) => {
        if (!ignorar) {
          setProdutos(encontrados)
        }
      })
      .catch(() => {
        if (!ignorar) {
          setErroProdutos('Não foi possível carregar os produtos.')
        }
      })
      .finally(() => {
        if (!ignorar) {
          setCarregandoProdutos(false)
        }
      })

    return () => {
      ignorar = true
    }
  }, [])

  function aplicarFiltros(filtros: FiltrosProdutos) {
    setFiltrosAtuais(filtros)
    carregarProdutos(filtros)
  }

  async function salvarProduto(dadosProduto: NovoProduto) {
    const estaEditando = produtoEmEdicao !== null

    try {
      setSalvandoProduto(true)

      if (produtoEmEdicao) {
        await atualizarProduto(produtoEmEdicao.id, dadosProduto)
      } else {
        await criarProduto(dadosProduto)
      }

      await carregarProdutos()
      setDrawerAberto(false)
      setProdutoEmEdicao(null)
      messageApi.success(
        estaEditando
          ? 'Produto atualizado com sucesso.'
          : 'Produto cadastrado com sucesso.',
      )
    } catch (erro) {
      messageApi.error(
        obterMensagemErro(
          erro,
          estaEditando
            ? 'Não foi possível atualizar o produto.'
            : 'Não foi possível cadastrar o produto.',
        ),
      )

      throw erro
    } finally {
      setSalvandoProduto(false)
    }
  }

  async function alterarStatusProduto(produto: Produto) {
    try {
      setProdutoAlterandoStatus(produto.id)

      if (produto.ativo) {
        await desativarProduto(produto.id)
      } else {
        await reativarProduto(produto.id)
      }

      await carregarProdutos()
      messageApi.success(
        produto.ativo
          ? 'Produto desativado com sucesso.'
          : 'Produto reativado com sucesso.',
      )
    } catch (erro) {
      messageApi.error(
        obterMensagemErro(
          erro,
          'Não foi possível alterar o produto.',
        ),
      )
    } finally {
      setProdutoAlterandoStatus(null)
    }
  }

  function abrirNovoProduto() {
    setProdutoEmEdicao(null)
    setDrawerAberto(true)
  }

  function conteudoProdutos() {
    return (
      <>
        <div className="page-header">
          <div>
            <h1 className="page-title">Produtos</h1>
            <p className="page-description">
              Gerencie os itens usados pelas recomendações da API.
            </p>
          </div>
          <div className="page-actions">
            <Button onClick={() => setSecao('importar')}>
              Importar vários
            </Button>
            <Button type="primary" onClick={abrirNovoProduto}>
              Novo produto
            </Button>
          </div>
        </div>

        <div className="products-panel">
          <div className="products-toolbar">
            <div className="products-count">
              <strong>{produtos.length}</strong>
              <span>
                {produtos.length === 1
                  ? 'produto encontrado'
                  : 'produtos encontrados'}
              </span>
            </div>
            <ProductFilters onFiltrar={aplicarFiltros} />
          </div>

          {erroProdutos && (
            <div className="products-alert">
              <Alert type="error" title={erroProdutos} showIcon />
            </div>
          )}

          <ProductTable
            produtos={produtos}
            carregando={carregandoProdutos}
            produtoAlterandoStatus={produtoAlterandoStatus}
            onEditar={(produto) => {
              setProdutoEmEdicao(produto)
              setDrawerAberto(true)
            }}
            onAlterarStatus={alterarStatusProduto}
          />
        </div>
      </>
    )
  }

  return (
    <Layout className="app-layout">
      {contextHolder}

      <Sider
        width={232}
        breakpoint="md"
        collapsedWidth={0}
        className="app-sider"
      >
        <div className="app-brand">
          <div className="app-brand-mark">X</div>
          <div className="app-brand-copy">
            <strong className="app-brand-name">Skin Admin</strong>
            <span className="app-brand-subtitle">Versão X · catálogo local</span>
          </div>
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[secao]}
          onClick={({ key }) => setSecao(key as SecaoPainel)}
          items={[
            { key: 'produtos', label: 'Produtos' },
            { key: 'importar', label: 'Importar catálogo' },
            { key: 'pedidos', label: 'Pedidos' },
            { key: 'ia', label: 'Configurar IA' },
          ]}
        />

        <div className="app-local-note">
          Dados deste painel ficam no computador em que a API desktop está instalada.
        </div>
      </Sider>

      <Layout>
        <Content className="app-content">
          {secao === 'produtos' && conteudoProdutos()}
          {secao === 'importar' && (
            <BulkImport
              onConcluido={async () => {
                await carregarProdutos()
                messageApi.success('Catálogo atualizado.')
              }}
            />
          )}
          {secao === 'pedidos' && <OrderHistory />}
          {secao === 'ia' && <AiSettings />}
        </Content>

        <Drawer
          title={produtoEmEdicao ? 'Editar produto' : 'Novo produto'}
          open={drawerAberto}
          onClose={() => {
            setProdutoEmEdicao(null)
            setDrawerAberto(false)
          }}
          size="large"
          destroyOnHidden
        >
          <ProductForm
            key={produtoEmEdicao?.id ?? 'novo'}
            onSubmit={salvarProduto}
            produtoInicial={produtoEmEdicao}
            salvando={salvandoProduto}
          />
        </Drawer>
      </Layout>
    </Layout>
  )
}

export default App
