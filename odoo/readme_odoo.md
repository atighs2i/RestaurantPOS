# Restaurant POS Odoo module and Docker compose

This folder contains a lightweight Odoo module scaffold (restaurant_pos_custom) and a docker-compose file to run an Odoo 16 development instance.

Quick start:
1. Ensure Docker and docker-compose are installed.
2. From repository root run:
   docker-compose -f docker-compose-odoo.yml up -d
3. Open http://localhost:8069 and create a new Odoo database. In Apps enable "Developer mode" and update apps list, then install the "restaurant_pos_custom" module from the Extra Addons path.

Notes:
- The module is a starting point: models for orders and recipes, basic views, i18n placeholders for Arabic and French, and simple RTL CSS.
- You should install required Odoo modules (point_of_sale, stock) in the database.
- To make the addon visible, ensure the folder ./odoo/addons is mounted as extra-addons (docker-compose sets this path).
