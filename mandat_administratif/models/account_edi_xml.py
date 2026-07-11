# -*- coding: utf-8 -*-
"""Injection du n° d'engagement juridique dans les fichiers de facturation.

Chorus Pro lit le n° d'engagement juridique dans la « référence de commande »
(BT-13 de la norme EN 16931) :
- CII / Factur-X : ram:BuyerOrderReferencedDocument/ram:IssuerAssignedID
- UBL            : cac:OrderReference/cbc:ID

Pour les structures qui exigent l'engagement, l'absence de cette balise
entraîne le rejet du flux. On post-traite donc la sortie des générateurs
natifs d'Odoo — ce qui couvre à la fois les exports XML directs et le XML
embarqué dans les PDF Factur-X (générés par le même builder CII).
"""
import logging

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)

NS_RAM = ('urn:un:unece:uncefact:data:standard:'
          'ReusableAggregateBusinessInformationEntity:100')
NS_CAC = ('urn:oasis:names:specification:ubl:schema:xsd:'
          'CommonAggregateComponents-2')
NS_CBC = ('urn:oasis:names:specification:ubl:schema:xsd:'
          'CommonBasicComponents-2')


def _unpack(result):
    """Les builders renvoient (contenu, erreurs) ou le contenu seul selon
    les versions : normaliser."""
    if isinstance(result, (tuple, list)):
        return result[0], result[1] if len(result) > 1 else None, True
    return result, None, False


def _repack(content, errors, was_tuple):
    return (content, errors) if was_tuple else content


def _to_bytes(content):
    return content.encode('utf-8') if isinstance(content, str) else content


def _inject_cii(content, engagement):
    root = etree.fromstring(_to_bytes(content))
    agreement = root.find(f'.//{{{NS_RAM}}}ApplicableHeaderTradeAgreement')
    if agreement is None:
        return content
    bord = agreement.find(f'{{{NS_RAM}}}BuyerOrderReferencedDocument')
    if bord is None:
        bord = etree.SubElement(
            agreement, f'{{{NS_RAM}}}BuyerOrderReferencedDocument')
        # Respecter l'ordre du schéma CII : avant ContractReferencedDocument,
        # AdditionalReferencedDocument ou SpecifiedProcuringProject.
        for tag in ('ContractReferencedDocument',
                    'AdditionalReferencedDocument',
                    'SpecifiedProcuringProject'):
            anchor = agreement.find(f'{{{NS_RAM}}}{tag}')
            if anchor is not None:
                anchor.addprevious(bord)
                break
    issuer = bord.find(f'{{{NS_RAM}}}IssuerAssignedID')
    if issuer is None:
        issuer = etree.SubElement(bord, f'{{{NS_RAM}}}IssuerAssignedID')
        bord.insert(0, issuer)
    issuer.text = engagement
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8')


def _inject_ubl(content, engagement):
    root = etree.fromstring(_to_bytes(content))
    order_ref = root.find(f'{{{NS_CAC}}}OrderReference')
    if order_ref is None:
        order_ref = etree.SubElement(root, f'{{{NS_CAC}}}OrderReference')
        # Respecter l'ordre du schéma UBL : avant la première balise suivante
        # présente (AccountingSupplierParty est toujours là).
        for tag in ('BillingReference', 'DespatchDocumentReference',
                    'ReceiptDocumentReference', 'OriginatorDocumentReference',
                    'ContractDocumentReference', 'AdditionalDocumentReference',
                    'ProjectReference', 'AccountingSupplierParty'):
            anchor = root.find(f'{{{NS_CAC}}}{tag}')
            if anchor is not None:
                anchor.addprevious(order_ref)
                break
    node_id = order_ref.find(f'{{{NS_CBC}}}ID')
    if node_id is None:
        node_id = etree.SubElement(order_ref, f'{{{NS_CBC}}}ID')
        order_ref.insert(0, node_id)
    node_id.text = engagement
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8')


def _inject_engagement(result, invoice, flavor):
    """Injecter l'engagement juridique dans le XML si pertinent ; en cas
    d'imprévu, renvoyer le contenu d'origine sans jamais bloquer la
    facturation."""
    engagement = getattr(invoice, 'engagement_juridique', False)
    partner = invoice.partner_id.commercial_partner_id
    if not engagement or not partner.is_public_entity:
        return result
    content, errors, was_tuple = _unpack(result)
    if not content:
        return result
    try:
        injector = _inject_cii if flavor == 'cii' else _inject_ubl
        content = injector(content, engagement)
    except Exception:  # pylint: disable=broad-except
        _logger.warning(
            "Impossible d'injecter l'engagement juridique dans le %s de %s ; "
            "contenu d'origine conservé.", flavor.upper(),
            invoice.display_name, exc_info=True,
        )
        return result
    return _repack(content, errors, was_tuple)


class AccountEdiXmlCII(models.AbstractModel):
    _inherit = 'account.edi.xml.cii'

    def _export_invoice(self, invoice):
        result = super()._export_invoice(invoice)
        return _inject_engagement(result, invoice, 'cii')


class AccountEdiXmlUBL21(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_21'

    def _export_invoice(self, invoice):
        result = super()._export_invoice(invoice)
        return _inject_engagement(result, invoice, 'ubl')
