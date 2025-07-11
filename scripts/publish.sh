#!/bin/bash
set -euo pipefail

# Função para extrair valores do pyproject.toml
get_pyproject_value() {
    uv run python -c "from tomllib import loads; print(loads(open('pyproject.toml', 'r').read())['project']['$1'])"
}

# Função robusta para verificar versão no PyPI
check_pypi_version() {
    local package=$1
    local version=$2
    local attempts=3
    local delay=5

    for ((i=1; i<=attempts; i++)); do
        echo "   Tentativa $i/$attempts de verificação..."
        
        # Processa a saída específica do uvx pip index versions
        if uvx pip index versions "$package" 2>/dev/null | \
           grep -A1 "Available versions:" | \
           grep -oE "\b${version//./\\.}\b" | \
           grep -q .; then
            return 0
        fi
        
        if [ $i -lt $attempts ]; then
            echo "   Versão não encontrada, aguardando $delay segundos..."
            sleep $delay
        fi
    done
    
    return 1
}

# Verificar versão
echo "🔍 Verificando compatibilidade de versões..."
PYPROJECT_VERSION=$(get_pyproject_value "version")
PROJECT_NAME=$(get_pyproject_value "name")
TAG_VERSION="${GITHUB_REF#refs/tags/}"

if [ "$PYPROJECT_VERSION" != "$TAG_VERSION" ]; then
    echo "❌ Erro crítico:"
    echo "   Versão no pyproject.toml: $PYPROJECT_VERSION"
    echo "   Versão da tag de release: $TAG_VERSION"
    exit 1
fi
echo "✅ Versões compatíveis ($PYPROJECT_VERSION)"

# Build
echo "🏗️ Construindo pacote..."
uv build

# Publicar com autenticação explícita
echo "🚀 Publicando no PyPI..."
if [ -n "${UV_PYPI_TOKEN:-}" ]; then
    echo "   Usando token de autenticação..."
    uv publish --token "$UV_PYPI_TOKEN"
else
    echo "   Nenhum token encontrado, tentando publicação sem autenticação explícita..."
    uv publish
fi


# Verificação robusta da publicação
echo "🔍 Verificando publicação no PyPI..."
if check_pypi_version "$PROJECT_NAME" "$PYPROJECT_VERSION"; then
    echo "✅ Versão $PYPROJECT_VERSION encontrada no PyPI"
else
    echo "❌ Falha na verificação:"
    echo "   Versão $PYPROJECT_VERSION não encontrada para $PROJECT_NAME"
    echo "   Saída completa do uvx pip index versions:"
    uvx pip index versions "$PROJECT_NAME" || true
    echo "   Visite: https://pypi.org/project/$PROJECT_NAME"
    exit 1
fi