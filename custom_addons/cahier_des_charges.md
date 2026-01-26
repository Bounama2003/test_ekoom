TU ES UN ARCHITECTE ODOO SENIOR (10+ ANS) ET UN EXPERT SAAS MULTI-TENANT.
TU CONNAIS EN PROFONDEUR ODOO ENTERPRISE, LE CORE ORM, LES HOOKS, LA SÉCURITÉ,
ET TU RESPECTES STRICTEMENT LES BONNES PRATIQUES ODOO.

=====================================================
OBJECTIF GLOBAL
=====================================================

Générer UN PROJET COMPLET ODOO 19 ENTERPRISE, PRÊT À L’EMPLOI,
FONCTIONNANT EN LOCAL SUR WINDOWS,
SANS AUCUN SCRIPT EXTERNE, SANS COMMANDE TERMINAL,
UNIQUEMENT VIA L’INTERFACE WEB ODOO (SERVICE WINDOWS).

Le projet implémente une architecture SaaS MULTI-TENANT STRICTE :
- 1 client = 1 base PostgreSQL
- 1 base MASTER = Super Admin SaaS
- Activation des fonctionnalités par PACK MÉTIER
- Sécurité serveur HARD (Python override)
- Limitation utilisateurs
- Interdiction technique d’installer des modules hors pack

=====================================================
CONTRAINTES TECHNIQUES OBLIGATOIRES
=====================================================

- Odoo 19 Enterprise UNIQUEMENT
- Windows 10 / 11
- PostgreSQL local
- Python officiel fourni avec Odoo
- Sources Odoo déjà présentes (PAS pip install odoo)
- Odoo lancé comme SERVICE WINDOWS
- Création des bases via l’INTERFACE WEB ODOO
- PAS DE :
  - scripts .bat
  - scripts shell
  - subprocess
  - commandes odoo-bin
  - dashboards graphiques
  - appels système
  - crontabs

TOUTE LA LOGIQUE DOIT ÊTRE :
- Python Odoo natif
- Wizards Odoo
- ORM Odoo
- Sécurité Odoo

=====================================================
NICHES MÉTIERS
=====================================================

1. Agro-business
2. Logistique
3. Immobilier

=====================================================
PACKS MÉTIERS (OBLIGATOIRES)
=====================================================

AGRO-BUSINESS
- Pack Usine Connectée
  Modules : mrp, quality, maintenance, stock

- Pack Distribution & Force de Vente
  Modules : sale, crm, stock (multi-warehouse), sign

- Pack Export & Conformité
  Modules : documents, website_sale, marketing_automation

LOGISTIQUE
- Pack Performance Flotte
  Modules : fleet, fieldservice, purchase, hr_expense, analytic_account
  (QR Code EXCLU – futur uniquement)

IMMOBILIER
- Pack Gestion Immobilière
  Modules : subscription, crm, calendar, fieldservice, account

=====================================================
RÔLES & SÉCURITÉ (CRITIQUE)
=====================================================

1. SUPER ADMIN SAAS
- GLOBAL
- UNIQUE
- Accès UNIQUEMENT sur la base MASTER
- Gère :
  - tenants
  - packs
  - associations packs ↔ modules
- N’APPARAÎT JAMAIS dans les utilisateurs des tenants
- Groupe dédié : group_saas_superadmin

2. ADMIN TENANT
- Administrateur de SA base
- Gère SES utilisateurs
- NE PEUT PAS :
  - devenir super admin
  - voir le super admin
  - installer des modules hors pack

=====================================================
LIMITATION UTILISATEURS (HARD)
=====================================================

- 100 utilisateurs INTERNES maximum par tenant
- Blocage serveur obligatoire :
  override res.users.create
- Message UserError clair
- AUCUNE logique JS
- AUCUN contournement possible

=====================================================
SÉCURITÉ MODULES (HARD)
=====================================================

UN TENANT NE PEUT PAS :
- Installer un module hors pack
- Voir un module non autorisé
- Forcer l’installation par URL ou RPC

OBLIGATION TECHNIQUE :
- override Python de ir.module.module.button_install
- vérification AVANT toute installation
- whitelist stockée dans ir.config_parameter
- blocage UserError immédiat

=====================================================
ARCHITECTURE À PRODUIRE
=====================================================

/addons
  /saas_superadmin
  /saas_tenant_guard

=====================================================
MODULE 1 : saas_superadmin (BASE MASTER)
=====================================================

INSTALLÉ UNIQUEMENT SUR LA BASE MASTER

Fonctions :
- CRUD Tenants
- CRUD Packs
- CRUD Pack ↔ Modules
- Wizards :
  - create tenant (sans créer la DB automatiquement)
  - assign pack
  - change pack
  - deactivate tenant
- Installation LOGIQUE des modules :
  - via ir.module.module sur la base cible
- Sécurité stricte (ACL + record rules)

INTERDICTIONS :
- PAS de dashboard
- PAS de script
- PAS de subprocess
- PAS de création DB automatique

Livrables COMPLETS :
- __manifest__.py
- models/*.py
- views/*.xml
- security/*.csv
- wizards/*.py
- menus XML
- ACL RÉELLES
- COMMENTAIRES clairs

=====================================================
MODULE 2 : saas_tenant_guard (BASE TENANT)
=====================================================

INSTALLÉ AUTOMATIQUEMENT PAR LE SUPER ADMIN

Fonctions :
- Stocker pack actif
- Stocker modules autorisés
- Bloquer installation modules non autorisés
- Limiter utilisateurs à 100
- Paramètres dans ir.config_parameter
- Invisible pour l’admin tenant

HOOKS OBLIGATOIRES :
- ir.module.module.button_install
- res.users.create

=====================================================
DOCUMENTATION OBLIGATOIRE
=====================================================

GÉNÉRER UN README.md DÉTAILLÉ contenant :

1. Installation Odoo 19 Enterprise sur Windows
2. Configuration PostgreSQL (locale C)
3. Lancement de la base MASTER
4. Création d’un tenant VIA L’INTERFACE WEB
5. Activation d’un pack
6. Vérification des restrictions
7. Tests fonctionnels et sécurité
8. Erreurs courantes et debug

=====================================================
FORMAT DE SORTIE
=====================================================

1. Arborescence complète
2. TOUS les fichiers Python / XML / CSV
3. README.md détaillé
4. CODE RÉEL ODOO 19
5. AUCUN pseudo-code
6. AUCUN script système
7. COMPATIBLE SERVICE ODOO WINDOWS

COMMENCE PAR :
1) Générer l’arborescence complète
2) Puis les fichiers UN PAR UN
3) Puis le README

RESPECTE STRICTEMENT TOUTES LES CONTRAINTES.
