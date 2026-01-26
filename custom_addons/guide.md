# Guide de Test pour l'Application SaaS Odoo

Ce guide vous accompagne étape par étape pour tester les fonctionnalités de l'application SaaS personnalisée dans l'interface web d'Odoo. Après chaque test, revenez vers moi avec le statut **"réussi"** si vous avez réussi à effectuer l'action, ou **"échec"** si vous avez rencontré un problème. Indiquez également une brève description de ce qui s'est passé en cas d'échec.

## Prérequis
- Assurez-vous qu'Odoo est installé et fonctionne sur votre serveur (version 19 recommandée).
- Les modules `saas_superadmin` et `saas_tenant_guard` doivent être présents dans le répertoire `custom_addons` d'Odoo.
- Vous devez avoir accès à l'interface web d'Odoo en tant qu'administrateur.
- **Important** : L'utilisateur PostgreSQL d'Odoo doit avoir les permissions pour créer des bases de données (droits CREATEDB).

## Étape 1 : Installation des Modules
1. Connectez-vous à l'interface web d'Odoo avec un compte administrateur.
2. Allez dans **Applications** (menu principal).
3. Cliquez sur **Mettre à jour la liste des applications** pour rafraîchir les modules disponibles.
4. Recherchez et installez le module **SaaS Superadmin** (uniquement sur la base de données master).
5. Le module **SaaS Tenant Guard** sera installé automatiquement sur chaque base de données tenant lors de leur création via le wizard de création de tenant (pas besoin de l'installer manuellement).
6. Vérifiez que le module SaaS Superadmin est installé sans erreurs (pas de messages d'erreur dans les logs).

**Test : Installation des modules**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 2 : Création de la Base de Données Master
1. Si ce n'est pas déjà fait, créez une nouvelle base de données Odoo via l'interface de gestion des bases de données (accessible via `/web/database/manager`).
2. Nommez-la quelque chose comme "master_db".
3. Installez les modules SaaS sur cette base.
4. Connectez-vous à cette base avec un compte admin.

**Test : Création de la base de données master**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 3 : Configuration des Paramètres SaaS
**Note** : Les modules SaaS Superadmin et SaaS Tenant Guard ne nécessitent pas de configuration manuelle des paramètres. Tous les paramètres sont gérés automatiquement par le système lors de la création des tenants et packs.

Si vous souhaitez vérifier les paramètres système généraux d'Odoo :
1. Dans l'interface web, allez dans **Paramètres > Paramètres généraux**.
2. Vérifiez les paramètres de base comme la langue, la devise, etc.
3. Aucun paramètre spécifique SaaS n'est requis pour ces modules.

**Test : Configuration des paramètres SaaS**  
(Pas de configuration nécessaire - marquez comme réussi)

## Étape 4 : Création d'un Pack SaaS
1. Allez dans le menu **SaaS > Packs** (ou similaire, selon les vues définies).
2. Cliquez sur **Créer** pour ajouter un nouveau pack.
3. Remplissez les champs : nom du pack, modules inclus, limites (utilisateurs, stockage, etc.).
4. Sauvegardez le pack.

**Test : Création d'un pack SaaS**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 5 : Création d'un Tenant
1. Allez dans le menu **SaaS > Tenants**.
2. Cliquez sur **"Nouveau"** (ou **"Create"**) pour ajouter un nouveau tenant.
3. Remplissez les informations :
   - **Nom du tenant** : Nom affiché du tenant
   - **Nom de la base de données** : Nom technique de la DB PostgreSQL (ex: tenant1_db)
   - **Nom de l'entreprise** : Nom de l'entreprise du tenant
   - **Pack métier** : Sélectionnez un pack créé à l'étape 4
   - **Email de l'admin** : Email de l'administrateur (deviendra le login)
   - **Mot de passe admin** : Mot de passe pour l'utilisateur admin (remplissez pour créer automatiquement la DB)
   - **Téléphone admin** : Téléphone (optionnel)
   - **Nombre max d'utilisateurs** : Limite d'utilisateurs (défaut 100)
   - **Notes** : Informations supplémentaires
4. Cliquez sur **"Sauvegarder"**.

**Note importante** : Si vous remplissez le champ **"Mot de passe admin"**, le système créera automatiquement :
- La base de données PostgreSQL pour le tenant
- L'utilisateur administrateur avec les identifiants fournis

Après création, vous devrez **manuellement installer le module "SaaS Tenant Guard"** sur la nouvelle base de données :
1. Connectez-vous à la nouvelle DB : `http://localhost:8069/web?db=tenant1db`
2. Allez dans **Applications**
3. Recherchez et installez **"SaaS Tenant Guard"**

Si vous laissez le champ vide, seul l'enregistrement tenant sera créé (pour modification manuelle ultérieure).

**Test : Création d'un tenant**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 6 : Assignation d'un Pack à un Tenant
**Important** : Cette opération doit être faite depuis la base de données **master**, pas depuis la DB tenant.

1. Retournez sur la base de données master (`http://localhost:8069/web?db=master_db`)
2. Allez dans le menu **SaaS > Tenants**
3. Ouvrez le tenant créé à l'étape précédente
4. Cliquez sur le bouton **"Assign Pack"** dans l'en-tête
5. Dans le wizard qui s'ouvre :
   - Le tenant est pré-sélectionné
   - Choisissez un pack dans la liste
   - Cliquez sur **"Assign Pack"**
6. Vérifiez que le pack est bien assigné au tenant (champ "Pack métier")

**Test : Assignation d'un pack à un tenant**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 7 : Changement de Pack pour un Tenant
1. Ouvrez un tenant existant.
2. Utilisez l'assistant **Changer Pack**.
3. Sélectionnez un nouveau pack et confirmez le changement.
4. Vérifiez que le pack a été mis à jour.

**Test : Changement de pack pour un tenant**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 8 : Désactivation d'un Tenant
1. Ouvrez un tenant actif.
2. Utilisez l'assistant **Désactiver Tenant**.
3. Confirmez la désactivation.
4. Vérifiez que le tenant est marqué comme inactif.

**Test : Désactivation d'un tenant**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 9 : Vérification des Permissions et Sécurité
1. Créez un utilisateur non-admin dans un tenant.
2. Vérifiez que les groupes de sécurité définis dans `saas_tenant_guard` limitent correctement l'accès (par exemple, empêcher l'installation de modules non autorisés).
3. Essayez d'installer un module depuis cet utilisateur et assurez-vous que c'est bloqué si nécessaire.

**Test : Vérification des permissions et sécurité**  
Revenez vers moi avec le statut : réussi ou échec.

## Étape 10 : Test des Fonctionnalités Avancées
1. Testez la création automatique de bases de données pour les tenants.
2. Vérifiez les données par défaut chargées (via les fichiers XML dans `data/`).
3. Testez les vues et menus personnalisés dans l'interface.

**Test : Fonctionnalités avancées**  
Revenez vers moi avec le statut : réussi ou échec.

## Conclusion
Une fois tous les tests terminés, faites-moi un résumé global. Si vous rencontrez des erreurs persistantes, fournissez les logs d'Odoo ou des captures d'écran pour diagnostiquer les problèmes.