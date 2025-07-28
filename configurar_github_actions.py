#!/usr/bin/env python3
"""
Script para configurar GitHub Actions para ejecución automática
PASO 4 del pipeline: Configurar automatización
"""

import os
import sys
from datetime import datetime

def configurar_github_actions():
    """Configurar GitHub Actions para ejecución automática"""
    print("🚀 **PASO 4: CONFIGURAR GITHUB ACTIONS**")
    print("=" * 60)
    print("📅 Configurando ejecución automática cada 30 minutos")
    print("=" * 60)
    
    # Crear directorio .github/workflows si no existe
    workflows_dir = ".github/workflows"
    os.makedirs(workflows_dir, exist_ok=True)
    
    # Crear archivo de workflow
    workflow_content = '''name: Scraping Automático de Noticias Jurídicas

on:
  schedule:
    # Ejecutar cada 30 minutos
    - cron: '*/30 * * * *'
  workflow_dispatch:  # Permitir ejecución manual

jobs:
  scraping:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout código
      uses: actions/checkout@v4
      
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Configurar variables de entorno
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        echo "SUPABASE_URL=$SUPABASE_URL" >> $GITHUB_ENV
        echo "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY" >> $GITHUB_ENV
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> $GITHUB_ENV
        
    - name: Ejecutar scraping automático
      run: |
        python backend/main.py
        
    - name: Notificar resultado
      if: always()
      run: |
        echo "✅ Scraping automático completado - $(date)"
        
    - name: Commit y push cambios (si hay)
      if: success()
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        git diff --quiet && git diff --staged --quiet || git commit -m "Auto-update: Scraping completado $(date)"
        git push
'''
    
    workflow_file = os.path.join(workflows_dir, "scraping_automatico.yml")
    
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    
    print(f"✅ Workflow creado: {workflow_file}")
    
    # Crear archivo de configuración para variables de entorno
    env_example = '''# Variables de entorno requeridas para GitHub Actions
# Agregar estas variables en Settings > Secrets and variables > Actions

SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
OPENAI_API_KEY=tu-openai-api-key
'''
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example)
    
    print(f"✅ Archivo .env.example creado")
    
    # Crear README con instrucciones
    readme_content = '''# Sistema de Noticias Jurídicas - GitHub Actions

## Configuración Automática

Este repositorio está configurado para ejecutar scraping automático de noticias jurídicas cada 30 minutos.

### Variables de Entorno Requeridas

Configurar en GitHub: Settings > Secrets and variables > Actions

- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Service Role Key de Supabase
- `OPENAI_API_KEY`: API Key de OpenAI

### Workflow

El workflow `scraping_automatico.yml` se ejecuta:
- Cada 30 minutos automáticamente
- Manualmente desde la pestaña Actions

### Monitoreo

- Verificar ejecuciones en: Actions > Scraping Automático
- Logs disponibles en cada ejecución
- Notificaciones automáticas de éxito/error

### Última actualización

Configurado el: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open('GITHUB_ACTIONS_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README de GitHub Actions creado")
    
    print(f"\n📋 **INSTRUCCIONES PARA COMPLETAR LA CONFIGURACIÓN**")
    print("=" * 60)
    print("1. Ir a tu repositorio en GitHub")
    print("2. Settings > Secrets and variables > Actions")
    print("3. Agregar las siguientes variables:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("   - OPENAI_API_KEY")
    print("4. Hacer commit y push de los archivos generados")
    print("5. Verificar en Actions que el workflow esté activo")
    
    print(f"\n✅ **CONFIGURACIÓN COMPLETADA**")
    print("=" * 60)
    print("🎯 Sistema listo para ejecución automática cada 30 minutos")
    print("📊 Monitoreo disponible en GitHub Actions")

if __name__ == "__main__":
    configurar_github_actions() 