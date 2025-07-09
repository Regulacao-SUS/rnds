![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rnds)
![GitHub License](https://img.shields.io/github/license/Regulacao-SUS/rnds)
![GitHub branch status](https://img.shields.io/github/checks-status/Regulacao-SUS/rnds/main)
![PyPI - Downloads](https://img.shields.io/pypi/dm/rnds)
![Codecov](https://img.shields.io/codecov/c/github/Regulacao-SUS/rnds)

# rnds

Pacote Python para integração com recursos RNDS e RIRA.

## Instalação

```bash
pip install navi-rnds
```

## Uso Básico

```python
from rnds import Rnds
from rnds.rira import Rira

# Exemplo de uso
rnds = Rnds(token="seu_token")
rira = Rira(token="seu_token")

# Utilize os métodos disponíveis
```

## Testes

Execute os testes com:

```bash
pytest
```

## Publicação no PyPI

1. Gere a distribuição:
   ```bash
   python -m build
   ```
2. Faça upload para o PyPI:
   ```bash
   twine upload dist/*
   ```

## Contribuição

Pull requests são bem-vindos!

## Licença

[MIT](LICENSE)
