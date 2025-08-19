#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -------------------------------------------
# SCRIPT: backup_clickdom.sh
# Description: Sauvegarde horodatée du projet Clickdom
# Location: ~/Documents/DevIA/Clickdom/scripts
# Modes: copy (par défaut) ou tar
# Nettoyage automatique des sauvegardes > 30 jours
# -------------------------------------------

# Chemin du projet Clickdom
PROJET_DIR="$HOME/Documents/DevIA/Clickdom"
# Dossier de sauvegarde
BACKUP_BASE="$HOME/Documents/backups/clickdom"
# Mode de sauvegarde: 'copy' ou 'tar'
METHODE=${1:-copy}
# Durée de rétention (jours)
RETENTION_DAYS=30

# Création du dossier de sauvegarde
mkdir -p "$BACKUP_BASE"

# Vérification du répertoire projet
if [[ ! -d "$PROJET_DIR" ]]; then
  echo "❌ ERREUR : Répertoire projet introuvable : $PROJET_DIR" >&2
  exit 1
fi

# Horodatage
TIMESTAMP=$(date +'%Y-%m-%d_%Hh%M')

echo "🚀 Démarrage de la sauvegarde Clickdom ($METHODE) à $TIMESTAMP"

if [[ "$METHODE" == "tar" ]]; then
  ARCHIVE="$BACKUP_BASE/clickdom_backup_${TIMESTAMP}.tar.gz"
  echo "📦 Création de l’archive compressée…"
  tar czf "$ARCHIVE" -C "$PROJET_DIR" .
  echo "✅ Archive créée : $ARCHIVE"
else
  DEST="$BACKUP_BASE/backup_${TIMESTAMP}"
  echo "📋 Copie simple du projet…"
  mkdir -p "$DEST"
  cp -a "$PROJET_DIR/." "$DEST/"
  echo "✅ Copie effectuée dans : $DEST"
fi

# Nettoyage automatique
echo "🧹 Suppression des sauvegardes > $RETENTION_DAYS jours…"
# Fichiers tar.gz
find "$BACKUP_BASE" -maxdepth 1 -type f -name '*.tar.gz' -mtime +${RETENTION_DAYS} -print -exec rm {} \\;
# Dossiers backup_*
find "$BACKUP_BASE" -maxdepth 1 -type d -name 'backup_*' -mtime +${RETENTION_DAYS} -print -exec rm -r {} \\;

echo "🎉 Sauvegarde terminée à $TIMESTAMP"