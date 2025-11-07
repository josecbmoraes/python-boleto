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


def render_boletos(lista_boletos: list[BoletoItau], saida_pdf: str) -> None:
    """
    - 1 parcela -> formato normal (retrato, 1 por página)
    - 2+ parcelas -> formato carnê (paisagem, 2 por página)
    """
    if not lista_boletos:
        raise ValueError("lista_boletos não pode ser vazia")
    is_carne = len(lista_boletos) >= 2
    boleto_pdf = BoletoPDF(saida_pdf, landscape=is_carne)

    if not is_carne:
        boleto_pdf.drawBoleto(lista_boletos[0])
        boleto_pdf.nextPage()
    else:
        for i in range(0, len(lista_boletos), 2):
            b1 = lista_boletos[i]
            b2 = lista_boletos[i + 1] if (i + 1) < len(lista_boletos) else None
            boleto_pdf.drawBoletoCarneDuplo(b1, b2)
            boleto_pdf.nextPage()

    boleto_pdf.save()


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
    render_boletos(parcelas, "boleto-openpix-itau-carne.pdf")
