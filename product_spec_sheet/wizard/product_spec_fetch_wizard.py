# -*- coding: utf-8 -*-
import json
import re
import time
from odoo import _, api, fields, models
from odoo.exceptions import UserError

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

_WEIGHT_KG = [r'(?:poids|weight)\s*[:\-]?\s*([\d,\.]+)\s*kg', r'\b([\d,\.]+)\s*kg\b']
_WEIGHT_G  = [r'(?:poids|weight)\s*[:\-]?\s*([\d]+)\s*g\b', r'\b(\d{2,4})\s*g(?:ramme)?s?\b']
_DIMS_MM   = [r'([\d,\.]+)\s*[×xX]\s*([\d,\.]+)\s*[×xX]\s*([\d,\.]+)\s*mm']
_DIMS_CM   = [r'([\d,\.]+)\s*[×xX]\s*([\d,\.]+)\s*[×xX]\s*([\d,\.]+)\s*cm']

def _flt(s):
    try:
        return float(str(s).replace(",", "."))
    except Exception:
        return None

def _extract_weight(text):
    for pat in _WEIGHT_KG:
        m = re.search(pat, text, re.I)
        if m:
            return _flt(m.group(1))
    for pat in _WEIGHT_G:
        m = re.search(pat, text, re.I)
        if m:
            v = _flt(m.group(1))
            if v and 10 < v < 50000:
                return v / 1000
    return None

def _extract_dims(text):
    for pat in _DIMS_MM:
        m = re.search(pat, text, re.I)
        if m:
            return _flt(m.group(1)), _flt(m.group(2)), _flt(m.group(3))
    for pat in _DIMS_CM:
        m = re.search(pat, text, re.I)
        if m:
            return _flt(m.group(1))*10, _flt(m.group(2))*10, _flt(m.group(3))*10
    return None, None, None

def _extract_field(text, *keywords):
    for kw in keywords:
        m = re.search(rf"{re.escape(kw)}\s*[:\-]?\s*([^\n\r\|;]{{3,100}})", text, re.I)
        if m:
            v = m.group(1).strip().rstrip(".,;")
            if len(v) > 2:
                return v
    return ""


class ProductSpecFetchWizard(models.TransientModel):
    _name        = "product.spec.fetch.wizard"
    _description = "Récupération des caractéristiques sur internet"

    product_tmpl_id     = fields.Many2one("product.template", required=True,
                              default=lambda self: self.env.context.get("active_id"),
                              ondelete="cascade")
    product_search_name = fields.Char(string="Nom recherché")
    state               = fields.Selection(
        [("draft","Recherche"),("done","Résultats"),("applied","Appliqué")],
        default="draft")
    source_url    = fields.Char(readonly=True)
    confidence    = fields.Selection(
        [("high","Élevée"),("medium","Moyenne"),("low","Faible")], readonly=True)
    weight_kg     = fields.Float(digits=(10,3))
    length_mm     = fields.Float()
    width_mm      = fields.Float()
    height_mm     = fields.Float()
    volume_cm3    = fields.Float(compute="_compute_volume", readonly=True)
    spec_os            = fields.Char(string="Système d'exploitation", readonly=True)
    spec_cpu           = fields.Char(string="Processeur",   readonly=True)
    spec_memory        = fields.Char(string="Mémoire",      readonly=True)
    spec_screen        = fields.Char(string="Écran",        readonly=True)
    spec_connectivity  = fields.Char(string="Réseaux",      readonly=True)
    spec_card_reader   = fields.Char(string="Lecteur carte",readonly=True)
    spec_ports         = fields.Char(string="Ports",        readonly=True)
    spec_battery       = fields.Char(string="Batterie",     readonly=True)
    spec_certification = fields.Char(string="Certification",readonly=True)
    shipping_html      = fields.Html(readonly=True, sanitize=False)
    apply_weight       = fields.Boolean("Mettre à jour weight / volume", default=True)
    apply_spec_lines   = fields.Boolean("Créer/MàJ les lignes de caractéristiques", default=True)
    update_existing    = fields.Boolean("Écraser les valeurs existantes", default=True)

    @api.depends("length_mm","width_mm","height_mm")
    def _compute_volume(self):
        for rec in self:
            if rec.length_mm and rec.width_mm and rec.height_mm:
                rec.volume_cm3 = (rec.length_mm/10)*(rec.width_mm/10)*(rec.height_mm/10)
            else:
                rec.volume_cm3 = 0.0

    @api.onchange("product_tmpl_id")
    def _onchange_product(self):
        if self.product_tmpl_id and not self.product_search_name:
            self.product_search_name = self.product_tmpl_id.name

    # ── Calcul frais de port depuis les modèles configurables ───────
    def _calc_shipping(self, weight_kg, l_mm, w_mm, h_mm):
        """
        Calcule les frais de port pour chaque transporteur actif.
        Priorité : tarif live (API) si activé, sinon grille statique.
        """
        results = []
        weight_g = weight_kg * 1000
        carriers = self.env['product.spec.carrier'].search([('active','=',True)])
        for carrier in carriers:
            vol_g = 0.0
            is_vol = False
            if l_mm and w_mm and h_mm:
                vol_g = (l_mm/10)*(w_mm/10)*(h_mm/10) / (carrier.volumetric_divisor or 5000) * 1000
                is_vol = vol_g > weight_g
            billed_g  = max(weight_g, vol_g)
            billed_kg = billed_g / 1000
            if carrier.max_weight_kg and billed_kg > carrier.max_weight_kg:
                continue

            for zone in carrier.zone_ids.sorted('sequence'):
                # 1. Essai tarif live via API
                source = "static"
                if carrier.api_use_live and carrier.api_provider not in ("none", False, ""):
                    live_price, live_src = carrier.get_live_rate(billed_kg, zone.name)
                    if live_price is not None:
                        results.append({
                            "carrier":   carrier.name,
                            "zone":      zone.name,
                            "billed_kg": round(billed_kg, 3),
                            "price":     live_price,
                            "is_vol":    is_vol,
                            "source":    "live",
                        })
                        continue  # pas besoin de la grille statique

                # 2. Grille statique
                price = zone.get_price(billed_g)
                if price is not None:
                    results.append({
                        "carrier":   carrier.name,
                        "zone":      zone.name,
                        "billed_kg": round(billed_kg, 3),
                        "price":     price,
                        "is_vol":    is_vol,
                        "source":    "static",
                    })
        return results

    def _build_shipping_html(self):
        if not self.weight_kg:
            self.shipping_html = "<p class='text-muted'>Poids non trouvé — frais de port non calculables.</p>"
            return
        quotes = self._calc_shipping(self.weight_kg, self.length_mm or 0,
                                     self.width_mm or 0, self.height_mm or 0)
        if not quotes:
            self.shipping_html = "<p class='text-muted'>Aucun transporteur actif configuré.</p>"
            return
        rows = ""
        prev = ""
        for q in quotes:
            span = sum(1 for x in quotes if x["carrier"] == q["carrier"])
            cell = (f'<td rowspan="{span}" style="vertical-align:middle;font-weight:500;'
                    f'border-right:1px solid #dee2e6;">{q["carrier"]}</td>'
                    if q["carrier"] != prev else "")
            prev = q["carrier"]
            vol    = ' <span class="badge bg-warning text-dark">vol.</span>' if q["is_vol"] else ""
            live   = ' <span class="badge bg-success text-white">live</span>' if q.get("source")=="live" else ''
            rows += (f"<tr>{cell}<td>{q['zone']}</td>"
                     f"<td>{q['billed_kg']:.3f} kg{vol}</td>"
                     f"<td><strong>{q['price']:.2f} €</strong>{live}</td></tr>")

        vol_note = ""
        if self.length_mm and self.width_mm and self.height_mm:
            carriers = self.env['product.spec.carrier'].search([('active','=',True)], limit=1)
            div = carriers.volumetric_divisor or 5000 if carriers else 5000
            vol_kg = (self.length_mm/10)*(self.width_mm/10)*(self.height_mm/10)/div
            if vol_kg > self.weight_kg:
                vol_note = (f'<p class="text-warning mt-2">⚠ Poids volumétrique '
                            f'({vol_kg:.3f} kg) supérieur au poids réel ({self.weight_kg:.3f} kg) : '
                            f'c\'est le poids volumétrique qui sera facturé.</p>')

        self.shipping_html = f"""
<table class="table table-sm table-bordered mt-2">
  <thead class="table-light">
    <tr><th>Transporteur</th><th>Zone</th><th>Poids facturé</th><th>Tarif HT</th></tr>
  </thead>
  <tbody>{rows}</tbody>
</table>{vol_note}
<p class="text-muted small mt-1">
  Tarifs issus de la configuration Odoo (Ventes → Configuration → Transporteurs).
  À valider avec vos contrats.
</p>"""

    # ── Fetch internet ───────────────────────────────────────────────
    def action_fetch(self):
        self.ensure_one()
        name = (self.product_search_name or "").strip()
        if not name:
            raise UserError(_("Renseignez un nom de produit à rechercher."))
        api_key = self.env["ir.config_parameter"].sudo().get_param(
            "product_spec_sheet.anthropic_api_key", default="")
        result = self._do_fetch(name, api_key)
        self._fill_from_result(result)
        self._build_shipping_html()
        return {"type":"ir.actions.act_window","res_model":self._name,"res_id":self.id,
                "view_mode":"form","target":"new","context":self.env.context}

    def _do_fetch(self, name, api_key=""):
        if api_key:
            ai = self._fetch_via_anthropic(name, api_key)
            if ai:
                return ai
        return self._fetch_via_scraping(name)

    def _fetch_via_anthropic(self, name, api_key):
        try:
            import anthropic as _anthropic
        except ImportError:
            return None
        prompt = (f'Recherche les caractéristiques complètes de "{name}". '
                  'Réponds UNIQUEMENT en JSON sans markdown :\n'
                  '{"weight_kg":null,"length_mm":null,"width_mm":null,"height_mm":null,'
                  '"os":"","cpu":"","memory":"","screen":"","connectivity":"",'
                  '"card_reader":"","ports":"","battery":"","certification":"",'
                  '"source_url":"","confidence":"low"}')
        try:
            client   = _anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-5", max_tokens=1000,
                tools=[{"type":"web_search_20250305","name":"web_search"}],
                messages=[{"role":"user","content":prompt}])
            text = "".join(b.text for b in response.content if b.type == "text")
            m    = re.search(r"\{[\s\S]*\}", text)
            return json.loads(m.group(0)) if m else None
        except Exception:
            return None

    def _fetch_via_scraping(self, name):
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise UserError(_("Modules Python manquants :\npip install requests beautifulsoup4 lxml"))
        best, score = {}, -1
        urls = self._get_search_urls(name, requests, BeautifulSoup)
        for url in urls[:10]:
            try:
                resp = requests.get(url, headers=HTTP_HEADERS, timeout=8)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["script","style","nav","footer","header","aside"]):
                    tag.decompose()
                text = re.sub(r"\s{2,}"," ",soup.get_text(" ",strip=True))[:10000]
                c = {"weight_kg":_extract_weight(text),
                     "length_mm":None,"width_mm":None,"height_mm":None,
                     "os":_extract_field(text,"système d'exploitation","OS"),
                     "cpu":_extract_field(text,"processeur","processor","CPU"),
                     "memory":_extract_field(text,"mémoire","memory","RAM"),
                     "screen":_extract_field(text,"écran","display"),
                     "connectivity":_extract_field(text,"connectivité","réseau"),
                     "card_reader":_extract_field(text,"lecteur","NFC","sans contact"),
                     "ports":_extract_field(text,"port","USB","ethernet"),
                     "battery":_extract_field(text,"batterie","battery","mAh"),
                     "certification":_extract_field(text,"certification","PCI","EMV"),
                     "source_url":url,"confidence":"low"}
                l,w,h = _extract_dims(text)
                c.update({"length_mm":l,"width_mm":w,"height_mm":h})
                s = sum([c["weight_kg"] is not None, c["length_mm"] is not None,
                         bool(c["os"]), bool(c["cpu"]), bool(c["screen"])])
                if s > score:
                    score, best = s, c
                if best.get("weight_kg") and best.get("length_mm"):
                    break
                time.sleep(0.4)
            except Exception:
                continue
        if best:
            hw, hd = bool(best.get("weight_kg")), bool(best.get("length_mm"))
            best["confidence"] = "high" if hw and hd else "medium" if hw or hd else "low"
        return best

    def _get_search_urls(self, name, requests, BeautifulSoup):
        urls = []
        try:
            resp = requests.post("https://html.duckduckgo.com/html/",
                data={"q":f"{name} fiche technique spécifications poids dimensions"},
                headers={**HTTP_HEADERS,"Content-Type":"application/x-www-form-urlencoded"},
                timeout=10)
            soup = BeautifulSoup(resp.text,"lxml")
            for a in soup.select("a.result__url"):
                href = a.get("href","")
                if href.startswith("http") and "duckduckgo" not in href:
                    urls.append(href)
                    if len(urls) >= 8:
                        break
        except Exception:
            pass
        return urls

    def _fill_from_result(self, r):
        if not r:
            self.state, self.confidence = "done", "low"
            return
        self.weight_kg=r.get("weight_kg") or 0.0; self.length_mm=r.get("length_mm") or 0.0
        self.width_mm=r.get("width_mm") or 0.0;   self.height_mm=r.get("height_mm") or 0.0
        self.spec_os=r.get("os","");             self.spec_cpu=r.get("cpu","")
        self.spec_memory=r.get("memory","");     self.spec_screen=r.get("screen","")
        self.spec_connectivity=r.get("connectivity",""); self.spec_card_reader=r.get("card_reader","")
        self.spec_ports=r.get("ports","");       self.spec_battery=r.get("battery","")
        self.spec_certification=r.get("certification","")
        self.source_url=r.get("source_url","");  self.confidence=r.get("confidence","low")
        self.state="done"

    # ── Application ────────────────────────────────────────────────
    def action_apply(self):
        self.ensure_one()
        product = self.product_tmpl_id
        if not product:
            raise UserError(_("Aucun produit sélectionné."))
        created = updated = 0
        if self.apply_weight and self.weight_kg:
            product.weight = self.weight_kg
        if self.apply_weight and self.volume_cm3:
            product.volume = round(self.volume_cm3/1_000_000, 8)
        if self.apply_spec_lines:
            SpecLine = self.env["product.template.spec.line"]
            Category = self.env["product.spec.category"]
            Attribute = self.env["product.spec.attribute"]
            def _gor_create(cat, attr):
                c = Category.search([("name","=",cat)],limit=1)
                if not c: c = Category.create({"name":cat,"sequence":99})
                a = Attribute.search([("name","=",attr),("category_id","=",c.id)],limit=1)
                if not a: a = Attribute.create({"name":attr,"category_id":c.id})
                return a
            def _upsert(cat, attr, val):
                nonlocal created, updated
                if not val: return
                a = _gor_create(cat, attr)
                ex = SpecLine.search([("product_tmpl_id","=",product.id),("attribute_id","=",a.id)],limit=1)
                if ex:
                    if self.update_existing and ex.value != val: ex.value = val; updated += 1
                else:
                    SpecLine.create({"product_tmpl_id":product.id,"attribute_id":a.id,"value":val}); created += 1
            _upsert("Système","Système d'exploitation",self.spec_os)
            _upsert("Système","Processeur",self.spec_cpu)
            _upsert("Système","Mémoire",self.spec_memory)
            _upsert("Écran","Taille",self.spec_screen)
            _upsert("Connectivité","Réseaux",self.spec_connectivity)
            _upsert("Connectivité","Lecteur de carte",self.spec_card_reader)
            _upsert("Connectivité","Ports",self.spec_ports)
            _upsert("Alimentation","Batterie",self.spec_battery)
            _upsert("Sécurité","Certification",self.spec_certification)
            if self.weight_kg:
                _upsert("Dimensions et poids","Poids",f"{self.weight_kg:.3f} kg")
            if self.length_mm and self.width_mm and self.height_mm:
                _upsert("Dimensions et poids","Encombrement",
                        f"{self.length_mm:.0f} × {self.width_mm:.0f} × {self.height_mm:.0f} mm")
        self.state = "applied"
        return {"type":"ir.actions.client","tag":"display_notification",
                "params":{"title":_("Caractéristiques appliquées"),
                          "message": _("%(c)s ligne(s) créée(s), %(u)s mise(s) à jour sur %(p)s.",
                                       c=created, u=updated, p=product.name),
                          "type":"success","sticky":False}}
