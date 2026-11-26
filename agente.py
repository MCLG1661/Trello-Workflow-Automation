import os
from datetime import datetime

from dotenv import load_dotenv
from trello import TrelloClient

# Carrega as credenciais do arquivo .env
load_dotenv()

# Configura o cliente do Trello
API_KEY = os.getenv('TRELLO_API_KEY')
TOKEN = os.getenv('TRELLO_TOKEN')

def conectar_trello():
    """Conecta à API do Trello com as credenciais configuradas"""
    try:
        client = TrelloClient(api_key=API_KEY, token=TOKEN)
        print("✅ Conectado ao Trello com sucesso!")
        return client
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def listar_meus_quadros(client):
    """Lista todos os seus quadros do Trello"""
    boards = client.list_boards()
    print("\n📋 Seus quadros:")
    for i, board in enumerate(boards):
        print(f"  {i+1}. {board.name} (ID: {board.id})")
    return boards

def selecionar_nome(items, nome):
    if not nome.strip():
        return None
    matches = [item for item in items if nome.casefold() in item.name.casefold()]
    exact = [item for item in matches if item.name.casefold() == nome.casefold()]
    candidates = exact or matches
    return candidates[0] if len(candidates) == 1 else None


def indice_valido(items, idx):
    if not 0 <= idx < len(items):
        raise ValueError("Opção inválida")
    return items[idx]


def selecionar_quadro(boards):
    """Permite selecionar um quadro pelo nome ou índice"""
    if not boards:
        print("Nenhum quadro encontrado.")
        return None
    
    nome = input("\n🔍 Digite o nome do quadro (ou número): ").strip()
    
    # Tenta selecionar por número
    if nome.isdigit():
        idx = int(nome) - 1
        if 0 <= idx < len(boards):
            return boards[idx]
    
    # Tenta selecionar por nome (parcial)
    if nome.isdigit():
        return None
    board = selecionar_nome(boards, nome)
    if board is None:
        print("❌ Quadro não encontrado ou seleção ambígua.")
    return board

def listar_listas_do_quadro(board):
    """Lista todas as listas de um quadro"""
    lists = board.list_lists()
    print(f"\n📌 Listas do quadro '{board.name}':")
    for i, lst in enumerate(lists):
        print(f"  {i+1}. {lst.name} (ID: {lst.id})")
    return lists

def criar_card(lista, nome, descricao=""):
    """Cria um novo card em uma lista específica"""
    try:
        card = lista.add_card(name=nome, desc=descricao)
        print(f"✅ Card '{card.name}' criado com sucesso!")
        return card
    except Exception as e:
        print(f"❌ Erro ao criar card: {e}")
        return None

def mover_card(card, lista_destino):
    """Move um card para outra lista"""
    try:
        card.change_list(lista_destino.id)
        print(f"✅ Card movido para '{lista_destino.name}'")
        return True
    except Exception as e:
        print(f"❌ Erro ao mover card: {e}")
        return False

def adicionar_comentario(card, comentario):
    """Adiciona um comentário a um card"""
    try:
        card.comment(comentario)
        print(f"✅ Comentário adicionado ao card '{card.name}'")
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar comentário: {e}")
        return False

def listar_cards_da_lista(lista):
    """Lista todos os cards de uma lista"""
    cards = lista.list_cards()
    print(f"\n🎴 Cards da lista '{lista.name}':")
    if not cards:
        print("  (Nenhum card encontrado)")
    for i, card in enumerate(cards):
        print(f"  {i+1}. {card.name}")
    return cards

def automatizar_tarefas_diarias(client):
    """
    Função principal de automação:
    - Cria cards diários em uma lista específica
    - Não move tarefas sem confirmação explícita de conclusão
    """
    print("\n" + "="*50)
    print("🤖 INICIANDO AUTOMAÇÃO DIÁRIA")
    print("="*50)
    
    # 1. Encontrar o quadro desejado
    boards = client.list_boards()
    print("\nQuadros disponíveis:")
    for i, board in enumerate(boards):
        print(f"  {i+1}. {board.name}")
    
    board_name = input("\n📁 Nome do quadro para automação: ").strip()
    board = selecionar_nome(boards, board_name)
    
    if not board:
        print(f"❌ Quadro '{board_name}' não encontrado!")
        return
    
    print(f"\n✅ Quadro selecionado: {board.name}")
    
    # 2. Listar listas do quadro
    lists = board.list_lists()
    print("\nListas disponíveis:")
    for i, lst in enumerate(lists):
        print(f"  {i+1}. {lst.name}")
    
    # 3. Selecionar lista para criar cards
    todo_list_name = input("\n📝 Nome da lista para criar cards (ex: 'To Do'): ").strip()
    todo_list = selecionar_nome(lists, todo_list_name)
    
    if not todo_list:
        print(f"❌ Lista '{todo_list_name}' não encontrada!")
        return
    
    # 4. Selecionar lista para mover cards finalizados
    done_list_name = input("✅ Nome da lista para mover cards concluídos (ex: 'Done'): ").strip()
    done_list = selecionar_nome(lists, done_list_name)
    
    if not done_list:
        print(f"❌ Lista '{done_list_name}' não encontrada!")
        return
    
    if todo_list.id == done_list.id:
        print("❌ Origem e destino devem ser diferentes.")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    task_name = f"Tarefa do dia - {today}"
    existing = [card for lst in lists for card in lst.list_cards()
                if card.name == task_name]
    if existing:
        print(f"ℹ️ Tarefa diária já existente: {task_name}")
        return
    novo_card = criar_card(todo_list, task_name, "Tarefa criada automaticamente pelo agente Python")
    if novo_card is None:
        print("❌ Automação interrompida: criação falhou.")
        return
    print(f"✅ Card criado: {novo_card.name}")
    print("Cards movidos: 0 (conclusão deve ser confirmada manualmente).")


def menu_principal():
    """Menu interativo do agente"""
    client = conectar_trello()
    if not client:
        return
    
    while True:
        print("\n" + "="*40)
        print("🤖 AGENTE TRELLO - AUTOMAÇÃO")
        print("="*40)
        print("1. 📋 Listar meus quadros")
        print("2. ➕ Criar novo card")
        print("3. 🔄 Mover card entre listas")
        print("4. 💬 Adicionar comentário a um card")
        print("5. 📊 Listar cards de uma lista")
        print("6. 🚀 Executar automação diária")
        print("0. 👋 Sair")
        print("-"*40)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "0":
            print("👋 Até logo!")
            break
        
        elif opcao == "1":
            listar_meus_quadros(client)
        
        elif opcao == "2":
            boards = listar_meus_quadros(client)
            board = selecionar_quadro(boards)
            if board:
                lists = listar_listas_do_quadro(board)
                if lists:
                    print("\nOpções:")
                    for i, lst in enumerate(lists):
                        print(f"  {i+1}. {lst.name}")
                    try:
                        idx = int(input("Número da lista: ")) - 1
                        lista = indice_valido(lists, idx)
                        nome_card = input("Nome do card: ")
                        desc_card = input("Descrição (opcional): ")
                        criar_card(lista, nome_card, desc_card)
                    except (ValueError, IndexError):
                        print("❌ Opção inválida!")
        
        elif opcao == "3":
            boards = listar_meus_quadros(client)
            board = selecionar_quadro(boards)
            if board:
                lists = listar_listas_do_quadro(board)
                if lists:
                    print("\nSelecione a lista ORIGEM:")
                    for i, lst in enumerate(lists):
                        print(f"  {i+1}. {lst.name}")
                    try:
                        idx_origem = int(input("Número da lista origem: ")) - 1
                        lista_origem = indice_valido(lists, idx_origem)
                        cards = listar_cards_da_lista(lista_origem)
                        
                        if cards:
                            idx_card = int(input("Número do card: ")) - 1
                            card = indice_valido(cards, idx_card)
                            
                            print("\nSelecione a lista DESTINO:")
                            for i, lst in enumerate(lists):
                                print(f"  {i+1}. {lst.name}")
                            idx_destino = int(input("Número da lista destino: ")) - 1
                            lista_destino = indice_valido(lists, idx_destino)
                            
                            mover_card(card, lista_destino)
                    except (ValueError, IndexError):
                        print("❌ Opção inválida!")
        
        elif opcao == "4":
            boards = listar_meus_quadros(client)
            board = selecionar_quadro(boards)
            if board:
                lists = listar_listas_do_quadro(board)
                if lists:
                    print("\nSelecione a lista do card:")
                    for i, lst in enumerate(lists):
                        print(f"  {i+1}. {lst.name}")
                    try:
                        idx_lista = int(input("Número da lista: ")) - 1
                        lista = indice_valido(lists, idx_lista)
                        cards = listar_cards_da_lista(lista)
                        
                        if cards:
                            idx_card = int(input("Número do card: ")) - 1
                            card = indice_valido(cards, idx_card)
                            comentario = input("Comentário: ")
                            adicionar_comentario(card, comentario)
                    except (ValueError, IndexError):
                        print("❌ Opção inválida!")
        
        elif opcao == "5":
            boards = listar_meus_quadros(client)
            board = selecionar_quadro(boards)
            if board:
                lists = listar_listas_do_quadro(board)
                if lists:
                    print("\nSelecione a lista:")
                    for i, lst in enumerate(lists):
                        print(f"  {i+1}. {lst.name}")
                    try:
                        idx = int(input("Número da lista: ")) - 1
                        listar_cards_da_lista(indice_valido(lists, idx))
                    except ValueError:
                        print("❌ Opção inválida!")
        
        elif opcao == "6":
            automatizar_tarefas_diarias(client)
        
        else:
            print("❌ Opção inválida! Tente novamente.")

# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()
