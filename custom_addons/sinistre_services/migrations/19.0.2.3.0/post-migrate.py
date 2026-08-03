# -*- coding: utf-8 -*-
"""
Migration 2.3.0 — POST-migrate
Injecte la vue complète (notebook + nouveaux onglets) une fois
que toutes les colonnes et tables existent en base.
"""
import logging
_logger = logging.getLogger(__name__)

_FULL_ARCH = """\
<form string="Intervenant">
  <sheet>
    <div class="oe_button_box" name="button_box">
      <button name="action_voir_missions" type="object"
              class="oe_stat_button" icon="fa-tasks">
        <field name="mission_count" widget="statinfo" string="Missions"/>
      </button>
    </div>
    <div class="oe_title">
      <h1><field name="name" placeholder="Nom de l&apos;intervenant"/></h1>
    </div>
    <notebook>

      <page string="G&eacute;n&eacute;ral" name="general">
        <group>
          <group string="Informations">
            <field name="partner_id" options="{&apos;quick_create&apos;: false}"/>
            <field name="user_id" help="Compte pour acc&egrave;s PWA"/>
            <field name="specialites" widget="many2many_tags"/>
            <field name="zone_intervention"/>
          </group>
          <group string="Contrat">
            <field name="taux_commission" widget="percentage"/>
            <field name="disponible" widget="boolean_toggle"/>
            <field name="actif" widget="boolean_toggle"/>
            <field name="fcm_token" readonly="1"/>
          </group>
        </group>
        <group string="Notes">
          <field name="note" nolabel="1"/>
        </group>
      </page>

      <page string="Coordonn&eacute;es bancaires" name="bancaire">
        <group string="Informations bancaires">
          <group>
            <field name="iban"/>
            <field name="bic"/>
          </group>
          <group>
            <field name="titulaire_compte"/>
            <field name="banque"/>
          </group>
        </group>
      </page>

      <page string="Planning" name="planning">
        <group string="Heures d&apos;ouverture (JSON)">
          <field name="planning_slots" nolabel="1" widget="text"
                 placeholder="G&eacute;r&eacute; via l&apos;application mobile PWA"/>
        </group>
        <separator string="Absences exceptionnelles"/>
        <field name="absence_ids">
          <list editable="bottom">
            <field name="date_debut"/>
            <field name="date_fin"/>
            <field name="motif"/>
          </list>
        </field>
      </page>

      <page string="Statistiques" name="stats">
        <group>
          <group string="Chiffre d&apos;affaires">
            <field name="ca_total" widget="monetary"/>
            <field name="commission_due" widget="monetary"/>
          </group>
        </group>
        <field name="certification_ids">
          <list editable="bottom">
            <field name="name"/>
            <field name="date_validite"/>
          </list>
        </field>
      </page>

    </notebook>
  </sheet>
  <chatter/>
</form>"""


def migrate(cr, version):
    _logger.info("[sinistre 2.3.0] post-migrate START")

    cr.execute("""
        UPDATE ir_ui_view
           SET arch_db = %s,
               write_date = NOW()
         WHERE model = 'sinistre.intervenant'
           AND type  = 'form'
           AND name  = 'sinistre.intervenant.form'
    """, (_FULL_ARCH,))

    updated = cr.rowcount
    _logger.info("[sinistre 2.3.0] vue intervenant mise à jour (%s ligne(s))", updated)

    if updated == 0:
        _logger.warning("[sinistre 2.3.0] aucune vue trouvée — vérifier le name/model")

    _logger.info("[sinistre 2.3.0] post-migrate END")
