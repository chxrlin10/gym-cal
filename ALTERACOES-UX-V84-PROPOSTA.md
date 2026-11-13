# Gym.cal — proposta v84 UX, baseada na v83

## O que foi realmente editado

Todas as alterações estão em `index.html`, limitadas ao layout da aba **Hoje** e a estilos pontuais. O restante do projeto foi preservado da v83.

1. **Treino mais fácil de encontrar.** O card existente `Seu treino de hoje` foi movido para logo depois dos macronutrientes; segue abrindo a aba Treino com a mesma lógica e dados anteriores.
2. **Registrar alimento mais rápido.** O botão existente `Adicionar alimento`, que aparecia depois dos quatro cards de refeições, foi movido para imediatamente antes da lista. Mantém `amSet(mi)` e escolha da refeição conforme a hora.
3. **Menos cartões competindo por atenção.** O atalho duplicado de sequência/rank foi colocado na seção expansível `Sequência e rank`. Dados continuam acessíveis pela aba Progresso.
4. **Convite de conta agrupado.** O convite para criar/conectar conta foi colocado na seção expansível `Conta e sincronização`, sem alterar autenticação ou função do convite.
5. **Pequenos ajustes de UX/CSS.** Botão de alimento com alvo de toque de 52px, foco visível e correções de espaçamento em telas pequenas.

## Fora do escopo (não alterado)

- Cálculos de calorias, macros, dieta e alimentos.
- Rotinas, estilos de treino, exercícios, histórico e cargas.
- Pontos, ranks, sequência, limites e penalidades.
- Supabase, sincronização, conta, backups, RLS e pagamentos.
- Arquivos nativos, pipeline Android e demais módulos.

## Verificações realizadas

- `node tests/app.test.cjs`: **32 testes passaram** (DOM simulado).
- `npm test`: interrompido no início de `tests/server.test.cjs` por falta do pacote `esbuild` neste ambiente. **Não declarar** a suíte integral aprovada.
- **Ainda não** testado visualmente em Android real, nem com Supabase real.

## Checklist para Claude após integrar

- Comparar v83 e esta proposta visualmente em 320, 360, 390 e 430px, e em tema claro/escuro.
- Confirmar que o card de treino e o botão Registrar alimento estão no local esperado.
- Confirmar que o botão abre a refeição correta e que alterar a data não quebra o comportamento existente.
- Expandir `Sequência e rank` e `Conta e sincronização` e verificar todos os botões.
- Testar registro de alimentos, exercícios, dados e sincronização sem regressões.
- Executar `npm ci && npm test` em ambiente com dependências e os testes de navegador/Android aplicáveis.

## Como integrar

Este ZIP é um **projeto completo** com modificações, não um mero trecho de código. Comparar o `index.html` com o da v83 e integrar cuidadosamente, sem sobrescrever mudanças mais recentes feitas depois do upload.
