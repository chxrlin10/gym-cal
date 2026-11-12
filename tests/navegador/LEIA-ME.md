# Testes de navegador (Chrome real)

Complementam o `npm test` (que usa DOM simulado). Abrem o `index.html` no Chrome e clicam na interface.

Requisitos: Python 3 e Playwright (`pip install playwright` e `playwright install chromium`, ou um Chrome instalado).

```
python3 tests/navegador/premium_v79.py        # receitas, troca de alimento, revisão, último treino, persistência, perfis, backup, expiração
python3 tests/navegador/assinatura.py         # tela de assinatura com a loja simulada (cobrança ligada só numa cópia temporária)
python3 tests/navegador/sequencia_e_limites.py # card diário da sequência, aviso de gasto alto, limite do cardio
```

Cada teste termina com `FALHAS: []` quando tudo passa. Para testar outro arquivo: `GYMCAL_HTML=/caminho/index.html python3 ...`.
Não substituem teste em celular real, compra pela Google Play nem Supabase de produção.
