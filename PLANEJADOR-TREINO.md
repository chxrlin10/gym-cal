# Planejador de treino do Gym.cal (v90)

Sistema **determinístico**: a mesma avaliação gera sempre o mesmo plano. Não usa IA generativa, sorteio, data nem rede. Cada escolha tem um motivo que aparece em Perfil › Preferências de treino › **Por que este plano?**.

É **opcional**. Quem não escolher "Pela minha avaliação" continua com o plano de sempre, idêntico ao da v89 (`tests/navegador/planos_v89.json` guarda uma impressão digital de 360 planos para provar isso).

## Onde está no código (`index.html`)

| O quê | Onde |
|---|---|
| Metadados dos exercícios | `EXM` (padrão de movimento, equipamento, nível, regiões). O catálogo `EX` não mudou. |
| Leitura segura da avaliação | `avOf(p)`: normaliza `p.av`, nunca confia no que foi salvo. |
| Regras e motor | `avSplit`, `avRr`, `PLN(p)` |
| Encaixe no plano atual | `plansFor(p)`: só usa o motor se `p.av.on`, não há "Minha rotina" e o estilo é Automático. |
| Tela | `avUI(p,o)` dentro de "Preferências de treino"; gravação em `saveP()`. |

`p.av` fica dentro do perfil, então sincroniza, entra no backup e na restauração como qualquer outro campo. Nenhuma migração de banco.

## Avaliação (`p.av`)

- `on`: liga o planejador.
- `g`: objetivo do treino: `hip` (ganhar massa), `for` (força), `sau` (saúde e condicionamento).
- `pr`: até 2 músculos prioritários. Sem escolha, o "Foco em pernas e glúteo" antigo vale como prioridade em Glúteos e Quadríceps.
- `dur`: 30, 45, 60 ou 90 minutos por treino.
- `eq`: equipamentos (B barra, H halter, M máquina, P polia, N banco, F barra fixa e paralelas). `null` = padrão do local. Peso do corpo (W) sempre existe.
- `ex`: exercícios a evitar.
- `lim`: regiões com dor ou limitação: ombro, cotovelo/punho, lombar, joelho, quadril.
- `cu`: "tenho condição de saúde, sintoma ou dor que um profissional pediu cuidado".
- Dias e experiência vêm de `p.days` e `p.exp`, que já existiam.

## Regras

1. **Divisão** (`avSplit`), por dias, nível e objetivo:
   - 2 dias: corpo inteiro ×2.
   - 3 dias: corpo inteiro ×3; ou Superior / Inferior / Corpo inteiro para quem quer massa e não é iniciante.
   - 4 dias: Superior / Inferior ×2.
   - 5 dias: iniciante, Superior / Inferior ×2 + corpo inteiro; demais, Empurrar / Puxar / Pernas + Superior / Pernas.
   - 6 dias: iniciante, Superior / Inferior ×3; demais, Empurrar / Puxar / Pernas ×2.
2. **Volume semanal por músculo** (`VOLL`): séries por semana por nível (iniciante, intermediário, avançado), separado entre grandes grupos e músculos menores, por objetivo. Prioridade soma séries até o teto (`VOLC`). Costas recebem 2 séries a mais que o peito (4 no avançado) para equilibrar empurrar e puxar. Modo cuidadoso usa 75%.
3. **Contagem de séries** (`crd`): o 1º músculo principal conta 1 por série, os outros principais 0,5, e o trabalho indireto 0,5 nos grandes grupos e 0,25 nos menores. Assim o plano não deixa braço só no indireto.
4. **Escolha dos exercícios**: só entram exercícios disponíveis (equipamento, nível, limitações, lista de evitar). Em cada sessão não repete exercício nem variações do mesmo exercício (`VG`). Entre empates vale a ordem do catálogo (principais primeiro), preferindo o que ainda não apareceu na semana. "Variar treino" (`p.vr`) muda o desempate, como antes.
5. **Séries, repetições e descanso** (`avRr`) por objetivo e nível: força usa poucas repetições e descanso longo; massa usa faixas médias; saúde usa faixas altas e descanso curto.
6. **Duração**: estima o tempo da sessão (5 min de aquecimento + séries × (45 s + descanso)). Se passar, tira séries dos músculos que não são prioridade, protegendo puxar quando já está abaixo de empurrar. O aviso aparece no "Por que este plano?".
7. **Limites explicados**: se um músculo ficar sem exercício disponível, o plano diz isso em vez de inventar.

## Salvaguardas de saúde

- O app **não diagnostica nem recomenda tratamento**. Marcar uma região só tira exercícios que mais exigem dela.
- O modo cuidadoso usa menos séries, só exercícios de nível iniciante ou intermediário, repetições mais leves e mostra aviso para conversar com um profissional antes de treinar com carga.
- Com iniciante em 5 ou 6 dias, o plano avisa que 3 a 4 dias costumam render igual e mantém o volume baixo.
- As faixas de volume são princípios gerais de treinamento, não prescrição individual nem médica.

## Como estender

- **Novo exercício**: adicione em `EX` e uma linha em `EXM` (o teste falha se faltar).
- **Nova divisão**: um caso em `avSplit` e, se precisar, um tipo de sessão em `SES`.
- **Mudar volume**: `VOLL` / `VOLC` / `PRB`, e rode `tests/navegador/planejador.py`.

## O que ainda não existe (próximas versões)

Substituição por equivalente com pontuação (v91), registro de esforço e execução, média semanal de peso, medidas e força (v92), revisão periódica e detecção de recuperação (v93).
