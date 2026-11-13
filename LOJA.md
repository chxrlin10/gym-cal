# Gym.cal — publicação na Google Play

## Textos da loja
**Nome:** Gym.cal: calorias e treino
**Descrição curta (80):** Meta de calorias, diário de comida e treino por série, tudo em um app.
**Descrição completa:**
O Gym.cal calcula sua meta diária de calorias pelo seu corpo e rotina, e sugere treinos para você: na academia ou em casa, de 2 a 6 dias por semana.
- Registre refeições em medidas do dia a dia (colher, fatia, unidade) com mais de 950 alimentos e leitor de código de barras
- Treino com demonstração animada e músculos trabalhados de cada exercício
- Foco opcional em pernas e glúteo
- Registro por série, com sugestão de progressão e recordes
- Calorias gastas no treino e no cardio (opcional) somadas à sua meta
- Peso, água, suplementos e dicas de alimentação
- Perfis para mais de uma pessoa no mesmo aparelho
- Conta na nuvem opcional, para backup
Estimativas por fórmulas conhecidas. Não é um dispositivo médico e não diagnostica, trata, cura ou previne doenças. Consulte um profissional de saúde para orientação, diagnóstico ou tratamento. Não substitui médico ou nutricionista. Para maiores de 18 anos.

**Categoria:** Saúde e fitness · **Classificação:** Livre · **Preço:** grátis, com assinatura Premium opcional (compras no app)
**Política de privacidade:** https://chxrlin10.github.io/gym-cal/privacidade.html
**Página de exclusão de conta:** https://chxrlin10.github.io/gym-cal/excluir-conta.html
**Termos de uso:** https://chxrlin10.github.io/gym-cal/termos.html
**Segurança dos dados (Play Console):** coleta e-mail, dados de saúde/fitness (opcional, com conta) e histórico de compras (se assinar); compras processadas pela Google Play e confirmadas pelo RevenueCat; não vende nem usa para anúncios; criptografado em trânsito; usuário pode pedir exclusão.

## Preparação v77
1. Executar e verificar Supabase conforme `supabase/EXECUTAR.md`.
2. Publicar páginas legais e recuperar-senha.html em URL pública; verificar sem login e em outra rede.
3. GitHub Actions usa Node22, Java21 e API36. `npm ci` instala versões travadas no lockfile. APK debug é o padrão.
4. Para AAB, executar manualmente com release=true. Configurar variável RC_PUBLIC_KEY e secrets ANDROID_KEYSTORE_BASE64, ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_ALIAS e ANDROID_KEY_PASSWORD. Nunca enviar a chave de assinatura para o repositório. Guardar cópia segura dela.
5. `ANDROID_VERSION_CODE` usa github.run_number: garantir que é maior que o último publicado; se mudar workflow/repositório, ajustar antes do upload.
6. AAB não foi compilado aqui: download do Gradle bloqueado pela rede do ambiente. Rodar Actions e conferir Pre-launch report; testar Android físico e compras em faixa interna.
7. Preencher declaração de saúde, Segurança dos dados (incluindo todos os perfis enviados e compras) e público-alvo 18+. Classificação indicativa vem do questionário, não de escrever “Livre” neste arquivo.
8. Se a conta pessoal estiver sujeita à exigência, completar teste fechado com 12 testadores por 14 dias contínuos e solicitar produção.
9. Preparar credenciais/instruções de acesso para revisão e imagens da loja. O ícone nativo usa o símbolo vetorial do favicon existente; confira visualmente no aparelho e gere material de loja em alta resolução.

Fontes para conferência antes de submeter:
- https://support.google.com/googleplay/android-developer/answer/11926878
- https://support.google.com/googleplay/android-developer/answer/10144311
- https://support.google.com/googleplay/android-developer/answer/14151465
- https://www.revenuecat.com/docs/platform-resources/google-platform-resources/google-plays-data-safety
