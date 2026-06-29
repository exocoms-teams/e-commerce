# -*- coding: utf-8 -*-
"""
Contrôleur Website public — Sinistre Services
Adapté de monetique_theme/controllers/main.py

Routes :
  /                           → Page d'accueil
  /nos-services               → Présentation des services
  /urgence                    → Page urgence 24/7
  /demande-intervention       → Formulaire demande (particulier / entreprise)
  /demande-intervention/send  → Traitement POST formulaire
  /contact                    → Formulaire contact
  /contact/send               → Traitement POST contact
  /suivi/<token>              → Suivi dossier public par token UUID
  /rappel                     → POST modal rappel
"""
import base64
import datetime
import logging
import re

from odoo import http, _
from odoo.http import request

from ..models.departements_fr import DEPARTEMENTS_FR

_logger = logging.getLogger(__name__)

_MAX_UPLOAD_BYTES = 5 * 1024 * 1024
_ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}


class SinistreWebsite(http.Controller):

    # ─── ACCUEIL ────────────────────────────────────────────────────
    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        return request.render('sinistre_services.ss_homepage', {
            'year': datetime.datetime.now().year,
        })

    # ─── NOS SERVICES ───────────────────────────────────────────────
    @http.route('/nos-services', type='http', auth='public', website=True)
    def nos_services(self, **kwargs):
        return request.render('sinistre_services.page_nos_services', {
            'year': datetime.datetime.now().year,
        })

    # ─── ASSURANCES (particuliers) ──────────────────────────────────
    @http.route('/assurances', type='http', auth='public', website=True)
    def assurances(self, **kwargs):
        return request.render('sinistre_services.page_assurances', {
            'year': datetime.datetime.now().year,
        })

    # ─── URGENCE 24/7 ───────────────────────────────────────────────
    @http.route('/urgence', type='http', auth='public', website=True)
    def urgence(self, **kwargs):
        return request.render('sinistre_services.ss_page_urgence', {
            'year': datetime.datetime.now().year,
        })

    # ─── FORMULAIRE DE DEMANDE D'INTERVENTION ───────────────────────
    @http.route('/demande-intervention', type='http', auth='public', website=True)
    def demande_intervention(self, **kwargs):
        """Formulaire de prise de contact / demande directe."""
        return request.render('sinistre_services.page_demande', {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
            'reference': None,
            'token': None,
            'type_pre': kwargs.get('type', ''),
            'urgence_pre': kwargs.get('urgence', ''),
            'form_data': {'source': kwargs.get('source', 'particulier')},
        })

    def _demande_render(self, **ctx):
        defaults = {
            'year': datetime.datetime.now().year,
            'type_pre': '',
            'urgence_pre': '',
            'form_data': {},
            'reference': None,
            'token': None,
            'error': False,
            'success': False,
        }
        defaults.update(ctx)
        return request.render('sinistre_services.page_demande', defaults)

    def _demande_validate(self, post, source):
        """Validation selon le profil demandeur."""
        common = ['telephone', 'type_intervention', 'adresse', 'code_postal', 'ville', 'description']
        if not all(post.get(f, '').strip() for f in common):
            return False
        if source == 'entreprise':
            return bool(
                post.get('entreprise_nom', '').strip()
                and post.get('nom', '').strip()
                and post.get('email', '').strip()
            )
        if source == 'assurance':
            return bool(
                post.get('assurance_nom', '').strip()
                and post.get('ref_assurance', '').strip()
                and post.get('nom', '').strip()
                and post.get('email', '').strip()
            )
        return bool(post.get('nom', '').strip() and post.get('email', '').strip())

    @http.route('/demande-intervention/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def demande_send(self, **post):
        """Traitement du formulaire de demande d'intervention."""
        source = post.get('source', 'particulier')
        if source not in ('particulier', 'entreprise', 'assurance'):
            source = 'particulier'

        if not self._demande_validate(post, source):
            return self._demande_render(
                error=True, success=False, form_data=post,
            )

        env = request.env(su=True)
        email = post.get('email', '').strip()
        adresse_full = ', '.join(filter(None, [
            post.get('adresse', '').strip(),
            post.get('code_postal', '').strip(),
            post.get('ville', '').strip(),
        ]))

        if source == 'assurance':
            assure_name = ' '.join(filter(None, [
                post.get('prenom', '').strip(),
                post.get('nom', '').strip(),
            ])) or 'Assuré'
            tel = post.get('telephone', '').strip()
            partner = env['res.partner'].search([
                ('name', '=', assure_name),
                ('phone', '=', tel),
            ], limit=1)
            if not partner:
                partner = env['res.partner'].create({
                    'name': assure_name,
                    'phone': tel,
                    'email': email,
                })
        else:
            partner = env['res.partner'].search([('email', '=', email)], limit=1)
            if not partner:
                is_company = (source == 'entreprise')
                if is_company and post.get('entreprise_nom', '').strip():
                    full_name = post.get('entreprise_nom', '').strip()
                else:
                    name_parts = [post.get('prenom', '').strip(), post.get('nom', '').strip()]
                    full_name = ' '.join(p for p in name_parts if p) or post.get('nom', 'Client').strip()
                partner_vals = {
                    'name': full_name,
                    'email': email,
                    'phone': post.get('telephone', '').strip(),
                    'is_company': is_company,
                }
                if post.get('siret', '').strip():
                    partner_vals['vat'] = post.get('siret', '').strip()
                partner = env['res.partner'].create(partner_vals)

        mission_vals = {
            'source': source,
            'client_id': partner.id,
            'type_intervention': post.get('type_intervention', 'autre'),
            'urgence': post.get('urgence', 'normale'),
            'description_sinistre': post.get('description', ''),
            'adresse_intervention': adresse_full,
            'contact_sur_place': f"{post.get('prenom', '')} {post.get('nom', '')}".strip(),
            'tel_sur_place': post.get('telephone', ''),
            'commentaire_interne': post.get('commentaire', ''),
        }

        if source == 'assurance':
            mission_vals['ref_assurance'] = post.get('ref_assurance', '').strip()
            mission_vals['contrat_assurance'] = post.get('contrat_assurance', '').strip()
            assurance_nom = post.get('assurance_nom', '').strip()
            if assurance_nom:
                assurance = env['sinistre.assurance'].search(
                    [('name', 'ilike', assurance_nom)], limit=1,
                )
                if assurance:
                    mission_vals['assurance_id'] = assurance.id
                extra_lines = [f"Compagnie: {assurance_nom}", f"Gestionnaire: {email}"]
                mission_vals['commentaire_interne'] = '\n'.join(filter(None, [
                    post.get('commentaire', '').strip(), *extra_lines,
                ]))

        try:
            mission = env['sinistre.mission'].create(mission_vals)
            _logger.info("[WEBSITE] Nouvelle demande créée : %s (%s)", mission.reference, source)
        except Exception as e:
            _logger.error("[WEBSITE] Erreur création mission web: %s", e)
            return self._demande_render(error=True, success=False, form_data=post)

        try:
            mail_vals = {
                'subject': f'[Sinistre Services] Nouvelle demande {source} — {mission.reference}',
                'body_html': f"""
                    <p><strong>Référence :</strong> {mission.reference}</p>
                    <p><strong>Source :</strong> {source}</p>
                    <p><strong>Type :</strong> {post.get('type_intervention', '')}</p>
                    <p><strong>Urgence :</strong> {post.get('urgence', 'normale')}</p>
                    <p><strong>Client :</strong> {partner.name} — {email} — {post.get('telephone', '')}</p>
                    <p><strong>Adresse :</strong> {adresse_full}</p>
                    <p><strong>Description :</strong><br/>{post.get('description', '')}</p>
                """,
                'email_from': email,
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            if source == 'assurance':
                mail_vals['body_html'] += f"""
                    <p><strong>Assurance :</strong> {post.get('assurance_nom', '')}</p>
                    <p><strong>Réf. sinistre :</strong> {post.get('ref_assurance', '')}</p>
                """
            env['mail.mail'].create(mail_vals).send()
        except Exception as e:
            _logger.warning("Email notification failed: %s", e)

        return self._demande_render(
            error=False,
            success=True,
            reference=mission.reference,
            token=mission.token_api,
            form_data={},
        )

    # ─── CONTACT ────────────────────────────────────────────────────
    def _contact_render(self, **ctx):
        defaults = {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
            'form_data': {},
        }
        defaults.update(ctx)
        return request.render('sinistre_services.page_contact', defaults)

    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kwargs):
        return self._contact_render()

    @http.route('/contact/send', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def contact_send(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip()
        message = post.get('message', '').strip()

        if not (name and email and message):
            return self._contact_render(error=True, form_data=post)

        try:
            mail_vals = {
                'subject': f"[Contact] {post.get('sujet', 'Nouveau message')}",
                'body_html': f"""
                    <p><strong>Nom :</strong> {name}</p>
                    <p><strong>Email :</strong> {email}</p>
                    <p><strong>Téléphone :</strong> {post.get('phone', 'Non renseigné')}</p>
                    <p><strong>Objet :</strong> {post.get('sujet', 'Non renseigné')}</p>
                    <p><strong>Message :</strong><br/>{message}</p>
                """,
                'email_from': email,
                'email_to': request.website.email or 'contact@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning("Contact send failed: %s", e)

        return self._contact_render(success=True)

    # ─── SUIVI DOSSIER (token public) ───────────────────────────────
    @http.route('/suivi/<string:token>', type='http', auth='public', website=True)
    def suivi_dossier(self, token, **kwargs):
        """Suivi public d'une mission par token UUID — sans authentification."""
        mission = request.env['sinistre.mission'].sudo().search([
            ('token_api', '=', token),
        ], limit=1)

        if not mission:
            return request.render('sinistre_services.ss_page_404', {
                'year': datetime.datetime.now().year,
                'message': "Dossier introuvable. Vérifiez le lien reçu par email.",
            })

        return request.render('sinistre_services.ss_page_suivi', {
            'year': datetime.datetime.now().year,
            'mission': mission,
        })

    # ─── MODAL RAPPEL ───────────────────────────────────────────────
    @http.route('/rappel', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def rappel(self, **post):
        phone = post.get('phone', '').strip()
        name = post.get('name', '').strip()
        if phone:
            try:
                mail_vals = {
                    'subject': '[Sinistre Services] Demande de rappel',
                    'body_html': f'<p><strong>Nom :</strong> {name or "Non renseigné"}</p>'
                                 f'<p><strong>Téléphone :</strong> {phone}</p>',
                    'email_from': request.website.email or 'contact@sinistre-services.fr',
                    'email_to': request.website.email or 'contact@sinistre-services.fr',
                }
                request.env['mail.mail'].sudo().create(mail_vals).send()
            except Exception as e:
                _logger.warning(f"Rappel mail failed: {e}")
        return request.redirect('/?rappel=ok')

    # ── REJOINDRE LE RÉSEAU ARTISAN ──────────────────────────────────
    def _rejoindre_render(self, **ctx):
        defaults = {
            'year': datetime.datetime.now().year,
            'error': False,
            'error_msg': '',
            'success': False,
            'form_data': {},
            'specialites_list': request.env['sinistre.specialite'].sudo().search([], order='name'),
            'departements_list': DEPARTEMENTS_FR,
        }
        defaults.update(ctx)
        return request.render('sinistre_services.page_rejoindre', defaults)

    def _rejoindre_specialite_labels(self, type_codes, autre_label):
        """Retourne les libellés des spécialités cochées + métier libre."""
        Specialite = request.env['sinistre.specialite'].sudo()
        labels = []
        for code in type_codes:
            spec = Specialite.search([('type_intervention', '=', code)], limit=1)
            labels.append(spec.name if spec else code)
        autre = (autre_label or '').strip()
        if autre:
            spec = Specialite.search([('name', '=ilike', autre)], limit=1)
            if not spec:
                spec = Specialite.create({
                    'name': autre.title(),
                    'type_intervention': 'autre',
                })
            if spec.name not in labels:
                labels.append(spec.name)
        return labels

    def _rejoindre_read_upload(self, file_storage):
        if not file_storage or not file_storage.filename:
            return None, None
        ext = ('.' + file_storage.filename.rsplit('.', 1)[-1].lower()
               if '.' in file_storage.filename else '')
        if ext not in _ALLOWED_EXTENSIONS:
            raise ValueError('format')
        data = file_storage.read()
        if len(data) > _MAX_UPLOAD_BYTES:
            raise ValueError('size')
        return base64.b64encode(data), file_storage.filename

    @http.route('/rejoindre-le-reseau', type='http', auth='public', website=True)
    def rejoindre_reseau(self, **kwargs):
        return self._rejoindre_render()

    @http.route('/rejoindre-le-reseau/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def rejoindre_send(self, **post):
        form = request.httprequest.form
        files = request.httprequest.files

        nom = post.get('nom', '').strip()
        prenom = post.get('prenom', '').strip()
        telephone = post.get('telephone', '').strip()
        email = post.get('email', '').strip()
        siret = re.sub(r'\D', '', post.get('siret', ''))
        specialites_codes = form.getlist('specialites')
        specialite_autre = post.get('specialite_autre', '').strip()
        departements = form.getlist('departements')

        form_data = dict(post)
        form_data['specialites_selected'] = specialites_codes
        form_data['departements_selected'] = departements

        if not (nom and telephone and email and prenom):
            return self._rejoindre_render(
                error=True,
                error_msg='Veuillez remplir tous les champs obligatoires.',
                form_data=form_data,
            )
        if len(siret) != 14:
            return self._rejoindre_render(
                error=True,
                error_msg='Le SIRET doit contenir exactement 14 chiffres.',
                form_data=form_data,
            )
        if not specialites_codes and not specialite_autre:
            return self._rejoindre_render(
                error=True,
                error_msg='Sélectionnez au moins une spécialité.',
                form_data=form_data,
            )
        if not departements:
            return self._rejoindre_render(
                error=True,
                error_msg="Sélectionnez au moins un département d'intervention.",
                form_data=form_data,
            )

        upload_fields = {
            'doc_certification': ('doc_certification', 'doc_certification_filename'),
            'doc_assurance': ('doc_assurance', 'doc_assurance_filename'),
            'doc_identite': ('doc_identite', 'doc_identite_filename'),
            'photo': ('photo', 'photo_filename'),
        }
        uploads = {}
        try:
            for key, (bin_field, name_field) in upload_fields.items():
                content, filename = self._rejoindre_read_upload(files.get(key))
                if not content:
                    return self._rejoindre_render(
                        error=True,
                        error_msg='Tous les documents sont obligatoires '
                                  '(certifications, assurance, pièce d\'identité, photo).',
                        form_data=form_data,
                    )
                uploads[bin_field] = content
                uploads[name_field] = filename
        except ValueError as err:
            msg = ('Chaque fichier doit faire moins de 5 Mo (PDF, JPG ou PNG).'
                   if str(err) == 'size' else
                   'Format de fichier non accepté (PDF, JPG ou PNG uniquement).')
            return self._rejoindre_render(error=True, error_msg=msg, form_data=form_data)

        specialite_labels = self._rejoindre_specialite_labels(
            specialites_codes, specialite_autre,
        )
        zone_label = ', '.join(departements)
        full_name = ' '.join(filter(None, [prenom, nom]))

        try:
            candidature = request.env['sinistre.candidature'].sudo().create({
                'prenom':            prenom,
                'nom':               nom,
                'email':             email,
                'telephone':         telephone,
                'specialites':       ', '.join(specialite_labels),
                'zone_intervention': zone_label,
                'siret':             siret,
                'statut_juridique':  post.get('statut_juridique') or False,
                'experience':        post.get('experience', ''),
                'message':           post.get('message', ''),
                **uploads,
            })

            mail_vals = {
                'subject': f'[Candidature Artisan] {full_name} — {candidature.name}',
                'body_html': f"""
                    <h3>Nouvelle candidature artisan {candidature.name}</h3>
                    <p><b>Nom :</b> {full_name}</p>
                    <p><b>Email :</b> {email}</p>
                    <p><b>Téléphone :</b> {telephone}</p>
                    <p><b>Spécialités :</b> {', '.join(specialite_labels)}</p>
                    <p><b>Statut :</b> {post.get('statut_juridique', '')}</p>
                    <p><b>Départements :</b> {zone_label}</p>
                    <p><b>SIRET :</b> {siret}</p>
                    <p><b>Expérience :</b> {post.get('experience', '')}</p>
                    <p><b>Message :</b> {post.get('message', '')}</p>
                    <p><i>Documents disponibles dans le back-office → Annuaire → Candidatures.</i></p>
                """,
                'email_from': email,
                'email_to': request.website.email or 'artisans@sinistre-services.fr',
            }
            request.env['mail.mail'].sudo().create(mail_vals).send()
        except Exception as e:
            _logger.warning("Rejoindre send failed: %s", e)
            return self._rejoindre_render(
                error=True,
                error_msg='Une erreur est survenue. Veuillez réessayer.',
                form_data=form_data,
            )

        return self._rejoindre_render(success=True)

    # ── ESPACE ARTISAN — LOGIN ───────────────────────────────────────
    @http.route('/intervenant/login', type='http', auth='public', website=True, sitemap=False)
    def intervenant_login(self, **kwargs):
        return request.render('sinistre_services.page_intervenant_login', {
            'year': datetime.datetime.now().year,
        })

    # ── Demande d'accès API sandbox (formulaire assurance) ────────────
    def _api_access_render(self, **ctx):
        defaults = {
            'year': datetime.datetime.now().year,
            'error': False,
            'success': False,
            'form_data': {},
        }
        defaults.update(ctx)
        return request.render('sinistre_services.page_api_access', defaults)

    @http.route('/assurances/api-access', type='http', auth='public',
                website=True, methods=['GET'], csrf=False)
    def api_access_form(self, **kw):
        return self._api_access_render()

    @http.route('/assurances/api-access/send', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def api_access_send(self, **post):
        societe = post.get('societe', '').strip()
        nom = post.get('nom', '').strip()
        email = post.get('email', '').strip()

        if not societe or not nom or not email or not post.get('accept_cgu'):
            return self._api_access_render(error=True, form_data=post)

        env = request.env(su=True)

        existing = env['sinistre.assurance'].search(
            [('partner_id.email', '=', email)], limit=1,
        )
        if existing:
            return self._api_access_render(success=True)

        partner = env['res.partner'].search([('email', '=', email)], limit=1)
        if not partner:
            contact_name = ' '.join(filter(None, [
                post.get('prenom', '').strip(), nom,
            ])) or societe
            partner = env['res.partner'].create({
                'name': contact_name,
                'email': email,
                'phone': post.get('telephone', '').strip(),
                'company_type': 'company',
                'comment': f"Société: {societe}",
            })

        types = []
        for t in ['serrurerie', 'plomberie', 'vitrerie', 'menuiserie', 'electricite']:
            if post.get(f'type_{t}'):
                types.append(t)

        volume_labels = {
            'moins_100': 'Moins de 100/mois',
            '100_500': '100 à 500/mois',
            '500_2000': '500 à 2 000/mois',
            'plus_2000': 'Plus de 2 000/mois',
        }
        volume = volume_labels.get(post.get('volume', ''), post.get('volume', ''))

        note_lines = [
            f"Contact: {post.get('prenom', '').strip()} {nom}".strip(),
            f"Fonction: {post.get('fonction', '')}",
            f"Volume: {volume}",
            f"Système: {post.get('systeme', '')}",
            f"Format: {post.get('format_api', 'json_rest')}",
            f"Types: {', '.join(types) or 'Non précisé'}",
            f"Besoins: {post.get('besoins', '')}",
        ]
        assurance_vals = {
            'name': societe,
            'partner_id': partner.id,
            'statut_compte': 'en_attente',
            'note': '\n'.join(note_lines),
            'format_api': post.get('format_api', 'json_rest'),
        }
        if post.get('code_assurance', '').strip():
            assurance_vals['code'] = post.get('code_assurance', '').strip()

        assurance = env['sinistre.assurance'].create(assurance_vals)

        try:
            admin = env.ref('base.user_admin')
            env['mail.mail'].create({
                'subject': f"Nouvelle demande d'accès API — {societe}",
                'email_to': admin.email or 'admin@sinistre-services.fr',
                'email_from': 'no-reply@sinistre-services.fr',
                'body_html': f"""
                    <h3>Nouvelle demande sandbox API</h3>
                    <p><b>Société :</b> {societe}</p>
                    <p><b>Contact :</b> {post.get('prenom', '')} {nom}</p>
                    <p><b>Email :</b> {email}</p>
                    <p><b>Téléphone :</b> {post.get('telephone', '')}</p>
                    <p><b>Volume :</b> {volume}</p>
                    <p><b>Système :</b> {post.get('systeme', '')}</p>
                    <p><b>Format :</b> {post.get('format_api', 'json_rest')}</p>
                    <p><b>Types :</b> {', '.join(types)}</p>
                    <p><b>Besoins :</b> {post.get('besoins', '')}</p>
                    <p><a href="/odoo/sinistre/assurances/{assurance.id}">Valider le compte dans Odoo →</a></p>
                """,
            }).send()
        except Exception:
            pass

        return self._api_access_render(success=True)
