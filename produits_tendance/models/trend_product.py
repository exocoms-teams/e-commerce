source = fields.Selection([
        ('scraping', 'Scraping'),
        ('crowdsourcing', 'Crowdsourcing'),
        ('api', 'API'),
    ], string="Source", required=True, default='api')

    ad_ids = fields.One2many(
        'trend.ad',
        'product_id',
        string="Publicités liées"
    )

    _product_ref_source_uniq = models.Constraint(
        'unique(product_ref, source)',
        "Ce produit (référence + source) est déjà enregistré. Impossible de le dupliquer.",
    )

    @api.constrains('sales_count')
    def _check_sales_count_positive(self):
        for record in self:
            if record.sales_count is not None and record.sales_count < 0:
                raise ValidationError(
                    "Le nombre de ventes (sales_count) ne peut pas être négatif."
                )