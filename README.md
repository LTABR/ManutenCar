# ManutenCar

> **Plataforma Web de Gestão e Manutenção Preventiva Veicular**
>
> Projeto acadêmico desenvolvido para a disciplina de Gestão de Projetos do curso de **Engenharia de Software da Universidade de Mogi das Cruzes (UMC)**.

---

## Sumário
  - [Sobre o Projeto](#sobre-o-projeto)
  - [Principais Funcionalidades](#principais-funcionalidades)
  - [Tecnologias Utilizadas](#tecnologias-utilizadas)
  - [Equipe de Desenvolvimente](#equipe-de-desenvolvimento)
  - [Estrutura de Gestão e Metodologia](#estrutura-de-gestão-e-metodologia)
  - [Execução do Projeto Localmente](#execução-do-projeto-localmente)
  - [Licença e Homologação](#licença-e-homologação)

---

## Sobre o Projeto

O **ManutenCar** é uma aplicação web desenvolvida para auxiliar motoristas na organização e acompanhamento do histórico de manutenção preventiva de seus veículos. O objetivo principal do sistema é ajudar a prevenir acidentes mecânicos e evitar prejuízos financeiros caudados pelo esquecimento de prazos de revisão de componentes vitais (como óleo do motor, sistema de freios, pneus, velas de ignição e líquido de arrefecimento).

O projeto adota uma **abordagem híbrida de gestão de software**:
- **Planejamento Preditivo (PMI/PMBOK - Waterfall):** Utilizado nas fases de iniciação, estruturação do escopo, viabilidade, EAP e cronograma de linha de base.
- **Execução Ágil (Scrum):** Utilizado no desenvolvimento incremental, fatiamento vertical de User Stories, rituais de Sprint e testes contínuos de qualidade.

---

## Principais Funcionalidades

- **Autenticação e Perfil de Usuário:** Cadastro de conta, login seguro com criptografia de senhas, controle de sessões via tokens (JWT/OAuth2) e recuperação de acesso.
- **Gestão de Veículos (CRUD):** Cadastro e atualização do histórico de automóveis, quilometragem percorrida e acompanhamento de peças.
- **Dashboard Orientado por Cores:** Interface com indicação visual direta (*Verde* para prazos vigentes e *Vermelho* para manutenções vencidas).
- **Motor de Cálculo e Previsão:** Algoritmos em Python que cruzam histórico, tempo de uso e quilometragem média para prever a vida útil e data sugerida de troca de componentes.
- **Sincronização de Calendário:** Visualização das próximas datas de revisão em formato de calendário interativo.
- **Guia e Rede Parceira:** Módulo informativo com dicas de manutenção, mural de perguntas frequentes (FAQ) e lista de contatos/disponibilidade de oficinas parceiras.
- **Conformidade com a LGPD:** Suporte à revogação e exclusão definitiva de conta/dados, com tratamento seguro de dados sensíveis.

---

## Tecnologias Utilizadas

### Front-End
- **Linguagem/Framework:** TypeScript, React
- **Estilização:** CSS3 (CSS Flexbox responsivo para uso em dispositivos móveis e desktop)

### Back-End
- **Linguagem:** Python (FastAPI / Flask)
- **Cálculos e Estatísticas:** Matplotlib, SciPy

### Banco de Dados & Infraestrutura
- **Banco Relacional:** MySQL
- **Armazenamento Local:** LocalStorage / Cache do navegador

### Garantia de Qualidade (QA)
- **Frameworks de Testes:** Cypress, Jest

---

## Equipe de Desenvolvimento

| Integrante | Papel Formal | Função no Time Ágil (Scrum) |
| :--- | :--- | :--- |
| **Mayte Cunha Severo da Silva** | Gerente de Projetos (GP) | Banco de Dados & Dev |
| **Breno Maciel de Assis** | Desenvolvedor Back-End | Product Owner (PO) |
| **Livia Keche de Oliveira** | Documentação & Processos | Scrum Master (SM) |
| **Lucas Tadashi Aniya** | Desenvolvedor Front-End | Developer |
| **Gustavo Pereira Prado** | Quality Assurance (QA) | Quality Assurance (QA) |

**Orientador:** Prof. Renato Mauro Richter

---

## Estrutura de Gestão e Metodologia

### 1. Rastreabilidade do Escopo (EAP → Product Backlog)

| Código EAP | Descrição da Entrega (EAP) | User Story (Backlog) | Esforço (SP) |
| :---: | :--- | :--- | :---: |
| **1.1** | Gestão de Usuários (Cadastro, Autenticação, LGPD) | **US-01 / US-02** | 13 SP |
| **1.2 / 1.6** | Gestão de Veículos e Motor de Cálculos (SciPy/Matplotlib) | **US-03 / US-04** | 13 SP |
| **1.3 / 1.4 / 1.5** | Calendário, Notificações e Suporte ao Cliente | **US-05 / US-06** | 8 SP |
| **1.7 / 1.8** | Sincronização, Persistência MySQL e Cache Local | **US-07** | 5 SP |
| **TOTAL** | **Escopo Completo do MVP** | **39 Story Points** | **39 SP** |

### 2. Sprints de Desenvolvimento (3 Sprints)
- **Sprint 1 (13 SP):** Infraestrutura de Banco de Dados MySQL, criptografia de senhas, rotas de autenticação/cadastro e LGPD.
- **Sprint 2 (13 SP):** Módulo CRUD de veículos/peças e integração do motor estatístico de cálculos em Python.
- **Sprint 3 (13 SP):** Sincronização de APIs REST, interface do calendário, canal de suporte e testes e2e com Cypress e Jest.

---

## Execução do Projeto Localmente

Requisitos: Python v3.10 ou superior, Node.js v18 ou superior e MySQL Server

### Passo a Passo

1. **Clonagem do repositório:**
   ```bash
   git clone https://github.com/Livia-Oliveira231964/ManutenCar.git
   cd ManutenCar
   ```

2. **Configuração do Back-End (Python):**
   ```bash
   cd backend
   python -m venv venv
   
   # No Linux/macOS:
   source venv/bin/activate
   # No Windows:
   # venv\Scripts\activate

   pip install -r requirements.txt
   python main.py
   ```

3. **Configuração do Front-End (TypeScript/React):**
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

4. **Execução da Suíte de Testes (QA):**
   ```bash
   # Testes unitários e de integração
   npm run test

   # Executar Cypress (Interface)
   npx cypress open
   ```

---

## Licença e Homologação

Este projeto é de caráter estritamente acadêmico, desenvolvido e homologado com sucesso como parte da avaliação parcial M1 do curso de Engenharia de Software da UMC.
