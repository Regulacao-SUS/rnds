![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rnds)
![GitHub branch status](https://img.shields.io/github/checks-status/Regulacao-SUS/rnds/main)
![PyPI - Downloads](https://img.shields.io/pypi/dm/rnds)
![Codecov](https://img.shields.io/codecov/c/github/Regulacao-SUS/rnds)
[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

Esta obra tem a [licença Creative Commons Atribuição-CompartilhaIgual 4.0
Internacional][cc-by-sa].

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/deed.fr
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg

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
