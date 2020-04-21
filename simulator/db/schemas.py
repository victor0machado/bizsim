clientes = [
    'clientes', """
    CREATE TABLE clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf VARCHAR(14) NOT NULL,
        nascimento DATE NOT NULL,
        id_endereco INTEGER,
        FOREIGN KEY (id_endereco) REFERENCES enderecos(id_endereco)
    );
    """
]

produtos = [
    'produtos', """
    CREATE TABLE produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        cor TEXT NOT NULL,
        tamanho TEXT NOT NULL,
        preco INTEGER NOT NULL
    );
    """
]

vendas = [
    'vendas', """
    CREATE TABLE vendas (
        id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
        data_venda DATE NOT NULL,
        frete TEXT NOT NULL,
        meio_pgto TEXT NOT NULL,
        id_cliente INTEGER,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    );
    """
]

enderecos = [
    'enderecos', """
    CREATE TABLE enderecos (
        id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
        cidade TEXT NOT NULL,
        uf VARCHAR(2) NOT NULL
    );
    """
]

prod_vend = [
    'prod_vend', """
    CREATE TABLE prod_vend (
        id_prod_vend INTEGER PRIMARY KEY AUTOINCREMENT,
        quantidade INTEGER NOT NULL,
        id_venda INTEGER,
        id_produto INTEGER,
        FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
        FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
    );
    """
]
