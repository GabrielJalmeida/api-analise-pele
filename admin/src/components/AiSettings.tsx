import { useEffect, useState } from 'react'

import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  Select,
  Switch,
} from 'antd'

import {
  ErroApi,
  obterConfiguracaoIA,
  salvarConfiguracaoIA,
} from '../services/api'
import type {
  AtualizacaoConfiguracaoIA,
  ConfiguracaoIA,
  ProvedorIA,
} from '../types/produto'


const modelosPadrao: Record<ProvedorIA, string> = {
  gemini: 'gemini-3.5-flash-lite',
  openai: 'gpt-5.6-luna',
  anthropic: 'claude-haiku-4-5-20251001',
}


function AiSettings() {
  const [form] = Form.useForm<AtualizacaoConfiguracaoIA>()
  const [configuracao, setConfiguracao] =
    useState<ConfiguracaoIA | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState<string | null>(null)

  useEffect(() => {
    obterConfiguracaoIA()
      .then((dados) => {
        setConfiguracao(dados)
        form.setFieldsValue({
          provedor: dados.provedor,
          modelo: dados.modelo,
          api_key: '',
          pedidos_atualizam_estoque: dados.pedidos_atualizam_estoque,
        })
      })
      .catch((erroRecebido) => {
        setErro(
          erroRecebido instanceof ErroApi
            ? erroRecebido.message
            : 'Não foi possível consultar a configuração.',
        )
      })
      .finally(() => setCarregando(false))
  }, [form])

  async function salvar(valores: AtualizacaoConfiguracaoIA) {
    try {
      setSalvando(true)
      setErro(null)
      setSucesso(null)

      const dados = await salvarConfiguracaoIA({
        ...valores,
        api_key: valores.api_key?.trim() || undefined,
      })

      setConfiguracao(dados)
      form.setFieldValue('api_key', '')
      setSucesso('Configuração salva. As próximas operações de IA já usarão este provedor.')
    } catch (erroRecebido) {
      setErro(
        erroRecebido instanceof ErroApi
          ? erroRecebido.message
          : 'Não foi possível salvar a configuração.',
      )
    } finally {
      setSalvando(false)
    }
  }

  const arquivoLocal =
    configuracao?.armazenamento === 'arquivo_local'

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Inteligência artificial</h1>
          <p className="page-description">
            Escolha o provedor usado nas análises e na organização de catálogos.
          </p>
        </div>
      </div>

      <Alert
        type="info"
        showIcon
        title="A chave fica somente neste computador"
        description="O painel nunca exibe a chave salva e não a envia ao frontend público. Cada instalação usa a própria conta do provedor escolhido."
        className="orders-guidance"
      />

      {erro && <Alert type="error" showIcon title={erro} className="import-guidance" />}
      {sucesso && <Alert type="success" showIcon title={sucesso} className="import-guidance" />}

      <Card loading={carregando} className="settings-card">
        <Form
          form={form}
          layout="vertical"
          onFinish={salvar}
          disabled={carregando || salvando || !arquivoLocal}
        >
          <Form.Item
            label="Provedor"
            name="provedor"
            rules={[{ required: true, message: 'Selecione um provedor.' }]}
          >
            <Select
              options={[
                { value: 'gemini', label: 'Google Gemini' },
                { value: 'openai', label: 'OpenAI' },
                { value: 'anthropic', label: 'Anthropic Claude' },
              ]}
              onChange={(provedor: ProvedorIA) => {
                form.setFieldValue('modelo', modelosPadrao[provedor])
              }}
            />
          </Form.Item>

          <Form.Item
            label="Modelo"
            name="modelo"
            rules={[
              { required: true, message: 'Informe o modelo.' },
              { min: 2, max: 120 },
            ]}
            extra="Você pode substituir pelo modelo disponível na sua conta sem alterar o código."
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Nova chave de API"
            name="api_key"
            extra={
              configuracao?.api_key_configurada
                ? 'Já existe uma chave para o provedor atual. Deixe vazio para mantê-la.'
                : 'Nenhuma chave foi configurada para o provedor atual.'
            }
          >
            <Input.Password
              autoComplete="new-password"
              placeholder="Cole somente se quiser cadastrar ou trocar a chave"
            />
          </Form.Item>

          <Form.Item
            label="Baixar estoque ao registrar pedido demonstrativo"
            name="pedidos_atualizam_estoque"
            valuePropName="checked"
            extra="Desativado por padrão, pois o site não processa uma compra real."
          >
            <Switch />
          </Form.Item>

          {!arquivoLocal && !carregando && (
            <Alert
              type="warning"
              showIcon
              title="Configuração pelo painel disponível no aplicativo instalado"
              description="No desenvolvimento web, use o arquivo .env da API."
              className="import-guidance"
            />
          )}

          <Button type="primary" htmlType="submit" loading={salvando} disabled={!arquivoLocal}>
            Salvar configuração
          </Button>
        </Form>
      </Card>
    </div>
  )
}

export default AiSettings
