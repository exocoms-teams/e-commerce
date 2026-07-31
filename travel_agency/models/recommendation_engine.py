from odoo import models, api


class TravelRecommendationEngine(models.AbstractModel):
    _name = 'travel.recommendation.engine'
    _description = 'Moteur de recommandation destination + hôtel'

    @api.model
    def get_recommendations(self, budget_max, nb_personnes, etoiles_min=None, pays=None, type_voyage=None):
        domain = [
                ('prix_par_personne', '>', 0),
                ('disponible', '=', True),
            ]
        if nb_personnes:
            domain.append(('nombre_personnes_max', '>=', nb_personnes))
        
        if pays:
            domain.append(('pays_destination', 'ilike', pays))

        destinations = self.env['product.template'].sudo().search(domain)

        results = []
        for dest in destinations:
            if not dest.prix_par_personne:
                continue
            if dest.prix_par_personne > budget_max * 1.15:  # marge de tolérance 15%
                continue

            score = 0
            # Plus proche du budget = mieux
            ecart_budget = abs(dest.prix_par_personne - budget_max) / budget_max
            score += max(0, 10 - ecart_budget * 10)
            # Bonus étoiles si un minimum est demandé
            if etoiles_min and dest.etoiles:
                if int(dest.etoiles) >= int(etoiles_min):
                    score += 5
                else:
                    continue  # ne correspond pas au confort minimum demandé
            results.append((score, dest))

        results.sort(key=lambda x: x[0], reverse=True)
        top_destinations = [d for _, d in results[:3]]

        # Pour chaque destination retenue, chercher un hôtel correspondant
        recommendations = []
        for dest in top_destinations:
            hotel_domain = [('disponible', '=', True)]
            if dest.ville_destination:
                hotel_domain.append(('ville', 'ilike', dest.ville_destination))
            if etoiles_min:
                hotel_domain.append(('etoiles', '>=', etoiles_min))
            hotels = self.env['travel.hotel'].sudo().search(hotel_domain, limit=2, order='prix_par_nuit asc')
            recommendations.append({'destination': dest, 'hotels': hotels})

        return recommendations