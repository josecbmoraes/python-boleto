#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal

from pyboleto.bank.itau import BoletoItau
from pyboleto.pdf import BoletoPDF

# Observações importantes:
# - Ajuste 'carteira', 'agencia_cedente' e 'conta_cedente' de acordo com o SEU convênio Itaú.
# - O cabeçalho do banco (logo/código 341) é do Itaú; Woovi/OpenPix entra apenas como "processado por".
# - Este exemplo pressupõe que pyboleto/pdf.py já foi patchado para:
#   (1) Desenhar QR Code PIX dentro do bloco de Instruções, sem sobrepor, com label "Pagar com PIX".
#   (2) Desenhar badge "Processado por Woovi (OpenPix)" no rodapé/área informativa do Recibo do Caixa.


def build_boleto_itau(
    *,
    valor_documento: Decimal | float | str,
    numero_documento: str,
    nosso_numero: str,
    data_vencimento: datetime.date,
    sacado_linhas: list[str],
    qrcode_pix_url: str | None = None,
    provider_name: str | None = "Woovi",
    provider_logo_url: str | None = None,
    provider_note: str | None = "Processado por Woovi (OpenPix)",
) -> BoletoItau:
    d = BoletoItau()

    # ======== CAMPOS DO CONVÊNIO ITAÚ (ajuste para o seu contrato) ========
    d.carteira = "109"
    d.agencia_cedente = "1234"
    d.conta_cedente = "56789"
    d.conta_cedente_dv = "1"

    # ======== DADOS DO BENEFICIÁRIO ========
    d.cedente = "Minha Empresa LTDA"
    d.cedente_documento = "12.345.678/0001-90"
    d.cedente_endereco = "Rua X, 123 - Centro - São Paulo/SP - CEP 00000-000"

    # ======== DATAS ========
    hoje = datetime.date.today()
    d.data_documento = hoje
    d.data_processamento = hoje
    d.data_vencimento = data_vencimento

    # ======== VALORES / IDENTIFICAÇÃO ========
    d.valor_documento = valor_documento
    d.nosso_numero = nosso_numero
    d.numero_documento = numero_documento

    # ======== INSTRUÇÕES / DEMONSTRATIVO ========
    d.instrucoes = [
        "- Após o vencimento, multa de 2% e juros de 0,033% a.d.",
        "- Em caso de dúvidas, contate nosso suporte.",
        "- Pague também via PIX escaneando o QR Code ao lado.",
    ]
    d.demonstrativo = [
        f"- Documento: {numero_documento}",
        f"- Valor: R$ {valor_documento}",
    ]

    # ======== SACADO ========
    d.sacado = sacado_linhas

    # ======== PIX (QR Code) ========
    d.qrcode_pix_url = qrcode_pix_url

    # ======== BADGE DO PROVEDOR ========
    d.provider_name = provider_name
    d.provider_logo_url = provider_logo_url
    d.provider_note = provider_note

    return d


def render_boletos(
    lista_boletos: list[BoletoItau],
    saida_pdf: str,
    *,
    carne_width_pct: float | None = None,
) -> None:
    """
    - 1 parcela -> formato normal (retrato, 1 por página)
    - 2 parcelas -> formato carnê (paisagem, 2 por página)
    - 3+ parcelas -> layout triplo (retrato, 3 módulos por página)
    """
    n = len(lista_boletos)
    if n == 0:
        return

    if n == 1:
        pdf = BoletoPDF(saida_pdf, landscape=False)
        pdf.drawBoleto(lista_boletos[0])
        pdf.nextPage()
        pdf.save()
        return

    if n == 2:
        pdf = BoletoPDF(
            saida_pdf,
            landscape=True,
            carne_width_pct=carne_width_pct,
        )
        pdf.drawBoletoCarneDuplo(lista_boletos[0], lista_boletos[1])
        pdf.nextPage()
        pdf.save()
        return

    pdf = BoletoPDF(saida_pdf, landscape=False)
    for i in range(0, n, 3):
        b1 = lista_boletos[i]
        b2 = lista_boletos[i + 1] if (i + 1) < n else None
        b3 = lista_boletos[i + 2] if (i + 2) < n else None
        pdf.drawBoletoTriploPorPagina(b1, b2, b3)
        pdf.nextPage()
    pdf.save()


if __name__ == "__main__":
    qr_url = "https://api.woovi-sandbox.com/openpix/charge/brcode/image/4830ef79-d099-404e-90b3-9ccb28d57adf.png"
    provider_logo = "https://cdn.exemplo.com/brand/woovi-logo.png"

    p1 = build_boleto_itau(
        valor_documento=Decimal("215.80"),
        numero_documento="ITAU-NF001",
        nosso_numero="10000001",
        data_vencimento=datetime.date.today() + datetime.timedelta(days=7),
        sacado_linhas=[
            "Cliente Teste",
            "Rua Sem Nome, 999 - Cidade/UF",
            "CEP 00000-000",
        ],
        qrcode_pix_url=qr_url,
        provider_logo_url=provider_logo,
    )
    render_boletos([p1], "boleto-openpix-itau-normal.pdf")

    parcelas = []
    base_venc = datetime.date.today() + datetime.timedelta(days=7)
    for idx in range(3):
        parcelas.append(
            build_boleto_itau(
                valor_documento=Decimal("215.80"),
                numero_documento=f"ITAU-PARC-{idx+1:02}",
                nosso_numero=f"{1010000 + idx:08d}",
                data_vencimento=base_venc + datetime.timedelta(days=30 * idx),
                sacado_linhas=[
                    "Cliente Teste",
                    "Rua Sem Nome, 999 - Cidade/UF",
                    "CEP 00000-000",
                ],
                qrcode_pix_url=qr_url,
                provider_logo_url=provider_logo,
            )
        )
    render_boletos(
        parcelas,
        "boleto-openpix-itau-carne.pdf",
        carne_width_pct=0.6,
    )
