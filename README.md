# python-boleto

Biblioteca Python mantida pela Trustcode para gerar boletos de cobranca bancaria (PDF e HTML) compativeis com as especificacoes da FEBRABAN. O pacote `python3-boleto` expoe classes de dados para cada banco brasileiro suportado, renderizadores para diferentes formatos e utilitarios de teste que ajudam a garantir a fidelidade visual dos titulos.

## Principais recursos

- Implementacoes prontas para os principais bancos brasileiros via `pyboleto.bank`, cada uma cuidando de digitos verificadores, campos livres e layouts especificos.
- Renderizacao em PDF (`pyboleto.pdf.BoletoPDF`) e HTML (`pyboleto.html.BoletoHTML`), ambos com suporte a multiplos boletos por arquivo.
- Scripts de exemplo em `bin/` que demonstram a geracao de boletos e produzem arquivos reais para inspecao manual.
- Suite de testes cobrindo codigos de barras, linhas digitaveis e regressoes visuais (PDF/HTML) com uso opcional do `pdftohtml`.

## Bancos implementados

| Banco                 | Carteiras / Convenios      | Status dos testes |
|-----------------------|----------------------------|-------------------|
| Banco do Brasil       | 18                         | Implementado e testado |
| Banrisul              | -                          | Implementado e testado |
| Bradesco              | 06, 03                     | Implementado e testado |
| Caixa Economica       | SR / SIGCB                 | Implementado (testes parciais) |
| HSBC                  | CNR, CSB                   | Implementado (testes pendentes) |
| Itau                  | 157                        | Implementado e testado |
| Itau                  | 175, 174, 178, 104, 109    | Implementado (testes pendentes) |
| Santander             | 102                        | Implementado e testado |
| Santander             | 101, 201                   | Implementado (testes pendentes) |
| Sicoob                | 1                          | Implementado e testado |
| Sicredi               | 1                          | Implementado e testado |
| Cecred                | 1                          | Implementado (sem testes automatizados) |
| Banco Real            | 57                         | Implementado (legado) |

## Requisitos

- Python 3.6 ou superior.
- `reportlab` para geracao de PDFs (instalado automaticamente via `pip`).
- `pdftohtml` (opcional) para os testes de regressao visual.

## Instalacao

Via PyPI:

```bash
pip install python3-boleto
```

Ambiente de desenvolvimento local:

```bash
git clone https://github.com/Trust-Code/python-boleto.git
cd python-boleto
python3 -m venv .venv
source .venv/bin/activate  # .\.venv\Scripts\activate no Windows
pip install -r requirements.txt
pip install -e .
```

## Uso rapido

```python
from datetime import date
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.pdf import BoletoPDF
from pyboleto.html import BoletoHTML

boleto = BoletoBradesco()
boleto.carteira = '06'
boleto.agencia_cedente = '0278-0'
boleto.conta_cedente = '0039232-4'
boleto.cedente = 'Empresa ACME LTDA'
boleto.cedente_documento = '102.323.777-01'
boleto.cedente_endereco = 'Rua Acme, 123 - Centro - Sao Paulo/SP'
boleto.data_vencimento = date(2024, 12, 1)
boleto.data_documento = date.today()
boleto.data_processamento = date.today()
boleto.valor_documento = 2158.41
boleto.nosso_numero = '1112011668'
boleto.numero_documento = '1112011668'
boleto.sacado = [
    'Cliente Teste',
    'Rua Desconhecida, 00 - Cidade/UF',
    'CEP 00000-000',
]

pdf = BoletoPDF('boleto.pdf')
pdf.drawBoleto(boleto)
pdf.save()

html = BoletoHTML('boleto.html')
html.drawBoleto(boleto)
html.save()
```

- Para gerar varios boletos no mesmo arquivo, chame `drawBoleto` em sequencia e finalize com `nextPage()` quando precisar forcar uma nova pagina.
- Alguns bancos exigem parametros extras como convenios, contas com DV separado ou campos customizados; consulte a classe correspondente em `pyboleto/bank/`.

## Scripts uteis

- `bin/pdf_pyboleto_sample.py`: cria PDFs de exemplo para todos os bancos suportados (normal e carne quando aplicavel).
- `bin/html_pyboleto_sample.py`: gera a versao HTML equivalente.
- `bin/pdf_pyboleto_in_memory_sample.py`: demonstra o uso de buffers em memoria, util para integrar com webapps.

Execute-os apos instalar as dependencias para inspecionar rapidamente a saida gerada.

## Executando testes

```bash
pytest
```

Os testes convertem os PDFs gerados para XML usando `pdftohtml` e comparam com fixtures em `tests/html` e `tests/xml`. Instale o utilitario antes de rodar a suite completa. Se precisar atualizar um fixture, remova o arquivo esperado correspondente e rode o teste novamente para gerar uma nova versao.

## Estrutura do repositorio

- `pyboleto/data.py`: classe base `BoletoData` e utilitarios para digitos verificadores.
- `pyboleto/bank/`: implementacoes especificas por banco.
- `pyboleto/pdf.py` e `pyboleto/html.py`: renderizadores de saida.
- `pyboleto/templates/` e `pyboleto/media/`: assets usados na renderizacao HTML.
- `tests/`: validacoes unitarias e visuais para cada banco.
- `docs/`: rascunhos de documentacao Sphinx.

## Contribuindo

1. Crie um branch e acrescente testes unitarios/visuais sempre que possivel.
2. Garanta que `pytest` passe e que os PDFs/HTMLs batam com os fixtures.
3. Abra um pull request descrevendo o banco ou a funcionalidade adicionada.

## Licenca

Distribuido sob a licenca BSD de 3 clausulas. Veja `LICENSE` para o texto completo.
