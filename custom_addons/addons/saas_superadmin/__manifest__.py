{
    "name": "SaaS Super Admin",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "SaaS Multi-Tenant Super Administration",
    "description": """
        SaaS Super Admin Module
        ========================

        Ce module est installé UNIQUEMENT sur la base MASTER.

        Fonctionnalités:
        - Gestion des tenants SaaS (CRUD)
        - Gestion des packs métiers (CRUD)
        - Association pack ↔ modules
        - Wizards de création tenant, assignation pack, changement pack
        - Installation logique des modules via ir.module.module
        - Sécurité stricte (ACL + record rules)

        Interdictions:
        - Pas de dashboard
        - Pas de script système
        - Pas de subprocess
        - Pas de création DB automatique
    """,
    "author": "SaaS Architecture",
    "website": "https://www.saas-architecture.com",
    "license": "LGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/saas_superadmin_security.xml",
        "views/saas_tenant_views.xml",
        "views/saas_pack_views.xml",
        "views/saas_tenant_menus.xml",
        "wizards/saas_create_tenant_views.xml",
        "wizards/saas_assign_pack_views.xml",
        "wizards/saas_change_pack_views.xml",
        "wizards/saas_deactivate_tenant_views.xml",
        "data/saas_pack_category_data.xml",
        "data/saas_pack_data.xml"
    ],
    "i18n": ["i18n/fr.po", "i18n/es.po", "i18n/de.po"],
    "assets": {
        "web.assets_backend": [
            "saas_superadmin/static/src/css/saas_superadmin.css"
        ]
    },
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False
}