import re
import json

# Texto fornecido
texto = """


Identificacao do equipamento:
                        Modelo: NHS Mini Max
               Versao da placa: 0
        Quantidade de baterias: 1
     Tensao de entrada nominal: 220.0 V
       Tensao de saida nominal: 220.0 V
              Mede temperatura: sim
          Mede tensao de saida: sim
               Tipo de bateria: selada
   Mede corrente do carregador: sim

Configuracao do equipamento:
                  Valida desde: 04/Jan 20:28:21
            Versao do firmware: 20
                Subtensao 120V: 95.0 V
              Sobretensao 120V: 145.0 V
                Subtensao 220V: 180.0 V
              Sobretensao 220V: 249.0 V
           Tensao nominal 120V: 120.0 V
           Tensao nominal 220V: 220.0 V
        Corrente do carregador: 0 mA

Configuracao do servidor:
                         Porta: /dev/ttyS0

Dados do equipamento:
             Tensao de entrada: 220.0 V
               Tensao de saida: 211.0 V
      Tensao de entrada minima: 220.0 V
      Tensao de entrada maxima: 220.0 V
     Tensao nominal de entrada: 220.0 V
       Tensao nominal de saida: 220.0 V
             Tensao da bateria: 13.6 V
                         Carga: 9.0%
                   Temperatura: 43 C
        Corrente do carregador: 0 mA
            Potencia excessiva: nao
                 Modo inversor: nao
                 Bateria baixa: nao
                 Rede em falha: nao
         Queda abrupta de rede: nao
                  Bypass ativo: sim
              Carregador ativo: nao

"""

# Separando as seções
secoes = re.split(r'\n\n+', texto.strip())

# Convertendo cada seção em um dicionário
dados = {}
for secao in secoes:
    linhas = secao.split('\n')
    categoria = linhas[0].strip(':')
    dados[categoria] = {}
    for linha in linhas[1:]:
        chave, valor = linha.split(':', 1)
        dados[categoria][chave.strip()] = valor.strip()

# Convertendo para JSON
json_resultado = json.dumps(dados, indent=4)

# Imprimindo o resultado
print(json_resultado)