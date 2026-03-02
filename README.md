# 🚀 Space Shooter 2D - Projeto Acadêmico

Este é um jogo de tiro espacial desenvolvido em **Python** utilizando a biblioteca **Pygame**. O projeto foi construído como parte de um trabalho acadêmico, focando em boas práticas de programação, padrões de projeto (Design Patterns) e persistência de dados.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.12
* **Biblioteca Gráfica:** Pygame 2.6.1
* **Banco de Dados:** SQLite (via módulo sqlite3)
* **IDE:** PyCharm / VS Code

## 🧠 Padrões de Projeto & Arquitetura
O desenvolvimento seguiu princípios de Engenharia de Software para garantir um código limpo e modular:

* **Singleton (AssetManager):** Garante que imagens e sons sejam carregados apenas uma vez na memória, otimizando a performance.
* **Proxy (DBProxy):** Intermedeia a comunicação com o banco de dados SQLite, protegendo a integridade dos Scores.
* **Mediator (EntityMediator):** Centraliza a comunicação entre as entidades (Player e Enemy), facilitando a detecção de colisões e pontuação.
* **Factory (EntityFactory):** Centraliza a criação de todos os objetos do jogo, desacoplando a lógica de spawn da lógica de nível.

## 🎮 Funcionalidades
- [x] **Movimentação Suave:** Controle preciso do jogador em 8 direções.
- [x] **Sistema de Níveis:** Progressão automática com troca de fundos (backgrounds) e aumento de dificuldade.
- [x] **IA de Inimigos:** Movimentação em grade com ataques calculados por probabilidade.
- [x] **High Scores:** Ranking persistente que salva a pontuação do jogador localmente.
- [x] **Comandos de Saída:** Uso da tecla `ESC` para retornar ao menu a qualquer momento.

## 🕹️ Como Jogar

1. **Instale o Pygame:**
```bash
pip install pygame
```
2. **Execute o Jogo**:
```bash
python main.py
```
## Estrutura do Projeto
```
├── assets/             # Imagens e Sons (.png, .wav, .mp3)
├── code/               # Módulos Python (Lógica do Jogo)
│   ├── Const.py        # Constantes e Configurações Globais
│   ├── AssetManager.py # Gerenciador de Recursos (Singleton)
│   ├── Level.py        # Lógica de Fases e Eventos
│   └── ...
├── main.py             # Ponto de entrada do jogo
└── scores.db           # Banco de dados SQLite
```
## ✍️ Créditos
Este projeto foi desenvolvido integralmente por:

#### Washington Fontana Netto

#### ⭐ Desenvolvido para fins acadêmicos.