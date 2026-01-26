import odoorpc
import getpass

# Configuration du Super Admin
ODOO_HOST = 'localhost'
ODOO_PORT = 8069
SUPER_ADMIN_USER = 'admin' # Le master password ou admin par défaut
DEFAULT_DB_PASSWORD = 'admin' # Mot de passe admin par défaut des nouveaux DB

def create_tenant_and_assign_pack(dbname, pack_ref_xml_id):
    print(f"--- Provisioning pour {dbname} ---")
    
    # 1. Connexion au serveur (Super Admin / List DB)
    try:
        odoo = odoorpc.ODOO(ODOO_HOST, port=ODOO_PORT)
    except Exception as e:
        print(f"Erreur de connexion au serveur Odoo : {e}")
        return

    # Vérifier si odoorpc est installé (pip install odoorpc)
    # Sinon, on utilise une méthode alternative ou l'interface web.
    # Pour ce guide, nous supposons que le DB est créé via l'interface web standard 
    # car créer une DB via RPC requiert des droits super-avancés.
    
    # Cependant, une fois la base créée, nous pouvons l'initialiser automatiquement :
    try:
        # Connexion à la base cible
        db = odoorpc.ODOO(ODOO_HOST, port=ODOO_PORT, database=dbname, login='admin', password=DEFAULT_DB_PASSWORD)
        
        # 2. Installer le module 'saas_pack_manager'
        print("Installation du module gestionnaire de pack...")
        if 'saas_pack_manager' not in db.env['ir.module.module'].search([]).mapped('name'):
            db.env['ir.module.module'].search([('name', '=', 'saas_pack_manager')]).button_immediate_install()
            print("Module installé. Veuillez ré-exécuter ce script après le redémarrage d'Odoo.")
            return

        # 3. Trouver l'ID du pack via son XML ID
        pack_xml_id = f'saas_pack_manager.{pack_ref_xml_id}'
        try:
            pack_id = db.env.ref(pack_xml_id).id
        except ValueError:
            print(f"Erreur : Le pack {pack_ref_xml_id} n'existe pas.")
            return

        # 4. Mettre à jour la configuration
        config = db.env['res.config.settings'].create({})
        config.write({'active_pack_id': pack_id})
        
        # 5. Exécuter l'activation
        print(f"Activation du pack : {pack_ref_xml_id}...")
        config.action_activate_pack()
        
        print(f"Succès ! Le tenant {dbname} est configuré.")

    except Exception as e:
        print(f"Erreur lors de la configuration : {e}")

if __name__ == "__main__":
    print("=== Odoo SaaS Super Admin Tool ===")
    db_name = input("Nom de la nouvelle base (ex: client2_agro) : ")
    print("Choix du Pack :")
    print("1. Agro - Usine Connectée")
    print("2. Agro - Distribution")
    print("3. Agro - Export")
    print("4. Logistique - Performance Flotte")
    print("5. Immobilier - Gestion")
    
    choice = input("Entrez le numéro du pack : ")
    pack_map = {
        '1': 'pack_agro_usine',
        '2': 'pack_agro_dist',
        '3': 'pack_agro_export',
        '4': 'pack_log_fleet',
        '5': 'pack_immo_gest',
    }
    
    if choice in pack_map:
        # Note: Assurez-vous que la base de données existe déjà avant de lancer ce script
        # (Créez-la via http://localhost:8069/web/database/manager)
        confirm = input(f"La base '{db_name}' existe-t-elle déjà ? (y/n) : ")
        if confirm.lower() == 'y':
            create_tenant_and_assign_pack(db_name, pack_map[choice])
        else:
            print("Créez d'abord la base via le gestionnaire de base de données Odoo, puis relancez ce script.")
    else:
        print("Choix invalide.")