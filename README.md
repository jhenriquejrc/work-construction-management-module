# Work Construction Management Module

Odoo 19.0 module for managing construction projects, properties, stages, and documents.

## Prerequisites

### Docker Compose Environment
- Docker and Docker Compose installed
- Odoo 19.0 container running
- PostgreSQL database container accessible
- Containers defined in `odoo-dev/docker-compose.yaml`

### Addons Path Configuration
The module must be placed in a directory that's mapped to Odoo's addons path in the Docker Compose configuration.

**Current setup:**
- Module location: `/home/mrrobot/development/jhenriquejrc/datasheep/work-construction-management`
- Expected addons path mount in docker-compose.yaml should include the `datasheep` directory

## Installation

### 1. Verify Module is in Addons Path

Check that the `datasheep` folder containing this module is mounted as an Odoo addons path:

```bash
cd /home/mrrobot/development/jhenriquejrc/odoo-dev
grep -A 5 "addons" docker-compose.yaml
```

The configuration should include a volume mount like:
```yaml
volumes:
  - ../datasheep:/mnt/extra-addons/datasheep
```

### 2. Start Odoo Docker Compose Stack

```bash
cd /home/mrrobot/development/jhenriquejrc/odoo-dev
docker compose --env-file=.env up
```

Or use the VS Code task: "Start Odoo (Docker Compose)"

### 3. Install the Module

**Option A: Via Odoo Web Interface**
1. Navigate to `http://localhost:8069` (or configured port)
2. Log in with admin credentials
3. Go to Apps menu
4. Click "Update Apps List" (may need to enable Developer Mode first)
5. Search for "Work Construction Management"
6. Click "Install"

**Option B: Via Odoo CLI**
```bash
docker exec -it <odoo_container_name> odoo-bin -d <database_name> -i work_construction_management --stop-after-init
```

Replace:
- `<odoo_container_name>`: Name of your Odoo container (check with `docker ps`)
- `<database_name>`: Name of your Odoo database

### 4. Verify Installation

After installation completes, check:
- No fatal errors in the Odoo logs
- Module appears in Apps list with "Installed" status
- "Work Management" menu appears in the backend navigation

## Smoke Testing

### Test Checklist

1. **Login**: Access Odoo backend with an authorized user account
2. **Navigate to module menu**: Click "Work Management" in the main menu
3. **Test Properties**:
   - Click "Properties" submenu
   - Verify the tree/list view loads without errors
   - Click "Create" and add a new property
   - Fill in Name, Start Date, End Date, Description
   - Save the record and verify form view renders correctly
4. **Test Stages**:
   - Click "Stages" submenu
   - Verify list view with sequence handle
   - Create a new stage
5. **Test Documents**:
   - Click "Documents" submenu
   - Verify list view loads
   - Create a new document with name and date

### Expected Results
✓ All menus visible and accessible  
✓ List/tree views render without exceptions  
✓ Form views render without exceptions  
✓ Records can be created and saved  
✓ Models appear in ORM registry (verify with Developer Mode → Technical → Models)

## Troubleshooting

### Common Failure Categories

| Issue Type | Symptoms | Where to Check |
|------------|----------|----------------|
| **Manifest Errors** | Module doesn't appear in Apps list | Odoo container logs, check manifest syntax |
| **ACL Issues** | "Access Denied" errors when opening views | `security/ir.model.access.csv`, verify user groups |
| **XML Parse Errors** | View not loading, error on module install | Odoo logs, check XML syntax in view files |
| **Import Failures** | Module install fails with Python errors | Container logs, check model imports in `__init__.py` |
| **Missing Dependencies** | Module install blocked | Manifest `depends` list, ensure base modules installed |

### Finding Odoo Container Logs

**View real-time logs:**
```bash
docker logs -f <odoo_container_name>
```

**Search for errors:**
```bash
docker logs <odoo_container_name> 2>&1 | grep -i error
docker logs <odoo_container_name> 2>&1 | grep -i "work.construction"
```

### Common Log Locations
- Container stdout/stderr: `docker logs`
- Odoo log file (if configured): Check volume mounts in docker-compose.yaml

### Rollback Procedure

If module installation fails or causes issues:

1. **Uninstall via Web Interface**:
   - Go to Apps → Find "Work Construction Management"
   - Click Uninstall
   - Confirm removal

2. **Manual Removal** (if web interface unavailable):
   ```bash
   docker exec -it <odoo_container_name> odoo-bin -d <database_name> -u work_construction_management --stop-after-init
   ```

3. **Remove from Addons Path** (last resort):
   - Stop Odoo containers: `docker compose down`
   - Remove or rename the module directory
   - Restart containers: `docker compose up`

4. **Database Reset** (nuclear option):
   - Drop and recreate the database
   - Restart with fresh install

## Module Structure

```
work-construction-management/
├── __init__.py              # Root package init
├── __manifest__.py          # Module metadata and dependencies
├── README.md                # This file
├── models/                  # Business models
│   ├── __init__.py
│   ├── work_property.py     # Property model
│   ├── work_stage.py        # Stage model
│   └── work_document.py     # Document model
├── views/                   # UI definitions
│   ├── work_property_views.xml
│   ├── work_stage_views.xml
│   ├── work_document_views.xml
│   ├── menu_views.xml       # Menu structure
│   └── portal_templates.xml # Portal templates (optional)
├── security/                # Access control
│   ├── security.xml         # Security groups
│   └── ir.model.access.csv  # Model access rights
├── data/                    # Seed data (optional)
├── controllers/             # Web controllers (optional)
└── tests/                   # Automated tests (optional)
```

## Dependencies

- `base`: Odoo core module (required)
- `portal`: Portal functionality (optional)
- `website`: Website integration (optional)

## Version

- **Odoo Version**: 19.0
- **Module Version**: 19.0.1.0.0

## Development

### Adding New Models
1. Create model file in `models/`
2. Add import in `models/__init__.py`
3. Create views in `views/`
4. Add access rights in `security/ir.model.access.csv`
5. Register new files in `__manifest__.py` data list (security before views)
6. Upgrade module: `-u work_construction_management`

### Updating Existing Module
```bash
docker exec -it <odoo_container_name> odoo-bin -d <database_name> -u work_construction_management --stop-after-init
```

## License

Specify your license here (e.g., LGPL-3, MIT, etc.)
