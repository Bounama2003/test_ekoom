# Guide de déploiement sur Odoo.sh (Multi‑tenant)  
**Version** : 1.0  
**Date** : 26/01/2026  

---  

## 🎯 Objectif  
Déployer vos modules personnalisés (ex : `saas_superadmin`, `saas_tenant_guard`) sur **Odoo.sh** en mode **multi‑tenant**, tout en suivant les meilleures pratiques de configuration, de tests et de gestion de l’infrastructure.

---  

## 📋 Checklist (à cocher au fur et à mesure)

- [ ] Créer le dépôt Git sur Odoo.sh (ou connecter un dépôt existant)  
- [ ] Organiser la branche `production` / `staging`  
- [ ] Ajouter les modules personnalisés au dépôt `custom_addons`  
- [ ] Mettre à jour les manifests (`__manifest__.py`)  
- [ ] Configurer les dépendances Python & Odoo (requirements.txt, pip)  
- [ ] Définir les paramètres d’Odoo (`ir.config_parameter`)  
- [ ] Valider le code (lint, tests unitaires)  
- [ ] Configurer les tests automatisés (GitHub Actions / Odoo.sh CI)  
- [ ] Déployer sur la branche `staging` (pré‑production)  
- [ ] Vérifier le bon fonctionnement multi‑tenant (création / suppression de clients)  
- [ ] Déployer sur la branche `production`  
- [ ] Activer la supervision & les alerts (Sentry, logs Odoo)  

---  

## 1️⃣ Pré‑requis  

| Élément | Version recommandée |
|---------|--------------------|
| Odoo | 19.0 (compatible avec votre code) |
| Python | 3.10+ |
| Git | 2.30+ |
| Odoo.sh account | ✅ |
| Accès aux branches `staging` & `production` | ✅ |
| Outils de CI (optionnel) | GitHub Actions, GitLab CI, ou Odoo.sh pipelines |

> **Note** : Odoo.sh utilise automatiquement un environnement Docker basé sur Odoo 19. Vous n’avez pas besoin de gérer vous‑même le Dockerfile, mais vous devez bien préciser vos dépendances.

---  

## 2️⃣ Structuration du dépôt  

Le dépôt doit contenir :  

```
/custom_addons/          ← votre répertoire d’addons (déjà présent)
    /saas_superadmin/
    /saas_tenant_guard/
/requirements.txt        ← dépendances Python (ex. psycopg2, lxml, …)
.gitignore               ← ignore les fichiers temporaires, logs, etc.
README.md                ← doc générale du projet
deployment.md            ← ce guide
```

### 2.1 `requirements.txt` (exemple)

```txt
# Odoo 19 dependencies
odoo==19.0
psycopg2-binary>=2.9
lxml>=4.9
# Ajoutez vos libs personnalisées ici
```

### 2.2 Manifest (`__manifest__.py`)  

Assurez‑vous que chaque module possède :  

```python
{
    'name': 'SAAS Superadmin',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Gestion multi‑tenant',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/saas_pack_views.xml',
        # … tous vos fichiers XML
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

> **Bonnes pratiques**  
> * Utilisez des **versions sémantiques** (`1.0.0`).  
> * Placez les fichiers de données (`data/*.xml`) avant les vues (`views/*.xml`).  
> * Ajoutez un `license` (ex. `LGPL-3`) et un `author`.

---  

## 3️⃣ Configuration Odoo.sh  

1. **Créer le projet** sur Odoo.sh → “New Project”.  
2. **Lier le dépôt** (GitHub, GitLab ou Bitbucket).  
3. **Définir les branches**  
   - `staging` → pré‑production (test des nouvelles versions).  
   - `production` → version stable.  

4. **Configurer le répertoire `custom_addons`** dans les **Settings → Addons** d’Odoo.sh :  
   - Ajouter le chemin `custom_addons` comme répertoire **extra addons**.  

5. **Variables d’environnement** (dans **Settings → Environment Variables**) :  

| Variable | Exemple | Description |
|----------|---------|-------------|
| `ODOO_RC` | `odoo.conf` | Fichier de configuration Odoo (si vous avez besoin de paramètres custom). |
| `PYTHONPATH` | `/opt/odoo/custom_addons` | Pour que Python trouve vos modules. |

---  

## 4️⃣ Bonnes pratiques de **développement & tests**  

1. **Lint & format**  
   - `pylint` ou `flake8` sur vos modules.  
   - `black` pour le formatage automatique.  

2. **Tests unitaires** (`unittest`, `pytest`)  
   - Placez les tests sous `tests/` dans chaque addon.  
   - Exemple :

```bash
python -m unittest discover -s addons/saas_superadmin/tests
```

3. **Tests d’intégration** (création d’un tenant)  
   - Utilisez les **wizards** déjà fournis (`saas_create_tenant`) dans des scripts Python ou via l’API RPC.  

4. **CI sur Odoo.sh**  
   - Odoo.sh exécute automatiquement les tests déclarés dans `tests/`.  
   - Vous pouvez ajouter un **GitHub Action** qui lance `odoo-bin -d test -i <addons>` pour valider avant le push.  

5. **Gestion des migrations** (`ir.model.data`)  
   - Utilisez les **`_sql_constraints`** pour garantir l’unicité.  
   - Mettez à jour les fichiers XML de données avec des **`noupdate="1"`** quand les données ne doivent pas être ré‑installées.  

---  

## 5️⃣ Déploiement sur la branche **staging** (pré‑production)

```bash
# 1️⃣ Commiter vos changements
git add .
git commit -m "Ajout modules SAAS + configs"

# 2️⃣ Pousser sur la branche staging
git push origin staging
```

Odoo.sh va automatiquement :

- Installer les dépendances (`requirements.txt`).  
- Installer les modules déclarés dans `custom_addons`.  
- Exécuter les tests présents dans chaque addon.  

### Vérifications post‑déploiement  

- Accédez à l’interface web de la branche `staging` (URL fournie par Odoo.sh).  
- Testez la création d’un **tenant** via le wizard `saas_create_tenant`.  
- Vérifiez les logs (`/var/log/odoo/odoo.log`) pour toute erreur.  

---  

## 6️⃣ Déploiement sur **production**  

Une fois les tests réussis :

```bash
git checkout production
git merge staging   # ou rebase, selon votre stratégie Git
git push origin production
```

Odoo.sh redéploiera la branche `production`.  

### Points de contrôle finaux  

- **Performance** – utilisez le module `web_profiler` ou `odoo benchmark`.  
- **Sécurité** – activez le **TLS** et vérifiez les **permissions** des groupes (`security/groups.xml`).  
- **Sauvegarde** – planifiez des sauvegardes automatiques via l’interface Odoo.sh.  

---  

## 7️⃣ Supervision & maintenance  

| Outil | Usage |
|------|------|
| **Sentry** | Capture des exceptions côté serveur. |
| **Odoo logs** | `/var/log/odoo/odoo.log` (consultable dans Odoo.sh UI). |
| **Cron monitoring** | Vérifiez les jobs dans `ir.cron` (ex. `saas_pack_data.xml`). |
| **Alertes** | Configurez des notifications Slack/Email via Odoo.sh → Settings → Alerts. |

---  

## 📂 Chemin des addons dans `odoo.conf`

Dans votre configuration locale (et sur Odoo.sh si vous utilisez un fichier de configuration), indiquez le répertoire contenant vos addons :

```ini
[options]
addons_path = C:\Users\HHPP\Desktop\odoo19\server\custom_addons\addons;C:\Users\HHPP\Desktop\odoo19\odoo\addons
```

**Vérification** : le premier chemin pointe exactement vers le répertoire `custom_addons\addons` que vous avez indiqué ; le second correspond au répertoire standard des addons Odoo. Cette configuration est donc correcte pour charger vos modules personnalisés ainsi que les addons de base.

Le point‑virgule sépare plusieurs chemins sous Windows. Ainsi Odoo chargera vos modules `saas_superadmin` et `saas_tenant_guard` situés dans `custom_addons\addons`.

---  

## 📧 Configuration des e‑mails (bonnes pratiques)

1. **Configurer le serveur SMTP** dans le menu *Paramètres → Technique → Paramètres de messagerie* ou via le fichier `odoo.conf` :

```ini
smtp_server = smtp.votreprovider.com
smtp_port = 587
smtp_user = votre.email@domaine.com
smtp_password = votre_mot_de_passe
smtp_ssl = True   # ou smtp_starttls = True selon le serveur
```

2. **Définir les paramètres par défaut** (`mail.default.from`, `mail.default.reply_to`) via *Paramètres → Technique → Paramètres* ou `ir.config_parameter`.  

3. **Faire les tests** :  
   - Créez un utilisateur de test et envoyez un mail depuis l’interface.  
   - Vérifiez les logs (`/var/log/odoo/odoo.log`) pour détecter d’éventuelles erreurs de connexion.

4. **Bonnes pratiques** :  
   - **Déployer d’abord le code** (modules) sur la branche `staging`.  
   - **Valider que les e‑mails fonctionnent** en environnement de pré‑production avant de passer en `production`.  
   - **Conserver les informations d’authentification sensibles** dans des variables d’environnement plutôt que dans `odoo.conf` en clair.

En suivant cet ordre, vous vous assurez que votre instance Odoo fonctionne correctement avant d’exposer le service en production.

---  

## 📚 Ressources complémentaires  

- [Documentation officielle Odoo.sh](https://www.odoo.com/documentation/19.0/applications/general/setup/odoo_sh.html)  
- [Guide Multi‑tenant Odoo (SAAS)](https://github.com/odoo/odoo/wiki/Multitenant-Setup)  
- [Best Practices Odoo Development](https://www.odoo.com/documentation/19.0/developer/)  

---  

*Ce guide est à adapter en fonction de vos spécificités de projet (nom du dépôt, modules additionnels, workflow Git). En suivant ces étapes, vous assurez un déploiement fiable, sécurisé et facilement ré‑versable sur Odoo.sh.*  

<task_progress>
- [x] Créer le fichier deployment.md avec le guide complet
- [x] Ajouter les sections sur le chemin des addons et la configuration des e‑mails
- [ ] Vérifier l’exactitude du contenu avec le client
</task_progress>
</write_to_file>