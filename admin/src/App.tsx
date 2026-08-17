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
} from './services/api'

import type {
  FiltrosProdutos,
  NovoProduto,
  Produto,
} from './types/produto'

import ProductFilters from './components/ProductFilters'
import ProductForm from './components/ProductForm'
import ProductTable from './components/ProductTable'

import './App.css'

const { Sider, Content } = Layout

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

  const [drawerAberto, setDrawerAberto] =
    useState(false)

  const [produtoEmEdicao, setProdutoEmEdicao] =
    useState<Produto | null>(null)

  const [salvandoProduto, setSalvandoProduto] =
    useState(false)

  const [
    produtoAlterandoStatus,
    setProdutoAlterandoStatus,
  ] = useState<number | null>(null)

  const [produtos, setProdutos] =
    useState<Produto[]>([])

  const [
    carregandoProdutos,
    setCarregandoProdutos,
  ] = useState(true)

  const [erroProdutos, setErroProdutos] =
    useState<string | null>(null)

  const [filtrosAtuais, setFiltrosAtuais] =
    useState<FiltrosProdutos>({
      ativo: true,
    })

  async function carregarProdutos(
    filtros: FiltrosProdutos = {},
  ) {
    try {
      setCarregandoProdutos(true)
      setErroProdutos(null)

      const produtosEncontrados =
        await buscarProdutos(filtros)

      setProdutos(produtosEncontrados)
    } catch {
      setErroProdutos(
        'Não foi possível carregar os produtos.',
      )
    } finally {
      setCarregandoProdutos(false)
    }
  }

  useEffect(() => {
    let ignorar = false

    async function carregarProdutosIniciais() {
      try {
        const produtosEncontrados =
          await buscarProdutos({
            ativo: true,
          })

        if (!ignorar) {
          setProdutos(produtosEncontrados)
        }
      } catch {
        if (!ignorar) {
          setErroProdutos(
            'Não foi possível carregar os produtos.',
          )
        }
      } finally {
        if (!ignorar) {
          setCarregandoProdutos(false)
        }
      }
    }

    carregarProdutosIniciais()

    return () => {
      ignorar = true
    }
  }, [])

  function aplicarFiltros(
    filtros: FiltrosProdutos,
  ) {
    setFiltrosAtuais(filtros)

    carregarProdutos(filtros)
  }

  async function salvarProduto(
    dadosProduto: NovoProduto,
  ) {
    const estaEditando =
      produtoEmEdicao !== null

    try {
      setSalvandoProduto(true)

      if (produtoEmEdicao) {
        await atualizarProduto(
          produtoEmEdicao.id,
          dadosProduto,
        )
      } else {
        await criarProduto(dadosProduto)
      }

      await carregarProdutos(filtrosAtuais)

      setDrawerAberto(false)
      setProdutoEmEdicao(null)

      if (estaEditando) {
        messageApi.success(
          'Produto atualizado com sucesso.',
        )
      } else {
        messageApi.success(
          'Produto cadastrado com sucesso.',
        )
      }
    } catch (erro) {
      const mensagemPadrao = estaEditando
        ? 'Não foi possível atualizar o produto.'
        : 'Não foi possível cadastrar o produto.'

      messageApi.error(
        obterMensagemErro(
          erro,
          mensagemPadrao,
        ),
      )
    } finally {
      setSalvandoProduto(false)
    }
  }

  function editarProduto(
    produto: Produto,
  ) {
    setProdutoEmEdicao(produto)
    setDrawerAberto(true)
  }

  async function alterarStatusProduto(
    produto: Produto,
  ) {
    try {
      setProdutoAlterandoStatus(produto.id)

      if (produto.ativo) {
        await desativarProduto(produto.id)
      } else {
        await reativarProduto(produto.id)
      }

      await carregarProdutos(filtrosAtuais)

      if (produto.ativo) {
        messageApi.success(
          'Produto desativado com sucesso.',
        )
      } else {
        messageApi.success(
          'Produto reativado com sucesso.',
        )
      }
    } catch (erro) {
      const mensagemPadrao = produto.ativo
        ? 'Não foi possível desativar o produto.'
        : 'Não foi possível reativar o produto.'

      messageApi.error(
        obterMensagemErro(
          erro,
          mensagemPadrao,
        ),
      )
    } finally {
      setProdutoAlterandoStatus(null)
    }
  }

  return (
    <Layout className="app-layout">
      {contextHolder}

      <Sider
        width={220}
        breakpoint='md'
        collapsedWidth={0}
        className="app-sider"
      >
        <div className="app-brand">
          <div className="app-brand-mark">
            S
          </div>

          <div className="app-brand-copy">
            <strong className="app-brand-name">
              Skin Admin
            </strong>

            <span className="app-brand-subtitle">
              Gestão de catálogo
            </span>
          </div>
        </div>

        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['produtos']}
          items={[
            {
              key: 'produtos',
              label: 'Produtos',
            },
          ]}
        />
      </Sider>

      <Layout>

        <Content className="app-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">
                Produtos
              </h1>

              <p className="page-description">
                Gerencie os produtos disponíveis no catálogo.
              </p>
            </div>

            <Button
              type="primary"
              onClick={() => {
                setProdutoEmEdicao(null)
                setDrawerAberto(true)
              }}
            >
              Novo produto
            </Button>
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

              <ProductFilters
                onFiltrar={aplicarFiltros}
              />
            </div>

            {erroProdutos && (
              <div className="products-alert">
                <Alert
                  type="error"
                  title={erroProdutos}
                  showIcon
                />
              </div>
            )}

            <ProductTable
              produtos={produtos}
              carregando={carregandoProdutos}
              produtoAlterandoStatus={
                produtoAlterandoStatus
              }
              onEditar={editarProduto}
              onAlterarStatus={alterarStatusProduto}
            />
          </div>
        </Content>

        <Drawer
          title={
            produtoEmEdicao
              ? 'Editar produto'
              : 'Novo produto'
          }
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