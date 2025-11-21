# DigTool - OSINT Email Verification Tool

DigTool est un outil OSINT modulaire et multithreadé permettant de vérifier la présence d'une adresse email sur différents services publics.

## Fonctionnalités


## Installation

### Depuis le code source

```bash
# Cloner le repository
git clone https://github.com/l0uishp/digtool.git
cd digtool

# Installer les dépendances
pip3 install -r requirements.txt

# Installer le package
pip3 install .
```

### Installation en mode développement

```bash
pip3 install -e .
```

## Utilisation

### Commande de base

```bash
digtool email@example.com
```

### Exemples

```bash
# Scan simple
digtool john.doe@example.com

# Scan verbose avec configuration personnalisée
digtool john.doe@example.com -v -c my_config.json

# Scan avec module spécifique
digtool john.doe@example.com -m gravatar
```

## Configuration

Le fichier `config.json` permet de personnaliser le comportement de DigTool :

```json
{
  "timeout": 10,
  "rate_limit": 1.0,
  "user_agent": "DigTool/1.0 (OSINT Scanner)",
  "modules": ["gravatar", "site_template"],
  "max_workers": 5,
  "verbose": false
}
```

### Paramètres

- **timeout** : Délai d'attente pour les requêtes HTTP (secondes)
- **rate_limit** : Pause entre requêtes (secondes)
- **user_agent** : User-Agent pour les requêtes HTTP
- **modules** : Liste des modules à exécuter
- **max_workers** : Nombre de threads parallèles
- **verbose** : Active les logs détaillés

## Architecture du projet

```
digtool/
├── digtool/
│   ├── __init__.py          # Package principal
│   ├── __main__.py          # Point d'entrée
│   ├── cli.py               # Interface ligne de commande
│   ├── core.py              # Logique principale
│   ├── config.py            # Gestion configuration
│   ├── logger.py            # Système de logging
│   └── modules/
│       ├── __init__.py      # Chargement modules
│       ├── base.py          # Classe de base
│       ├── gravatar.py      # Module Gravatar
│       └── site_template.py # Template pour nouveaux modules
├── config.json              # Configuration par défaut
├── setup.py                 # Installation package
├── pyproject.toml           # Configuration moderne Python
├── requirements.txt         # Dépendances
└── README.md               # Documentation
```

## Modules inclus

### Gravatar
Vérifie si l'email possède un profil Gravatar.

### SiteTemplate
Module template montrant comment interroger un site web.
