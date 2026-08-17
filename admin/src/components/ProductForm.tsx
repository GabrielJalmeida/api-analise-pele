import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  Alert,
  Button,
  Col,
  Divider,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Switch,
  Upload,
} from 'antd'

import type {
  NovoProduto,
  Produto,
} from '../types/produto'

import {
  enviarImagemProduto,
} from '../services/api'


type DadosFormularioProduto =
  Omit<NovoProduto, 'imagem_url'>


interface ProductFormProps {
  onSubmit: (
    produto: NovoProduto,
  ) => Promise<void>

  produtoInicial?: Produto | null
  salvando: boolean
}


const API_URL = (
  import.meta.env.VITE_API_URL ?? ''
).replace(/\/$/, '')


function montarUrlImagem(
  imagemUrl: string,
): string {
  if (
    imagemUrl.startsWith('http://')
    || imagemUrl.startsWith('https://')
  ) {
    return imagemUrl
  }

  return `${API_URL}${imagemUrl}`
}


function ProductForm({
  onSubmit,
  produtoInicial,
  salvando,
}: ProductFormProps) {
  const [form] =
    Form.useForm<DadosFormularioProduto>()

  const [
    arquivoImagem,
    setArquivoImagem,
  ] = useState<File | null>(null)

  const [
    previewLocal,
    setPreviewLocal,
  ] = useState<string | null>(null)

  const previewLocalRef =
    useRef<string | null>(null)

  const [
    processandoImagem,
    setProcessandoImagem,
  ] = useState(false)

  const [
    erroImagem,
    setErroImagem,
  ] = useState<string | null>(null)


  const ocupado =
    salvando || processandoImagem


  useEffect(() => {
    if (produtoInicial) {
      form.setFieldsValue({
        nome: produtoInicial.nome,
        marca: produtoInicial.marca,
        descricao_curta:
          produtoInicial.descricao_curta,
        conteudo:
          produtoInicial.conteudo,
        ativos_principais:
          produtoInicial.ativos_principais,
        preco: produtoInicial.preco,
        estoque: produtoInicial.estoque,
        categoria:
          produtoInicial.categoria,
        tipo_pele:
          produtoInicial.tipo_pele,
        pele_sensivel:
          produtoInicial.pele_sensivel,
        indicado_para_espinha:
          produtoInicial.indicado_para_espinha,
        ativo: produtoInicial.ativo,
      })
    } else {
      form.resetFields()

      form.setFieldsValue({
        marca: 'Lumina Skin',
        pele_sensivel: false,
        indicado_para_espinha: false,
        ativo: true,
      })
    }
  }, [
    form,
    produtoInicial,
  ])

  useEffect(() => {
    return () => {
      if (previewLocalRef.current) {
        URL.revokeObjectURL(
          previewLocalRef.current,
        )
      }
    }
  }, [])


  const previewImagem =
    previewLocal
    ?? (
      produtoInicial?.imagem_url
        ? montarUrlImagem(
          produtoInicial.imagem_url,
        )
        : null
    )


  function restaurarImagemAtual() {
    if (previewLocalRef.current) {
      URL.revokeObjectURL(
        previewLocalRef.current,
      )

      previewLocalRef.current = null
    }

    setArquivoImagem(null)
    setPreviewLocal(null)
    setErroImagem(null)
  }


  async function enviarFormulario(
    valores: DadosFormularioProduto,
  ) {
    setErroImagem(null)

    if (
      !produtoInicial
      && !arquivoImagem
    ) {
      setErroImagem(
        'Selecione uma imagem para o produto.',
      )

      return
    }

    setProcessandoImagem(true)

    try {
      let imagemUrl =
        produtoInicial?.imagem_url ?? ''

      if (arquivoImagem) {
        const resultado =
          await enviarImagemProduto(
            arquivoImagem,
            valores.nome,
            valores.categoria,
          )

        imagemUrl =
          resultado.imagem_url
      }

      await onSubmit({
        ...valores,
        imagem_url: imagemUrl,
      })
    } catch (erro) {
      if (erro instanceof Error) {
        setErroImagem(
          erro.message,
        )
      } else {
        setErroImagem(
          'Não foi possível processar a imagem do produto.',
        )
      }
    } finally {
      setProcessandoImagem(false)
    }
  }


  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={enviarFormulario}
      initialValues={{
        marca: 'Lumina Skin',
        pele_sensivel: false,
        indicado_para_espinha: false,
        ativo: true,
      }}
    >
      <Divider titlePlacement="start">
        Imagem e identidade
      </Divider>

      <Form.Item label="Imagem do produto">
        <div
          style={{
            border:
              '1px solid #d9d9d9',
            borderRadius: 12,
            overflow: 'hidden',
            background: '#fafafa',
          }}
        >
          {previewImagem ? (
            <div
              style={{
                height: 260,
                display: 'flex',
                alignItems: 'center',
                justifyContent:
                  'center',
                padding: 16,
              }}
            >
              <img
                src={previewImagem}
                alt="Pré-visualização do produto"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  borderRadius: 8,
                }}
              />
            </div>
          ) : (
            <div
              style={{
                height: 180,
                display: 'flex',
                alignItems: 'center',
                justifyContent:
                  'center',
                color: '#8c8c8c',
                padding: 24,
                textAlign: 'center',
              }}
            >
              Nenhuma imagem selecionada.
            </div>
          )}

          <div
            style={{
              padding: 16,
              borderTop:
                '1px solid #f0f0f0',
            }}
          >
            <Upload
              accept="image/jpeg,image/png,image/webp"
              maxCount={1}
              showUploadList={false}
              disabled={ocupado}
              beforeUpload={(arquivo) => {
                if (previewLocalRef.current) {
                  URL.revokeObjectURL(
                    previewLocalRef.current,
                  )
                }

                const novaPreview =
                  URL.createObjectURL(arquivo)

                previewLocalRef.current =
                  novaPreview

                setPreviewLocal(
                  novaPreview,
                )

                setArquivoImagem(
                  arquivo,
                )

                setErroImagem(null)

                return false
              }}
            >
              <Button
                disabled={ocupado}
              >
                {previewImagem
                  ? 'Escolher outra imagem'
                  : 'Selecionar imagem'}
              </Button>
            </Upload>

            {arquivoImagem && (
              <div
                style={{
                  marginTop: 12,
                }}
              >
                <div>
                  <strong>
                    Novo arquivo:
                  </strong>{' '}
                  {arquivoImagem.name}
                </div>

                {produtoInicial && (
                  <Button
                    type="link"
                    onClick={
                      restaurarImagemAtual
                    }
                    disabled={ocupado}
                    style={{
                      paddingLeft: 0,
                    }}
                  >
                    Manter imagem atual
                  </Button>
                )}
              </div>
            )}

            <div
              style={{
                marginTop: 8,
                color: '#8c8c8c',
                fontSize: 12,
              }}
            >
              JPG, PNG ou WEBP.
              O backend otimiza e
              renomeia o arquivo
              automaticamente.
            </div>
          </div>
        </div>
      </Form.Item>

      {erroImagem && (
        <Alert
          type="error"
          showIcon
          message={erroImagem}
          style={{
            marginBottom: 24,
          }}
        />
      )}

      <Row gutter={16}>
        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Nome"
            name="nome"
            rules={[
              {
                required: true,
                message:
                  'Informe o nome do produto.',
              },
              {
                min: 2,
                message:
                  'O nome deve ter pelo menos 2 caracteres.',
              },
              {
                max: 100,
                message:
                  'O nome não pode ultrapassar 100 caracteres.',
              },
            ]}
          >
            <Input
              placeholder="Ex.: Pérola Hialurônica"
              disabled={ocupado}
              maxLength={100}
            />
          </Form.Item>
        </Col>

        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Marca"
            name="marca"
            rules={[
              {
                required: true,
                message:
                  'Informe a marca.',
              },
              {
                min: 2,
                message:
                  'A marca deve ter pelo menos 2 caracteres.',
              },
              {
                max: 60,
                message:
                  'A marca não pode ultrapassar 60 caracteres.',
              },
            ]}
          >
            <Input
              placeholder="Lumina Skin"
              disabled={ocupado}
              maxLength={60}
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        label="Descrição curta"
        name="descricao_curta"
        rules={[
          {
            required: true,
            message:
              'Informe uma descrição.',
          },
          {
            min: 10,
            message:
              'A descrição deve ter pelo menos 10 caracteres.',
          },
          {
            max: 300,
            message:
              'A descrição não pode ultrapassar 300 caracteres.',
          },
        ]}
      >
        <Input.TextArea
          placeholder={
            'Ex.: Sérum hidratante de textura leve para reforçar o conforto e a hidratação da pele.'
          }
          rows={4}
          maxLength={300}
          showCount
          disabled={ocupado}
        />
      </Form.Item>

      <Row gutter={16}>
        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Conteúdo"
            name="conteudo"
            rules={[
              {
                required: true,
                message:
                  'Informe o conteúdo.',
              },
              {
                max: 30,
                message:
                  'O conteúdo não pode ultrapassar 30 caracteres.',
              },
            ]}
          >
            <Input
              placeholder="Ex.: 30 ml"
              maxLength={30}
              disabled={ocupado}
            />
          </Form.Item>
        </Col>

        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Ativos principais"
            name="ativos_principais"
            rules={[
              {
                required: true,
                message:
                  'Informe os principais ativos.',
              },
              {
                max: 200,
                message:
                  'Os ativos não podem ultrapassar 200 caracteres.',
              },
            ]}
          >
            <Input
              placeholder={
                'Ex.: Ácido hialurônico e pantenol'
              }
              maxLength={200}
              disabled={ocupado}
            />
          </Form.Item>
        </Col>
      </Row>

      <Divider titlePlacement="start">
        Informações comerciais
      </Divider>

      <Row gutter={16}>
        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Preço"
            name="preco"
            rules={[
              {
                required: true,
                message:
                  'Informe o preço do produto.',
              },
            ]}
          >
            <InputNumber
              min={0.01}
              precision={2}
              step={0.01}
              decimalSeparator=","
              prefix="R$"
              style={{
                width: '100%',
              }}
              disabled={ocupado}
            />
          </Form.Item>
        </Col>

        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Estoque"
            name="estoque"
            rules={[
              {
                required: true,
                message:
                  'Informe o estoque do produto.',
              },
            ]}
          >
            <InputNumber
              min={0}
              precision={0}
              style={{
                width: '100%',
              }}
              disabled={ocupado}
            />
          </Form.Item>
        </Col>
      </Row>

      <Divider titlePlacement="start">
        Recomendação
      </Divider>

      <Row gutter={16}>
        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Categoria"
            name="categoria"
            rules={[
              {
                required: true,
                message:
                  'Selecione a categoria.',
              },
            ]}
          >
            <Select
              placeholder="Selecione"
              disabled={ocupado}
              options={[
                {
                  value: 'limpeza',
                  label: 'Limpeza',
                },
                {
                  value:
                    'hidratante',
                  label:
                    'Hidratante',
                },
                {
                  value: 'serum',
                  label: 'Sérum',
                },
                {
                  value:
                    'protetor_solar',
                  label:
                    'Protetor solar',
                },
                {
                  value: 'outros',
                  label: 'Outros',
                },
              ]}
            />
          </Form.Item>
        </Col>

        <Col
          xs={24}
          sm={12}
        >
          <Form.Item
            label="Tipo de pele"
            name="tipo_pele"
            rules={[
              {
                required: true,
                message:
                  'Selecione o tipo de pele.',
              },
            ]}
          >
            <Select
              placeholder="Selecione"
              disabled={ocupado}
              options={[
                {
                  value: 'oleosa',
                  label: 'Oleosa',
                },
                {
                  value: 'seca',
                  label: 'Seca',
                },
                {
                  value: 'mista',
                  label: 'Mista',
                },
                {
                  value: 'normal',
                  label: 'Normal',
                },
                {
                  value: 'todos',
                  label:
                    'Todos os tipos',
                },
              ]}
            />
          </Form.Item>
        </Col>
      </Row>

      <Divider titlePlacement="start">
        Compatibilidade
      </Divider>

      <Form.Item
        label="Adequado para pele sensível"
        name="pele_sensivel"
        valuePropName="checked"
      >
        <Switch
          disabled={ocupado}
        />
      </Form.Item>

      <Form.Item
        label="Indicado para pele com espinhas"
        name="indicado_para_espinha"
        valuePropName="checked"
      >
        <Switch
          disabled={ocupado}
        />
      </Form.Item>

      <Divider titlePlacement="start">
        Disponibilidade
      </Divider>

      <Form.Item
        label="Produto ativo"
        name="ativo"
        valuePropName="checked"
      >
        <Switch
          disabled={ocupado}
        />
      </Form.Item>

      <Button
        type="primary"
        htmlType="submit"
        loading={ocupado}
        disabled={ocupado}
      >
        {produtoInicial
          ? 'Salvar alterações'
          : 'Cadastrar produto'}
      </Button>
    </Form>
  )
}

export default ProductForm