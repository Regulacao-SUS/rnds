![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rnds)
![GitHub branch status](https://img.shields.io/github/checks-status/Regulacao-SUS/rnds/main)
![PyPI - Downloads](https://img.shields.io/pypi/dm/rnds)
![Codecov](https://img.shields.io/codecov/c/github/Regulacao-SUS/rnds)
[![CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-sa/4.0/deed.pt)

# rnds

Pacote Python para integração com recursos RNDS e RIRA.

## Instalação

```bash
pip install rnds
```

## Uso Básico

```python
from rnds import RNDS
from rnds.rira.rira import RIRA
```

# Exemplo de uso

Veja exemplos de:
* Implementação de serviços [RIRA_pending](exemplos/exemplo_rira_pending.py)
* Implementação de serviços [CFM](exemplos/exemplo_cfm.py)
* Implementação de serviços [RNDS](exemplos/exemplo_rnds.py)

# Utilize os métodos disponíveis

## Testes

Execute os testes com:

```bash
pytest --cov=rnds --cov-report=term-missing
```

## Publicação no PyPI

1. Gere a distribuição:
   ```bash
   uv build
   ```
2. Faça upload para o PyPI:
   ```bash
   uv publish
   ```

## Contribuição

Pull requests são bem-vindos!

## Licença

<<<<<<< HEAD
<<<<<<< HEAD
Esta obra tem a [Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional](http://creativecommons.org/licenses/by-sa/4.0/deed.pt).

=======

=======
>>>>>>> fde9ea3 (rebase from main)
Esta obra tem a [Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional](http://creativecommons.org/licenses/by-sa/4.0/deed.pt).

>>>>>>> 6d1ab9b (fix: correção do readme)
[![CC BY-SA 4.0](https://licensebuttons.net/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/deed.pt)
