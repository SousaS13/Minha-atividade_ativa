import sqlite3
from datetime import datetime

# CORES TERMINAL
RED   = "\033[31m"
GREEN = "\033[32m"
AMARELO = "\033[33m"
CIANO = "\033[36m"
RESET = "\033[0m"

# CONEXÃO ÚNICA COM BANCO
con = sqlite3.connect("tia_rosa.db")
cursor = con.cursor()

# CRIAÇÃO DAS TABELAS
cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    categoria TEXT,
    preco REAL
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf TEXT,
    total REAL,
    data TEXT,
    FOREIGN KEY (cpf) REFERENCES clientes(cpf)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    preco_unitario REAL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
)""")
con.commit()

# RECIBO
def gerar_recibo(carrinho):
    print("\n" + GREEN + "RECIBO DE COMPRA:" + RESET)
    total = 0
    for nome, quantidade, preco in carrinho:
        preco_total = quantidade * preco
        print(f"{quantidade}x {nome} - R$ {preco_total:.2f}")
        total += preco_total
    print(f"\n{GREEN}TOTAL:{RESET} R$ {total:.2f}")

# SALVAR PEDIDO
def salvar_pedido(cpf, carrinho):
    total = sum(q * p for _, q, p in carrinho)
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute("INSERT INTO pedidos (cpf, total, data) VALUES (?, ?, ?)", (cpf, total, data))
    pedido_id = cursor.lastrowid

    for nome, quantidade, preco_unitario in carrinho:
        cursor.execute("SELECT id FROM produtos WHERE nome = ?", (nome,))
        resultado = cursor.fetchone()
        if resultado:
            produto_id = resultado[0]
            cursor.execute("""INSERT INTO itens_pedido 
                (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)""", (pedido_id, produto_id, quantidade, preco_unitario))

    con.commit()
    print(GREEN + "\nPedido salvo com sucesso!" + RESET)

# LISTAR PEDIDOS
def listar_pedidos():
    cursor.execute("SELECT id, cpf, total, data FROM pedidos ORDER BY data DESC")
    pedidos = cursor.fetchall()
    for id_pedido, cpf, total, data in pedidos:
        print(f"{CIANO}Pedido #{id_pedido}{RESET} | CPF: {cpf} | Total: R$ {total:.2f} | Data: {data}")
        cursor.execute("""SELECT produtos.nome, itens_pedido.quantidade 
            FROM itens_pedido 
            JOIN produtos ON itens_pedido.produto_id = produtos.id 
            WHERE itens_pedido.pedido_id = ?""", (id_pedido,))
        itens = cursor.fetchall()
        print("Produtos:", ", ".join([f"{q}x {n}" for n, q in itens]))
        print("-" * 50)

# REALIZAR PEDIDO
def realizar_pedido():
    listar_produtos_sql()
    cpf = input("\nInforme o CPF do cliente: ").strip()
    cursor.execute("SELECT nome FROM clientes WHERE cpf = ?", (cpf,))
    cliente = cursor.fetchone()

    if not cliente:
        print(RED + "CPF não encontrado. Cadastre o cliente primeiro." + RESET)
        return

    print(GREEN + f"\nOlá novamente, {cliente[0]}! Vamos montar seu pedido:" + RESET)
    carrinho = []

    while True:
        produto_id = input("Digite o ID do produto (ou 'fim' para encerrar): ").strip()
        if produto_id.lower() == "fim":
            break

        cursor.execute("SELECT nome, preco FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()

        if produto:
            nome, preco = produto
            try:
                quantidade = int(input(f"Quantos '{nome}' você deseja? "))
                if quantidade <= 0:
                    print(AMARELO + "Quantidade inválida. Tente novamente." + RESET)
                    continue
                carrinho.append((nome, quantidade, preco))
                print(GREEN + f"{quantidade}x '{nome}' adicionados ao carrinho!" + RESET)
            except ValueError:
                print(RED + "Quantidade inválida!" + RESET)
        else:
            print(RED + "Produto não encontrado!" + RESET)

    if carrinho:
        gerar_recibo(carrinho)
        salvar_pedido(cpf, carrinho)
    else:
        print(AMARELO + "Carrinho vazio." + RESET)

# LISTAR PRODUTOS
def listar_produtos_sql():
    cursor.execute("SELECT id, nome, categoria, preco FROM produtos ORDER BY categoria")
    produtos = cursor.fetchall()
    print("\n" + CIANO + "📋 PRODUTOS DISPONÍVEIS:" + RESET)
    for id, nome, categoria, preco in produtos:
        print(f"{id}. {nome} ({categoria}) - R$ {preco:.2f}")

# BOAS-VINDAS
def boas_vindas():
    print("\n" + CIANO + "Bem-vindo ao Coffe Shops Tia Rosa!" + RESET)
    cpf = input("Digite seu CPF: ").strip()
    cursor.execute("SELECT nome, telefone FROM clientes WHERE cpf = ?", (cpf,))
    cliente = cursor.fetchone()

    if cliente:
        print(GREEN + f"\nOlá, {cliente[0]}! Seja bem-vinda!" + RESET)
        conhecia = input("Você já conhece a nossa loja? (s/n): ").strip().lower()

        if conhecia in ["s", "sim"]:
            print(CIANO + "Que ótimo! Deseja ir direto para nosso Menu?" + RESET)
            resposta = input("Digite 's' para ir ou qualquer outra tecla para ficar por aqui: ").strip().lower()
            if resposta == "s":
                print(GREEN + "Ótima escolha! Preparando o menu..." + RESET)
                menu_principal()
                return
            else:
                print(AMARELO + "Sem pressa! Fique à vontade para explorar no seu tempo." + RESET)

        elif conhecia in ["n", "não"]:
            largura = 80
            mensagem = [
                "🌷 Coffe Shops Tia Rosa 🌷",
                "Há mais de 15 anos servindo memórias, sabores e acolhimento.",
                "Do espresso encorpado ao bolo de banana com afeto,",
                "cada detalhe é pensado para transformar cafés em momentos únicos.",
                "Sinta-se em casa, pois aqui você sempre será recebido com carinho."
            ]

            print("\n" + "+" + "-" * (largura + 2) + "+")
            for linha in mensagem:
                print("| " + linha.center(largura) + " |")
            print("+" + "-" * (largura + 2) + "+")
            print(GREEN + "\nConfira nosso menu para descobrir tudo que temos preparado com amor!" + RESET)
        else:
            print(AMARELO + "Resposta não reconhecida, mas não tem problema! Sinta-se em casa para explorar nosso menu." + RESET)

    else:
        nome = input("Nome: ")
        telefone = input("Telefone: ")
        cursor.execute("INSERT INTO clientes (cpf, nome, telefone) VALUES (?, ?, ?)", (cpf, nome, telefone))
        con.commit()
        print(GREEN + f"\nCadastro realizado com sucesso!" + RESET)
        print(CIANO + "Que bom ter você aqui pela primeira vez! Conheça nossas delícias no menu principal." + RESET)

# LISTAR CLIENTES
def listar_clientes():
    cursor.execute("SELECT nome, cpf, telefone FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    print("\nCLIENTES CADASTRADOS:")
    for nome, cpf, telefone in clientes:
        print(f"{nome} | CPF: {cpf} | Tel: {telefone}")

# CADASTRAR PRODUTO
def cadastrar_produto():
    nome = input("Nome do produto: ")
    categoria = input("Categoria: ")
    preco = float(input("Preço (R$): "))
    cursor.execute("INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)", (nome, categoria, preco))
    con.commit()
    print(GREEN + f"\nProduto '{nome}' cadastrado!" + RESET)

# RELATÓRIO SIMPLES
def relatorio_completo():
    cursor.execute("""SELECT clientes.nome, pedidos.cpf, COUNT(pedidos.id), SUM(pedidos.total)
        FROM pedidos JOIN clientes ON pedidos.cpf = clientes.cpf
        GROUP BY pedidos.cpf ORDER BY SUM(pedidos.total) DESC""")
    clientes = cursor.fetchall()
    print("\nClientes com pedidos:")
    for nome, cpf, qtde, total in clientes:
        print(f"{nome} | CPF: {cpf} | Pedidos: {qtde} | Total: R$ {total:.2f}")

# MENU PRINCIPAL
def menu_principal():
    while True:
        print("\n" + CIANO + " MENU PRINCIPAL — COFFE SHOPS TIA ROSA" + RESET)
        print("1️⃣ Realizar Pedido")
        print("2️⃣ Listar Produtos")
        print("3️⃣ Listar Clientes")
        print("4️⃣ Listar Histórico de Pedidos")
        print("5️⃣ Boas-Vindas / Cadastro de Cliente")
        print("6️⃣ Relatório de Vendas")
        print("7️⃣ Cadastrar Novo Produto")
        print("0️⃣ Sair")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "1":
            realizar_pedido()
        elif escolha == "2":
            listar_produtos_sql()
        elif escolha == "3":
            listar_clientes()
        elif escolha == "4":
            listar_pedidos()
        elif escolha == "5":
            boas_vindas()
        elif escolha == "6":
            relatorio_completo()
        elif escolha == "7":
            cadastrar_produto()
        elif escolha == "0":
            print(GREEN + "\nEncerrando sistema... Até a próxima visita à Tia Rosa! ☕" + RESET)
            break
        else:
            print(AMARELO + "Opção inválida. Tente novamente!" + RESET)


# INSERÇÃO AUTOMÁTICA DE PRODUTOS NO BANCO
def inserir_produtos_iniciais():
    produtos = {
        "espresso_duplo": {"nome": "Espresso Duplo", "categoria": "Bebidas Quentes", "preco": 7.00},
        "latte_baunilha": {"nome": "Latte com Baunilha", "categoria": "Bebidas Quentes", "preco": 10.00},
        "mocha_chocolate": {"nome": "Mocha com Chocolate Meio Amargo", "categoria": "Bebidas Quentes", "preco": 11.50},
        "cha_preto": {"nome": "Chá Preto com Especiarias", "categoria": "Bebidas Quentes", "preco": 8.00},
        "chocolate_quente": {"nome": "Chocolate Quente Cremoso", "categoria": "Bebidas Quentes", "preco": 9.50},
        "frappuccino_caramelo": {"nome": "Frappuccino de Caramelo", "categoria": "Bebidas Geladas", "preco": 12.00},
        "coldbrew_laranja": {"nome": "Cold Brew com Laranja", "categoria": "Bebidas Geladas", "preco": 10.50},
        "cafe_leitecoco": {"nome": "Café Gelado com Leite de Coco", "categoria": "Bebidas Geladas", "preco": 11.00},
        "smoothie_frutas": {"nome": "Smoothie de Frutas Vermelhas", "categoria": "Bebidas Geladas", "preco": 13.00},
        "cha_hibisco": {"nome": "Chá Gelado de Hibisco", "categoria": "Bebidas Geladas", "preco": 9.00},
        "coca_cola": {"nome": "Coca-Cola (350ml)", "categoria": "Bebidas Geladas", "preco": 6.00},
        "cha_berlim": {"nome": "Chá Berlim Gelado", "categoria": "Bebidas Geladas", "preco": 13.00},
        "bolo_banana": {"nome": "Bolo de Banana com Nozes", "categoria": "Comidas", "preco": 8.50},
        "croissant": {"nome": "Croissant com Queijo e Presunto", "categoria": "Comidas", "preco": 9.50},
        "pao_queijo": {"nome": "Pão de Queijo Artesanal", "categoria": "Comidas", "preco": 6.00},
        "torta_limao": {"nome": "Torta de Limão", "categoria": "Comidas", "preco": 10.00},
        "cookies": {"nome": "Cookies com Flor de Sal", "categoria": "Comidas", "preco": 7.50},
        "quiche": {"nome": "Quiche Individual", "categoria": "Comidas", "preco": 9.50},
        "cafe_arabica": {"nome": "Café Arábica ou Robusta", "categoria": "Ingredientes Extras", "preco": 0.00},
        "leite_varios": {"nome": "Leite (Integral/Vegetal)", "categoria": "Ingredientes Extras", "preco": 2.00},
        "sabores": {"nome": "Canela, Cardamomo, Baunilha", "categoria": "Ingredientes Extras", "preco": 1.50},
        "chocolate_caramelo": {"nome": "Chocolate Meio Amargo, Caramelo", "categoria": "Ingredientes Extras", "preco": 2.00},
        "chantilly": {"nome": "Chantilly, Marshmallows", "categoria": "Ingredientes Extras", "preco": 2.00},
        "raspas": {"nome": "Raspas de Limão ou Laranja", "categoria": "Ingredientes Extras", "preco": 1.00},
        "mel_acucar": {"nome": "Mel ou Açúcar Mascavo", "categoria": "Ingredientes Extras", "preco": 1.00},
        "gelo_pedras": {"nome": "Gelo ou Pedras de Café Congelado", "categoria": "Ingredientes Extras", "preco": 1.00}
    }

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total = cursor.fetchone()[0]
    
    if total == 0:
        largura = 40
        for item in produtos.values():
            nome = item["nome"].center(largura)
            preco = f"R$ {item['preco']:.2f}".center(largura)
            borda = "+" + "-" * (largura + 2) + "+"
            print("\n" + borda)
            print("| " + CIANO + nome + RESET + " |")
            print("| " + AMARELO + preco + RESET + " |")
            print(borda)

            cursor.execute(
                "INSERT INTO produtos (nome, categoria, preco) VALUES (?, ?, ?)",
                (item["nome"], item["categoria"], item["preco"])
            )
        con.commit()
        print(GREEN + f"\n {len(produtos)} produtos foram inseridos com sucesso no banco!" + RESET)
    else:
        print(AMARELO + f"\n Produtos já existem no banco. Inserção automática ignorada." + RESET)



# CHAMAR IMEDIATAMENTE APÓS CRIAR A TABELA
inserir_produtos_iniciais()

# INICIAR SISTEMA
boas_vindas()
menu_principal()

# FECHAR CONEXÃO FINAL DO BANCO
con.close()




