# Copyright 2026 EXOCOMS Group (https://www.exocoms.fr)
# Licence : OPL-1 (Odoo Proprietary License v1.0). Voir le fichier LICENSE.

# URL de base de la Business API.
API_BASE_URL_LIVE = 'https://b2b.revolut.com/api/1.0/'
API_BASE_URL_SANDBOX = 'https://sandbox-b2b.revolut.com/api/1.0/'

# Audience imposee par Revolut dans le JWT d'assertion client.
JWT_AUDIENCE = 'https://revolut.com'

# Duree de validite du JWT d'assertion genere a chaque echange de jeton.
JWT_LIFETIME_SECONDS = 60 * 60

# Marge de securite avant expiration du jeton d'acces (qui vit 40 minutes).
ACCESS_TOKEN_SAFETY_MARGIN_SECONDS = 120

# Nombre maximum de transactions renvoyees par appel (limite Revolut).
TRANSACTIONS_PAGE_SIZE = 1000

# Types de transaction Revolut consideres comme des encaissements marchands.
# Ajustables par connexion : Revolut ne garantit pas un type unique pour les
# versements du compte marchand vers le compte courant.
MERCHANT_SETTLEMENT_TYPES = ['topup', 'transfer']

# Etats de transaction importes. Les transactions en attente sont ignorees :
# elles n'ont pas encore d'impact sur le solde du compte.
IMPORTED_STATES = ['completed']
