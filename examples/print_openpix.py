#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Exemplo de impressão de boletos com QR Code PIX via OpenPix/Woovi."""
import datetime
import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.pdf import BoletoPDF


def build_boleto_bradesco(qr_url):
    """Monta um boleto Bradesco preenchido com dados fictícios."""
    d = BoletoBradesco()
    d.carteira = '06'
    d.cedente = 'Empresa ACME LTDA'
    d.cedente_documento = "12.345.678/0001-90"
    d.cedente_endereco = (
        "Rua Acme, 123 - Centro - São Paulo/SP - CEP: 12345-678"
    )
    d.agencia_cedente = '0278-0'
    d.conta_cedente = '43905'
    d.data_vencimento = datetime.date(2025, 10, 25)
    d.data_documento = datetime.date(2025, 2, 12)
    d.data_processamento = datetime.date(2025, 2, 12)
    d.instrucoes = [
        "- Pague também via PIX escaneando o QR Code ao lado.",
        "- Após o vencimento, cobrar multa de 2% e juros de 0,033% a.d.",
        "- Não receber após 10 dias do vencimento.",
    ]
    d.demonstrativo = ["- Serviço Teste R$ 5,00", "- Total R$ 5,00"]
    d.valor_documento = 2158.41
    d.nosso_numero = "1112011668"
    d.numero_documento = "1112011668"
    d.sacado = [
        "Cliente Teste",
        "Rua Desconhecida, 00 - Cidade/UF - CEP 00000-000",
        ""
    ]
    d.qrcode_pix_url = qr_url
    return d


def render_boletos(lista_boletos, saida_pdf):
    """Renderiza boletos alternando entre formato normal e carnê."""
    if not lista_boletos:
        raise ValueError('lista_boletos não pode ser vazia')
    is_carne = len(lista_boletos) >= 2
    boleto_pdf = BoletoPDF(saida_pdf, landscape=is_carne)

    if not is_carne:
        boleto_pdf.drawBoleto(lista_boletos[0])
        boleto_pdf.nextPage()
    else:
        for i in range(0, len(lista_boletos), 2):
            boleto_1 = lista_boletos[i]
            boleto_2 = lista_boletos[i + 1] if i + 1 < len(lista_boletos) else None
            boleto_pdf.drawBoletoCarneDuplo(boleto_1, boleto_2)
            boleto_pdf.nextPage()

    boleto_pdf.save()


if __name__ == "__main__":
    # URL de teste fornecida pela Woovi/OpenPix (sandbox).
    qr = "https://api.woovi-sandbox.com/openpix/charge/brcode/image/4830ef79-d099-404e-90b3-9ccb28d57adf.png"
    render_boletos([build_boleto_bradesco(qr)], "boleto-openpix-normal.pdf")
    render_boletos([build_boleto_bradesco(qr) for _ in range(3)],
                   "boleto-openpix-carne.pdf")
