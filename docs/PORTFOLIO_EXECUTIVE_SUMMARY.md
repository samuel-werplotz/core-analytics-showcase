# Guia Executivo de Bolso — Análise Técnica & Entrevistas

Este guia sintetiza os principais pontos de engenharia, decisões de arquitetura e estratégias de orquestração de IA do **Core Analytics** para consulta rápida antes ou durante reuniões com recrutadores, engenheiros sêniores e clientes.

---

## 🚀 Pitch Curto (30 Segundos)

> *"Eu desenvolvi o Core Analytics, um SaaS de BI No-Code de alta performance em Python/Django, Polars e DuckDB, 100% orquestrado por mim através de agentes de IA. Em vez de usar IA apenas para autocomplete, criei um harness de governança com validações estritas de segurança multi-tenant, TDD com mais de 900 testes automatizados e deploy hardenizado em produção (VPS com Docker e Nginx). O sistema processa planilhas CSV/Excel convertendo-as para Parquet e DuckDB in-memory em milissegundos rodando em uma infraestrutura enxuta de 1 vCPU e 2GB de RAM."*

---

## 🔑 5 Pilares para Destacar em Entrevistas

### 1. Orquestração de IA & Governança de Código
- **Como responder:** "Utilizei um método chamado AI Harnessing. Defini contratos operacionais rígidos em markdown (`AGENTS.md`) limitando a janela de contexto da IA, proibindo refatorações oportunistas e exigindo a execução de testes (`pytest`) e checagens do Django antes de dar qualquer tarefa por concluída. Isso evitou alucinações e manteve a base de código limpa."

### 2. Engine Analytics Híbrida (Polars + Parquet + DuckDB)
- **Como responder:** "Banco relacional (PostgreSQL) não é otimizado para agregação OLAP. Em vez de contratar uma infraestrutura cara como Redshift ou ClickHouse, estruturei uma pipeline onde planilhas são convertidas via Polars em arquivos colunares Parquet por tenant. O DuckDB executa consultas SQL em memória sobre esses arquivos Parquet, gerando agregações em milissegundos."

### 3. Otimização Severa de Hardware (1 vCPU / 2GB RAM)
- **Como responder:** "Para manter o custo da infraestrutura próximo de zero no piloto, estruturei um gerenciador de sessão DuckDB com semáforo thread-safe. Limitei a concorrência (`DUCKDB_THREADS=1`) e os limites de memória (`memory_limit`), impedindo vazamento de recursos ou crash do sistema operacional mesmo sob carga."

### 4. Multi-Tenancy Rígido e Segurança de Dados
- **Como responder:** "Adotei o princípio de zero-confiança no input do cliente. O `organization_id` nunca é aceito pelo frontend. O backend descobre a organização através do usuário autenticado no middleware (`request.current_organization`). Além disso, os arquivos Parquet ficam fisicamente isolados no storage por ID da organização (`storage/tenants/<org_id>/`)."

### 5. DevOps, Hardening & Backups Criptografados
- **Como responder:** "O deploy foi feito com Docker hardenizado (usuário sem privilégios `uid 10001` e sem capacidades de root), Nginx atuando como proxy reverso com suporte a HTTP 429 para rate-limiting e headers de segurança CSP/HSTS. Criei um script de backup diário que criptografa os dados com `rclone crypt` antes de enviar para S3/DigitalOcean Spaces, com ensaios periódicos de restauração."

---

## ❓ Perguntas Frequentes de Entrevistadores (Q&A)

### Q: Como você garantiu que a IA não introduziu brechas de segurança ou dados expostos?
**Resposta:** *"Defini regras invioláveis no arquivo de contexto do agente. Qualquer tentativa de expor SQL bruto, paths absolutos de arquivos, stack traces ou buscar recursos no banco sem filtrar pela organização ativa causava a rejeição da entrega. Além disso, criamos testes de invasão e isolamento multi-tenant dedicados na suíte de testes."*

### Q: Por que não usou Pandas em vez de Polars?
**Resposta:** *"O Polars é escrito em Rust, utiliza execução lazy e possui suporte nativo ao PyArrow. Ele é substancialmente mais rápido na conversão de CSV/Excel para Parquet e consome uma fração da memória RAM em comparação ao Pandas, o que foi crítico para o nosso limite de 2GB RAM."*

### Q: Como funciona o sistema de Embeds de dashboards?
**Resposta:** *"Para permitir que dashboards fossem incorporados em sites externos de forma segura sem expor a sessão do usuário, criamos tokens HMAC assinados com tempo de expiração e limitação por origem HTTP (`allowlist`). Isso isolou completamente o ambiente público do núcleo da aplicação."*

### Q: Qual foi a maior lição aprendida na orquestração de IA?
**Resposta:** *"IA é um multiplicador de produtividade, mas exige diretrizes arquiteturais claras e automação de testes. Sem uma suíte forte de testes automatizados e regras de escopo, a IA perde contexto e reescreve padrões. O segredo foi manter entregas pequenas, incrementais e validadas por código."*

---

## 📋 Checklist de Segurança para Redes Sociais / GitHub Público

- [x] Zero senhas ou segredos de banco de dados no repositório.
- [x] Zero chaves de API reais (usar sempre `YOUR_API_KEY_HERE`).
- [x] `.env.example` sanitizado.
- [x] Sem links ou IPs privados de servidores de produção.
- [x] Regras de negócio confidenciais preservadas no SaaS comercial.

---
*Elaborado para Samuel Werplotz.*
