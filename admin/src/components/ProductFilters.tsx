import { Button, Form, Input, Select } from 'antd'
import type { FiltrosProdutos } from '../types/produto'

interface ProductFiltersProps {
  onFiltrar: (filtros: FiltrosProdutos) => void
}

function ProductFilters({
  onFiltrar,
}: ProductFiltersProps) {
  return (
    <Form
      layout="inline"
      initialValues={{
        ativo: true,
      }}
      onFinish={onFiltrar}
      className="product-filters"
    >
      <Form.Item name="busca">
        <Input
          placeholder="Buscar produto"
          allowClear
        />
      </Form.Item>

      <Form.Item name="categoria">
        <Select
          placeholder="Categoria"
          allowClear
          style={{ width: 160 }}
          options={[
            { value: 'limpeza', label: 'Limpeza' },
            { value: 'hidratante', label: 'Hidratante' },
            { value: 'serum', label: 'Sérum' },
            { value: 'protetor_solar', label: 'Protetor solar' },
            { value: 'outros', label: 'Outros' },
          ]}
        />
      </Form.Item>

      <Form.Item name="tipo_pele">
        <Select
          placeholder="Tipo de pele"
          allowClear
          style={{ width: 160 }}
          options={[
            { value: 'oleosa', label: 'Oleosa' },
            { value: 'seca', label: 'Seca' },
            { value: 'mista', label: 'Mista' },
            { value: 'normal', label: 'Normal' },
            { value: 'todos', label: 'Todos os tipos' },
          ]}
        />
      </Form.Item>

      <Form.Item name="ativo">
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 130 }}
          options={[
            { value: true, label: 'Ativos' },
            { value: false, label: 'Inativos' },
          ]}
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
        >
          Filtrar
        </Button>
      </Form.Item>
    </Form>
  )
}

export default ProductFilters
