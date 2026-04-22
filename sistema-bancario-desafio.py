from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

# ========== MODELOS ============

class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, nome, data_nascimento, cpf):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero: int, cliente: Cliente):
        self._agencia = "0001"
        self._numero = numero
        self._cliente = cliente
        self._saldo = 0.0
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int):
        return cls(numero, cliente)

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ VALOR INVÁLIDO @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ SALDO INSUFICIENTE @@@")
            return False

        self._saldo -= valor
        print("\n=== SAQUE REALIZADO ===")
        return True

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n@@@ VALOR INVÁLIDO @@@")
            return False

        self._saldo += valor
        print("\n=== DEPÓSITO REALIZADO ===")
        return True

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor: float) -> bool:
        numero_saques = len([
            t for t in self.historico.transacoes
            if t["tipo"] == Saque.__name__
        ])

        if valor > self.limite:
            print("\n@@@ LIMITE EXCEDIDO @@@")
            return False

        if numero_saques >= self.limite_saques:
            print("\n@@@ LIMITE DE SAQUES EXCEDIDO @@@")
            return False

        return super().sacar(valor)

    def extrato(self):
        largura = 50
        print(f"{f' EXTRATO ':=^{largura}}")
        if not self.historico.transacoes:
            print("Nenhuma movimentação.")
        else:
            for t in self.historico.transacoes:
                if (t['tipo'] == "Deposito"):
                    cor = "\033[92m"
                elif (t['tipo'] == "Saque"):
                    cor = "\033[91m"
                else:
                    cor = ""
                print(f"{t['data']:<20} - {cor}{t['tipo']:<10}: R$ {t['valor']:>10.2f}\033[0m")
        #print(f"\nSaldo: R$ {self.saldo:.2f}")
        print(f"\n\033[1m\033[94m{'SALDO ':.<32} : R$ {self.saldo:>10.2f}\033[0m")
        print(f"{f'':=^{largura}}")

    def __str__(self):
        return f"""
Agência: {self.agencia}
Conta: {self.numero}
Titular: {self.cliente.nome}
"""
# ===== TRANSAÇÕES ========

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta: Conta):
        pass

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta: Conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

# =========== FUNÇÕES AUXILIARES ==============

def filtrar_cliente(clientes, cpf=None):
    if cpf is None:
        cpf = input("CPF: ")
    return next((c for c in clientes if c.cpf == cpf), None)

def recuperar_conta_cliente(cliente):
    return cliente.contas[0] if cliente.contas else None

# ==== OPERAÇÕES DO MENU =====

def depositar(clientes):
    cliente = filtrar_cliente(clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    valor = float(input("Valor: "))
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        print("Conta não encontrada!")
        return

    cliente.realizar_transacao(conta, Deposito(valor))

def sacar(clientes):
    cliente = filtrar_cliente(clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    valor = float(input("Valor: "))
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        print("Conta não encontrada!")
        return

    cliente.realizar_transacao(conta, Saque(valor))

def exibir_extrato(clientes):    
    cliente = filtrar_cliente(clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        print("Conta não encontrada!")
        return

    conta.extrato()

def criar_cliente(clientes):
    cpf = input("CPF: ")
    if filtrar_cliente(clientes, cpf):
        print("Cliente já existe!")
        return
    
    nome = input("Nome: ")
    data = input("Nascimento: ")
    endereco = input("Endereço: ")

    cliente = PessoaFisica(endereco, nome, data, cpf)
    clientes.append(cliente)

    print("Cliente criado!")

def criar_conta(numero, clientes, contas):
    cliente = filtrar_cliente(clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    conta = ContaCorrente.nova_conta(cliente, numero)
    cliente.adicionar_conta(conta)
    contas.append(conta)

    print("Conta criada!")

def listar_contas(contas):
    for conta in contas:
        print(textwrap.dedent(str(conta)))

# ===== MENU ======

def menu():
    largura = 80
    titulo_menu = f"{f' MENU ':=^{largura}}"
    return input(textwrap.dedent("""
    """) + titulo_menu + textwrap.dedent("""
    1 - Depositar
    2 - Sacar
    3 - Extrato
    4 - Nova Conta
    5 - Listar Contas
    6 - Novo Cliente
    7 - Sair \n""").upper() + f"{'':=^{largura}}" + textwrap.dedent("""
    => """))

# ===== PROGRAMA PRINCIPAL ======

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)
            input("\nPressione Enter para continuar...")

        elif opcao == "2":
            sacar(clientes)
            input("\nPressione Enter para continuar...")

        elif opcao == "3":
            exibir_extrato(clientes)
            input("\nPressione Enter para continuar...")

        elif opcao == "4":
            criar_conta(len(contas) + 1, clientes, contas)
            input("\nPressione Enter para continuar...")

        elif opcao == "5":
            listar_contas(contas)
            input("\nPressione Enter para continuar...")

        elif opcao == "6":
            criar_cliente(clientes)
            input("\nPressione Enter para continuar...")

        elif opcao == "7":
            print(" OBRIGADO POR USAR NOSSOS SERVIÇOS - MEGABANK. ")
            break

        else:
            print("Opção inválida!")
            input("\nPressione Enter para continuar...")


if __name__ == "__main__": # Para não executar main() quando importado como biblioteca
    main()