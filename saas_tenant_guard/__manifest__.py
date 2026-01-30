{
    "name": "SaaS Tenant Guard",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "SaaS Multi-Tenant Security and Restrictions",
    "description": """
        SaaS Tenant Guard Module
        ========================
        
        Ce module est installé AUTOMATIQUEMENT par le Super Admin sur chaque base tenant.
        
        Fonctionnalités:
        - Stocker le pack actif
        - Stocker les modules autorisés
        - Bloquer l'installation de modules non autorisés
        - Limiter les utilisateurs à 100 maximum
        - Paramètres dans ir.config_parameter
        - Invisible pour l'admin tenant
        
        Hooks obligatoires:
        - ir.module.module.button_install
        - res.users.create
        
        Sécurité HARD:
        - Override Python de ir.module.module.button_install
        - Override Python de res.users.create
        - Aucune logique JS
        - Aucun contournement possible
    """,
    "author": "SaaS Architecture",
    "website": "https://www.saas-architecture.com",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/saas_tenant_guard_security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "saas_tenant_guard/static/src/css/saas_tenant_guard.css",
        ],
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
