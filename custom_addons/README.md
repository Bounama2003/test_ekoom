# SaaS Multi-Tenant Odoo 19 Enterprise - README

## Table des matières

1. [Présentation](#présentation)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Installation Odoo 19 Enterprise sur Windows](#installation-odoo-19-enterprise-sur-windows)
5. [Configuration PostgreSQL](#configuration-postgresql)
6. [Installation des modules SaaS](#installation-des-modules-saas)
7. [Lancement de la base MASTER](#lancement-de-la-base-master)
8. [Configuration des Packs Métiers](#configuration-des-packs-métiers)
9. [Création d'un tenant](#création-dun-tenant)
10. [Activation d'un pack](#activation-dun-pack)
11. [Vérification des restrictions](#vérification-des-restrictions)
12. [Tests fonctionnels et sécurité](#tests-fonctionnels-et-sécurité)
13. [Erreurs courantes et debug](#erreurs-courantes-et-debug)

---

## Présentation

Ce projet implémente une architecture **SaaS Multi-Tenant** pour Odoo 19 Enterprise sur Windows avec les caractéristiques suivantes :

- **1 client = 1 base PostgreSQL**
- **1 base MASTER** pour le Super Admin SaaS
- **Activation des fonctionnalités par PACK MÉTIER**
- **Sécurité serveur HARD** (Python override)
- **Limitation utilisateurs** (100 max/tenant)
- **Interdiction technique** d'installer des modules hors pack

---

## Architecture

### Modules créés

```
/addons
  /saas_superadmin        # Installé UNIQUEMENT sur la base MASTER
  /saas_tenant_guard      # Installé sur CHAQUE base tenant
```

### Packs Métiers

#### Agro-Business
- **Pack Usine Connectée** : `mrp`, `quality`, `maintenance`, `stock`
- **Pack Distribution & Force de Vente** : `sale`, `crm`, `stock`, `sign`
- **Pack Export & Conformité** : `documents`, `website_sale`, `marketing_automation`

#### Logistique
- **Pack Performance Flotte** : `fleet`, `fieldservice`, `purchase`, `hr_expense`, `analytic_account`

#### Immobilier
- **Pack Gestion Immobilière** : `subscription`, `crm`, `calendar`, `fieldservice`, `account`

---

## Prérequis

- **Windows 10 ou 11**
- **Odoo 19 Enterprise** (sources déjà présentes)
- **PostgreSQL 15+** (locale C)
- **Python 3.10+** (officiel Odoo)
- **Service Windows** pour Odoo

---

## Installation Odoo 19 Enterprise sur Windows

### 1. Télécharger et installer PostgreSQL

1. Télécharger PostgreSQL depuis le site officiel
2. Installer avec les paramètres suivants :
   - Port : 5432
   - Password postgres : choisir un mot de passe sécurisé
   - Locale : C
   - Encoding : UTF8

### 2. Vérifier PostgreSQL

```sql
-- Via pgAdmin ou psql
psql -U postgres
postgres=# SELECT version();
postgres=# \l
```

### 3. Configurer le service Windows Odoo

1. Ouvrir l'invite de commande en tant qu'administrateur
2. Se positionner dans le répertoire Odoo
3. Installer le service :
```cmd
sc create Odoo19 binPath="C:\path\to\odoo\service\odoo.exe" start= auto
```

4. Configurer le fichier `odoo.conf` :
```ini
[options]
addons_path = C:\path\to\odoo\addons,C:\path\to\custom\addons
admin_passwd = super_secure_password
db_host = localhost
db_port = 5432
db_user = postgres
db_password = your_postgres_password
dbfilter = ^%d$
logfile = C:\path\to\odoo\logs\odoo.log
logrotate = True
```

---

## Configuration PostgreSQL

### 1. Créer la base MASTER

Via l'interface web Odoo :
1. Lancer Odoo via le service Windows
2. Accéder à `http://localhost:8069`
3. Sélectionner "Gérer les bases de données"
4. Créer la base `master` avec un compte admin

### 2. Vérifier la connexion

Via pgAdmin, vérifier que la base `master` est créée et accessible.

---

## Installation des modules SaaS

### 1. Copier les modules

Copier les dossiers suivants dans `custom_addons` :
```
/saas_superadmin
/saas_tenant_guard
```

### 2. Installer saas_superadmin sur la base MASTER

1. Se connecter à la base `master` en tant qu'admin
2. Aller dans **Apps**
3. Supprimer le filtre "Apps"
4. Rechercher **SaaS Super Admin**
5. Cliquer sur **Installer**

### 3. Vérifier l'installation

Un nouveau menu **SaaS Admin** apparaît avec :
- Tenants
- Business Packs
- Pack Modules

---

## Lancement de la base MASTER

### 1. Démarrer le service Odoo

```cmd
net start Odoo19
```

### 2. Accéder à l'interface

- URL : `http://localhost:8069`
- Base de données : `master`
- Utilisateur : admin (créé lors de l'installation)
- Mot de passe : celui défini lors de la création

### 3. Configurer le Super Admin SaaS

1. Aller dans **Settings > Users & Companies**
2. Sélectionner l'utilisateur admin
3. Ajouter le groupe **SaaS Super Admin**
4. Enregistrer

---

## Configuration des Packs Métiers

### 1. Créer les Packs Agro-Business

#### Pack Usine Connectée
1. Aller dans **SaaS Admin > Business Packs**
2. Cliquer sur **Create**
3. Remplir :
   - Pack Code : `AGRO_USINE`
   - Pack Name : `Pack Usine Connectée`
   - Category : `Agro-Business`
   - Included Modules : `mrp`, `quality`, `maintenance`, `stock`
4. Cocher **Is Predefined**
5. Enregistrer

#### Pack Distribution & Force de Vente
1. Créer un nouveau pack
2. Remplir :
   - Pack Code : `AGRO_DISTRIBUTION`
   - Pack Name : `Pack Distribution & Force de Vente`
   - Category : `Agro-Business`
   - Included Modules : `sale`, `crm`, `stock`, `sign`
3. Cocher **Is Predefined**
4. Enregistrer

#### Pack Export & Conformité
1. Créer un nouveau pack
2. Remplir :
   - Pack Code : `AGRO_EXPORT`
   - Pack Name : `Pack Export & Conformité`
   - Category : `Agro-Business`
   - Included Modules : `documents`, `website_sale`, `marketing_automation`
3. Cocher **Is Predefined**
4. Enregistrer

### 2. Créer le Pack Logistique

#### Pack Performance Flotte
1. Créer un nouveau pack
2. Remplir :
   - Pack Code : `LOG_FLOTTE`
   - Pack Name : `Pack Performance Flotte`
   - Category : `Logistique`
   - Included Modules : `fleet`, `fieldservice`, `purchase`, `hr_expense`, `analytic_account`
3. Cocher **Is Predefined**
4. Enregistrer

### 3. Créer le Pack Immobilier

#### Pack Gestion Immobilière
1. Créer un nouveau pack
2. Remplir :
   - Pack Code : `IMMO_GESTION`
   - Pack Name : `Pack Gestion Immobilière`
   - Category : `Immobilier`
   - Included Modules : `subscription`, `crm`, `calendar`, `fieldservice`, `account`
3. Cocher **Is Predefined**
4. Enregistrer

---

## Création d'un tenant

### 1. Via l'interface web

1. Aller dans **SaaS Admin > Tenants**
2. Cliquer sur **Create New Tenant** (Wizard)
3. Remplir les informations :
   - Tenant Name : `Mon Client Agro`
   - Database Name : `mon_client_agro_db`
   - Company Name : `Mon Client Agro Inc.`
   - Admin Email : `admin@monclient.com`
   - Admin Phone : `+33123456789`
   - Business Pack : Choisir un pack (ex: Pack Usine Connectée)
   - Max Users : 100 (par défaut)
   - Notes : (optionnel)
4. Cliquer sur **Create Tenant**

### 2. État du tenant

Le tenant est créé avec l'état **Draft**.

### 3. Créer la base de données

1. Se déconnecter de la base `master`
2. Retourner sur `http://localhost:8069`
3. Sélectionner **Gérer les bases de données**
4. Créer la base `mon_client_agro_db` avec le compte admin
5. Se connecter à la nouvelle base

### 4. Installer saas_tenant_guard

1. Sur la nouvelle base, aller dans **Apps**
2. Supprimer le filtre "Apps"
3. Rechercher **SaaS Tenant Guard**
4. Cliquer sur **Installer**

---

## Activation d'un pack

### 1. Retourner sur la base MASTER

1. Se connecter à `master`
2. Aller dans **SaaS Admin > Tenants**
3. Sélectionner le tenant créé

### 2. Activer le tenant

1. Cliquer sur le bouton **Activate**
2. Les paramètres du pack sont automatiquement configurés sur la base tenant
3. **Installation manuelle des modules** : Sur la base tenant, aller dans **Apps**, rechercher et installer les modules autorisés du pack

### 3. Vérification sur la base tenant

1. Se connecter à la base tenant
2. Aller dans **Apps**
3. Vérifier que les modules du pack sont installés

---

## Vérification des restrictions

### 1. Limite utilisateurs

1. Créer 100 utilisateurs
2. Essayer de créer le 101ème
3. **Résultat attendu** : Message d'erreur
```
User limit reached.

This tenant is limited to 100 users maximum.
Current users: 100

Contact your SaaS provider to increase your user limit.
```

### 2. Interdiction d'installer des modules hors pack

1. Sur la base tenant, aller dans **Apps**
2. Rechercher un module hors pack (ex: `website_blog`)
3. Cliquer sur **Installer**
4. **Résultat attendu** : Message d'erreur
```
Module "website_blog" is not authorized for installation.

This tenant is restricted to specific modules based on the assigned Business Pack.
Contact your SaaS provider to request additional modules.
```

### 3. Modules visibles

1. Sur la base tenant, aller dans **Apps**
2. **Résultat attendu** : Seuls les modules du pack assigné sont visibles (filtrés automatiquement)

---

## Tests fonctionnels et sécurité

### Test 1 : Création tenant

**Étapes** :
1. Base MASTER → SaaS Admin → Create New Tenant
2. Remplir les informations
3. Créer la base via l'interface web
4. Installer saas_tenant_guard

**Résultat attendu** :
- Tenant créé en état Draft
- Base créée avec succès
- Module saas_tenant_guard installé

---

### Test 2 : Activation tenant

**Étapes** :
1. Base MASTER → SaaS Admin → Tenants
2. Sélectionner le tenant
3. Cliquer sur Activate

**Résultat attendu** :
- Tenant passe en état Active
- Modules du pack installés automatiquement

---

### Test 3 : Limite utilisateurs

**Étapes** :
1. Base tenant → Settings → Users
2. Créer 100 utilisateurs
3. Tenter de créer le 101ème

**Résultat attendu** :
- Erreur UserError avec message clair
- Pas de contournement possible

---

### Test 4 : Sécurité modules

**Étapes** :
1. Base tenant → Apps
2. Rechercher module hors pack
3. Tenter d'installer

**Résultat attendu** :
- Erreur UserError
- Message indiquant que le module n'est pas autorisé

---

### Test 5 : Changement de pack

**Étapes** :
1. Base MASTER → SaaS Admin → Tenants
2. Sélectionner un tenant actif
3. Tenter de changer le pack

**Résultat attendu** :
- Erreur UserError
- Message indiquant de suspendre le tenant d'abord

---

### Test 6 : Suspension tenant

**Étapes** :
1. Base MASTER → SaaS Admin → Tenants
2. Sélectionner un tenant actif
3. Cliquer sur Suspend
4. Changer le pack
5. Réactiver le tenant

**Résultat attendu** :
- Tenant suspendu
- Pack changé
- Tenant réactivé
- Nouveaux modules installés

---

## Erreurs courantes et debug

### Erreur 1 : Database name "master" is reserved

**Cause** : Tentative de créer un tenant avec le nom de base `master`

**Solution** : Utiliser un autre nom de base

---

### Erreur 2 : Only active tenants can be suspended

**Cause** : Tentative de suspendre un tenant non actif

**Solution** : Activer le tenant d'abord

---

### Erreur 3 : User limit reached

**Cause** : Tentative de créer plus de 100 utilisateurs

**Solution** : Contacter le SaaS provider pour augmenter la limite

---

### Erreur 4 : Module not authorized for installation

**Cause** : Tentative d'installer un module hors pack

**Solution** : Contacter le SaaS provider pour ajouter le module au pack

---

### Erreur 5 : Cannot change pack for active tenant

**Cause** : Tentative de changer le pack d'un tenant actif

**Solution** : Suspendre le tenant, changer le pack, puis réactiver

---

## Debug

### Logs Odoo

Les logs sont dans le fichier configuré dans `odoo.conf` :
```
logfile = C:\path\to\odoo\logs\odoo.log
```

### Vérifier les paramètres SaaS

Sur une base tenant, via Python :
```python
env['ir.config_parameter'].sudo().search([
    ('key', 'like', 'saas_tenant_guard.%')
]).read()
```

Résultat attendu :
```
[
    {'key': 'saas_tenant_guard.pack_id', 'value': '1'},
    {'key': 'saas_tenant_guard.allowed_modules', 'value': 'mrp,quality,maintenance,stock'},
    {'key': 'saas_tenant_guard.max_users', 'value': '100'},
    {'key': 'saas_tenant_guard.is_active', 'value': 'True'}
]
```

---

## Maintenance

### Mettre à jour un pack

1. Base MASTER → SaaS Admin → Business Packs
2. Sélectionner le pack
3. Modifier la liste des modules
4. Enregistrer
5. Suspendre le tenant
6. Réactiver le tenant

---

### Supprimer un tenant

1. Suspendre ou archiver le tenant
2. Base MASTER → SaaS Admin → Tenants
3. Sélectionner le tenant
4. Cliquer sur Action → Delete
5. Supprimer manuellement la base PostgreSQL via pgAdmin

---

## Sécurité

### Rôles

**SUPER ADMIN SAAS**
- Accès UNIQUEMENT sur la base MASTER
- Gère les tenants et les packs
- N'apparaît JAMAIS dans les utilisateurs des tenants

**ADMIN TENANT**
- Administrateur de SA base
- Gère SES utilisateurs
- NE PEUT PAS devenir super admin
- NE PEUT PAS installer de modules hors pack

### Restrictions HARD

- **Python override** de `ir.module.module.button_install`
- **Python override** de `res.users.create`
- **Aucune logique JS**
- **Aucun contournement possible**

---

## Support

Pour toute question ou problème, consulter :
- Logs Odoo
- Documentation Odoo officielle
- PostgreSQL logs

---

## Licence

LGPL-3
