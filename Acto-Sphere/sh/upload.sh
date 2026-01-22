#!/bin/bash
echo "Initiating Cloud Sync..."
echo "Compressing Vault..."
tar -czf vault_backup.tar.gz ../vault_storage/
echo "Uploading vault_backup.tar.gz to Remote Server..."
sleep 2
echo "Sync Complete! (Mock)"
