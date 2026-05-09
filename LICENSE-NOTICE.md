# LICENSE NOTICE

## Status jurídico deste fork

Este repositório (`Regis-BR/bravo-code-sdd-g`) é um fork público de [`ip2cloud/bravo-code-sdd`](https://github.com/ip2cloud/bravo-code-sdd) com modificações substanciais.

A situação de licenciamento é heterogênea e está documentada honestamente abaixo.

---

## 1. Código herdado do upstream

O repositório upstream `ip2cloud/bravo-code-sdd` **não declara nenhuma licença explícita** (não há arquivo `LICENSE` nem nota de copyright no código). Sob a interpretação padrão do direito autoral aplicável (incluindo a Lei 9.610/1998 no Brasil e o U.S. Copyright Act), código sem licença explícita é considerado **"all rights reserved"** — todos os direitos pertencem ao autor original.

Implicações:

- O ato de **forkar** repositório público no GitHub é tecnicamente coberto pelos Termos de Serviço do GitHub (cláusula D.5), que concedem aos usuários do GitHub direito limitado de visualização e bifurcação para uso *na própria plataforma*.
- Qualquer **uso fora do GitHub**, **redistribuição**, **modificação para fins comerciais** ou **incorporação em obras derivadas** do código herdado **não tem base legal explícita** sem autorização do autor original (`ip2cloud`).

Recomendação para terceiros: **não use o código herdado deste fork em produtos comerciais sem antes contatar `ip2cloud` e obter licença explícita**.

---

## 2. Modificações originais por Regis Renzi

Todas as modificações, adições e novos arquivos introduzidos neste fork (incluindo, mas não se limitando a):

- Arquivos sob `.github/`
- Workflows em `.github/workflows/`
- Servidor MCP em `kb-mcp/` (Onda 4)
- Configurações em `.devcontainer/` (Onda 4)
- Documentação em `docs/`
- Este arquivo `LICENSE-NOTICE.md`
- Modificações no `README.md`

são **propriedade intelectual de Regis Renzi** (CPF e dados profissionais sob `regis@rnztech.com`, RNZ Tech Ltda).

**Reserva de direitos:**

```
Copyright (c) 2026 Regis Renzi (RNZ Tech Ltda).
All rights reserved.

Internal use only. No license is granted to use, copy, modify, merge,
publish, distribute, sublicense, or sell copies of these contributions
without prior written permission from the copyright holder.

For licensing inquiries: regis@rnztech.com
```

---

## 3. Visibilidade pública vs licença

Este repositório é **público no GitHub** por configuração de fork (forks de repos públicos não podem ser tornados privados pela UI do GitHub).

**Visibilidade pública não implica licença permissiva.** O conteúdo pode ser visualizado por qualquer pessoa, mas isso não confere direito de uso, modificação ou redistribuição.

Se você está lendo este repositório:

- **Você pode**: ler, estudar, citar conceitualmente em discussões públicas.
- **Você não pode** (sem autorização): copiar trechos para outros projetos, criar fork comercial, redistribuir como obra própria.

---

## 4. Para uso interno do mantenedor (Regis Renzi)

Para uso pessoal e dentro de RNZ Tech Ltda / Organização Renzi:

- As **ideias arquiteturais** absorvidas deste framework podem ser **reimplementadas em produtos próprios** (Contabia, SecureToken, etc.) por método **clean room** — ou seja, a partir da compreensão dos conceitos, sem cópia direta de código autoral do upstream.
- A reimplementação clean room é juridicamente robusta porque o que é protegido por copyright é a **expressão** (código específico), não a **ideia** (estrutura conceitual de pipeline SDD em 5 fases, agent matching, etc.).

---

## 5. Histórico desta nota

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-05-09 | 1.0 | Documento inicial criado durante Onda 1 do roadmap deste fork |

---

## 6. Disclaimer

Este documento é uma declaração de boa-fé sobre o status jurídico percebido. **Não constitui aconselhamento jurídico**. Em caso de dúvida sobre uso comercial, consulte advogado especializado em propriedade intelectual e software.

---

**Contato**: regis@rnztech.com
**Mantenedor**: Regis Renzi — RNZ Tech Ltda / Organização Renzi (Suzano, SP, Brasil)
