# Case Study: Building a Production Analytics SaaS via AI Orchestration

## Executive Summary

Este estudo de caso documenta como um **SaaS completo de Analytics e BI sem SQL** foi projetado, desenvolvido, testado e publicado em produção utilizando **orquestração estratégica de agentes de Inteligência Artificial**.

Diferente da abordagem comum de solicitar trechos avulsos de código via chat ("vibe coding"), este projeto foi guiado por uma metodologia estruturada de **AI Harnessing** (Governança de Agentes), alcançando:

- **>900 testes unitários e de integração** aprovados com 0 falhas.
- **Zero vulnerabilidades de segurança** multi-tenant ou vazamento de dados.
- **Ambiente de produção real em VPS** rodando com suporte a múltiplos clientes.
- **Alta eficiência de hardware**, processando datasets em Parquet/DuckDB em uma VPS de 1 vCPU e 2GB RAM.

---

## 1. O Desafio de Engenharia

Construir uma plataforma de BI no-code apresenta desafios complexos de arquitetura:

1. **Desempenho com Dados Heterogêneos:** CSVs e planilhas Excel enviadas por usuários têm colunas imprevisíveis, tipos nulos, formatações de data variadas e tamanhos arbitrários.
2. **Segurança Multi-Tenant Absoluta:** O vazamento de dados de um cliente para outro inviabilizaria comercialmente qualquer SaaS B2B.
3. **Escala Econômica:** Evitar infraestruturas caras (como ClickHouse ou Redshift gerenciados) para manter o produto viável financeiramente nos estágios iniciais.

---

## 2. A Metodologia de Orquestração de IA (AI Harness)

Para evitar que o uso de agentes de IA gerasse um "monstro de código" difícil de manter, estabelecemos um sistema de **governança rigorosa por agentes**.

### A. Estrutura de Regras de IA (`AGENTS.md`)

O agente de IA operava sob um conjunto inviolável de diretrizes:

- **Context Window Enxuto:** Cada interação recebia apenas os arquivos diretamente relevantes para a tarefa atual, evitando saturação do prompt.
- **Verificação Pré/Pós-Mudança:** A IA era obrigada a ler a especificação da fase, propor o plano, executar as edições e imediatamente rodar a suíte de testes.

```text
Entendimento do Requisito -> Leitura Autoritativa -> Escopo Limitado -> Edição Única -> Testes (pytest) -> Verificação (manage.py check) -> Log & Registro
```

### B. Proteção contra Regressões

Qualquer código gerado pela IA precisava satisfazer três portões antes de ser considerado "concluído":

1. **`docker compose exec web pytest`**: Garantindo que nenhum comportamento existente quebrou.
2. **`docker compose exec web python manage.py check`**: Validando a integridade dos modelos e rotas Django.
3. **`docker compose exec web python manage.py makemigrations --check`**: Confirmando que nenhuma alteração de modelo ficou sem migração.

---

## 3. Decisões Arquiteturais Chave

### A. Polars + Parquet + DuckDB (A Tríade de Alta Performance)

Em vez de salvar dados de planilhas diretamente no PostgreSQL (o que causaria explosão de tabelas dinâmicas e baixa performance em agregações OLAP):

1. **Ingestão:** O **Polars** converte o CSV/XLSX enviando streaming diretamente para o formato **Parquet**.
2. **Armazenamento:** Cada dataset é salvo como arquivo colunar Parquet comprimido no sistema de arquivos isolado do tenant (`storage/tenants/<org_id>/datasets/<dataset_id>/current.parquet`).
3. **Consulta SQL:** O **DuckDB** executa consultas analíticas (`GROUP BY`, `SUM`, `AVG`, filtros de data) diretamente sobre o arquivo Parquet sem precisar carregar os dados em um banco tradicional.

### B. Otimização de Recursos em Hardware Restrito

Para rodar com baixíssimo custo na VPS (1 vCPU, 2GB RAM):

- Criou-se um gerenciador de sessão DuckDB com **semáforo global e limites de memória estritos** (`services/duckdb_session.py`).
- O número de threads de execução do DuckDB foi explicitamente limitado (`DUCKDB_THREADS=1`), impedindo que consultas complexas causem *Out of Memory (OOM)* no SO.

### C. Multi-Tenancy Rígido na Camada de Serviço

A segurança multi-tenant é garantida por dois pilares:

1. **Middleware de Organização:** O middleware intercepta toda requisição autenticada e injeta `request.current_organization`.
2. **Consultas Restritas:** Todas as consultas no Django ou no DuckDB filtram obrigatoriamente pelo UUID da organização ativa. A IA foi programada para rejeitar qualquer consulta direta por `id` desacompanhada de `organization`.

---

## 4. Hardening de Segurança e DevOps

A aplicação foi preparada para produção real com os seguintes níveis de hardening:

- **Contêineres não-root:** O serviço web roda no Docker sob usuário sem privilégios (`uid 10001`) e `cap_drop: ALL`.
- **Proteção Nginx com Zonas de Rate-Limit:** Configuração do Nginx limitando rajadas em login (1r/s) e aplicação (10r/s), respondendo `HTTP 429` com `Retry-After: 1`.
- **Backups Criptografados Offsite:** Scripts automatizados (`scripts/backup.sh`) geram dumps do PostgreSQL e storage de tenants, criptografam os dados com `rclone crypt` e enviam para um bucket S3/Spaces em nuvem, com testes periódicos de restauração (`scripts/restore_drill.sh`).

---

## 5. Resultados e Lições Aprendidas

1. **Velocidade com Qualidade:** O MVP foi desenvolvido e publicado em produção em tempo recorde sem sacrificar testes ou segurança.
2. **Engenharia > Gerador de Código:** A IA atua como uma ferramenta extremamente poderosa quando o desenvolvedor mantém o controle da arquitetura, estabelece regras rígidas e exige testes automatizados em cada iteração.
3. **Padrões de Qualidade Corporativa:** A base de código resultante segue os mesmos padrões de segurança, separação de responsabilidades e resiliência exigidos por grandes empresas de tecnologia.

---
*Estudo de caso desenvolvido por Samuel Werplotz.*
