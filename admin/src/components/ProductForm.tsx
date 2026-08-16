import { useEffect } from 'react'

import {
  Button,
  Col,
  Divider,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Switch,
} from 'antd'

import type {
  NovoProduto,
  Produto,
} from '../types/produto'

interface ProductFormProps {
  onSubmit: (produto: NovoProduto) => Promise<void>
  produtoInicial?: Produto | null
  salvando: boolean
}

function ProductForm({
  onSubmit,
  produtoInicial,
  salvando,
}: ProductFormProps) {
  const [form] = Form.useForm<NovoProduto>()

  useEffect(() => {
    if (produtoInicial) {
      form.setFieldsValue(produtoInicial)
    } else {
      form.resetFields()
    }
  }, [form, produtoInicial])

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={onSubmit}
      initialValues={{
        pele_sensivel: false,
        indicado_para_espinha: false,
        ativo: true,
      }}
    >
      <Divider titlePlacement="start">
        Informações do produto
      </Divider>

      <Form.Item
        label="Nome"
        name="nome"
        rules={[
          {
            required: true,
            message: 'Informe o nome do produto.',
          },
        ]}
      >
        <Input
          placeholder="Ex.: Gel de limpeza facial"
          disabled={salvando}
        />
      </Form.Item>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            label="Preço"
            name="preco"
            rules={[
              {
                required: true,
                message: 'Informe o preço do produto.',
              },
            ]}
          >
            <InputNumber
              min={0.01}
              precision={2}
              step={0.01}
              decimalSeparator=","
              prefix="R$"
              style={{ width: '100%' }}
              disabled={salvando}
            />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            label="Estoque"
            name="estoque"
            rules={[
              {
                required: true,
                message: 'Informe o estoque do produto.',
              },
            ]}
          >
            <InputNumber
              min={0}
              precision={0}
              style={{ width: '100%' }}
              disabled={salvando}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            label="Categoria"
            name="categoria"
            rules={[
              {
                required: true,
                message: 'Selecione a categoria.',
              },
            ]}
          >
            <Select
              placeholder="Selecione"
              disabled={salvando}
              options={[
                {
                  value: 'limpeza',
                  label: 'Limpeza',
                },
                {
                  value: 'hidratante',
                  label: 'Hidratante',
                },
                {
                  value: 'serum',
                  label: 'Sérum',
                },
                {
                  value: 'protetor_solar',
                  label: 'Protetor solar',
                },
                {
                  value: 'outros',
                  label: 'Outros',
                },
              ]}
            />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            label="Tipo de pele"
            name="tipo_pele"
            rules={[
              {
                required: true,
                message: 'Selecione o tipo de pele.',
              },
            ]}
          >
            <Select
              placeholder="Selecione"
              disabled={salvando}
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
                  label: 'Todos os tipos',
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
        <Switch disabled={salvando} />
      </Form.Item>

      <Form.Item
        label="Indicado para pele com espinhas"
        name="indicado_para_espinha"
        valuePropName="checked"
      >
        <Switch disabled={salvando} />
      </Form.Item>

      <Divider titlePlacement="start">
        Disponibilidade
      </Divider>

      <Form.Item
        label="Produto ativo"
        name="ativo"
        valuePropName="checked"
      >
        <Switch disabled={salvando} />
      </Form.Item>

      <Button
        type="primary"
        htmlType="submit"
        loading={salvando}
        disabled={salvando}
      >
        {produtoInicial
          ? 'Salvar alterações'
          : 'Cadastrar produto'}
      </Button>
    </Form>
  )
}

export default ProductForm