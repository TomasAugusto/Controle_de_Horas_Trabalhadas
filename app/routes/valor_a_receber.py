from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta


valor_a_receber_bp = Blueprint('valor_a_receber', __name__)



def formatar_horas_decimais(valor_decimal):
    horas = int(valor_decimal)
    minutos = int(round((valor_decimal - horas) * 60))
    return f"{horas}h{minutos:02d}min"



#----------------------------------Valor a Receber-------------------------------------------

@valor_a_receber_bp.route('/calcular_valor_mensal', methods=['GET', 'POST'])
def calcular_valor_mensal():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obter o ID do colaborador logado
    colaborador_id = session['usuario_id']

    # Obter o mês e ano selecionados (padrão: mês e ano atual)
    mes = int(request.args.get('mes', datetime.today().month))
    ano = int(request.args.get('ano', datetime.today().year))

    # Lista de nomes dos meses em português
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    nome_mes = meses[mes - 1]  # Subtrair 1 porque a lista começa em 0

    # Conectar ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consultar o valor da hora do colaborador
    cursor.execute("SELECT ValorHora FROM Usuarios WHERE IdUsuario = ?", (colaborador_id,))
    valor_hora = cursor.fetchone()[0]

    # Consultar os registros do colaborador no mês e ano selecionados
    query = """
    SELECT DataRegistro, HoraInicio, HoraFim
    FROM RegistrosHoras
    WHERE IdColaborador = ?
    AND MONTH(DataRegistro) = ?
    AND YEAR(DataRegistro) = ?
    ORDER BY DataRegistro, HoraInicio
    """
    cursor.execute(query, (colaborador_id, mes, ano))
    registros = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Calcular o total de horas trabalhadas (considerando sobreposições)
    total_horas = calcular_horas_trabalhadas(registros)

    horas_formatadas = formatar_horas_decimais(total_horas)


    # Calcular o valor total a receber
    valor_total = total_horas * valor_hora

    # Renderizar o template e passar os dados
    return render_template(
        'calcular_valor_mensal.html', # Nome do arquivo HTML 
        mes=mes,
        nome_mes=nome_mes,  # Passar o nome do mês
        ano=ano,
        valor_hora=valor_hora,
        total_horas=total_horas,
        valor_total=valor_total,
        meses=meses,
        horas_formatadas=horas_formatadas
    )


from collections import defaultdict

def calcular_horas_trabalhadas(registros):
    """
    Calcula o total de horas trabalhadas por dia, considerando sobreposições de horários no mesmo dia.
    """
    if not registros:
        return 0

    # Agrupar registros por data
    registros_por_data = defaultdict(list)

    for data_registro, hora_inicio, hora_fim in registros:
        data = data_registro  # Garante que é só a data, sem horário
        hora_inicio_dt = datetime.combine(data, hora_inicio)
        hora_fim_dt = datetime.combine(data, hora_fim)
        registros_por_data[data].append((hora_inicio_dt, hora_fim_dt))

    total_horas = 0

    # Consolidar intervalos por dia
    for data, intervalos in registros_por_data.items():
        # Ordenar os intervalos por hora de início
        intervalos.sort(key=lambda x: x[0])

        intervalos_consolidados = []

        for inicio, fim in intervalos:
            if not intervalos_consolidados:
                intervalos_consolidados.append((inicio, fim))
            else:
                ultimo_inicio, ultimo_fim = intervalos_consolidados[-1]
                if inicio <= ultimo_fim:
                    # Sobreposição: fundir
                    novo_inicio = min(ultimo_inicio, inicio)
                    novo_fim = max(ultimo_fim, fim)
                    intervalos_consolidados[-1] = (novo_inicio, novo_fim)
                else:
                    intervalos_consolidados.append((inicio, fim))

        # Soma os intervalos consolidados do dia
        for inicio, fim in intervalos_consolidados:
            diferenca = fim - inicio
            total_horas += diferenca.total_seconds() / 3600  # Converter segundos em horas

    return total_horas


@valor_a_receber_bp.route('/admin/calcular_valor_mensal', methods=['GET', 'POST'])
def admin_calcular_valor_mensal():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obter o mês e ano selecionados (padrão: mês e ano atual)
    mes = int(request.args.get('mes', datetime.today().month))
    ano = int(request.args.get('ano', datetime.today().year))
    usuario_id = request.args.get('usuario')  # ID do usuário selecionado

    # Lista de nomes dos meses em português
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    nome_mes = meses[mes - 1]  # Subtrair 1 porque a lista começa em 0

    # Conectar ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consultar todos os usuários para o filtro
    cursor.execute("SELECT IdUsuario, Usuario FROM Usuarios")
    usuarios = cursor.fetchall()

    # Consultar os registros do usuário selecionado no mês e ano selecionados
    if usuario_id:
        query = """
        SELECT DataRegistro, HoraInicio, HoraFim
        FROM RegistrosHoras
        WHERE IdColaborador = ?
        AND MONTH(DataRegistro) = ?
        AND YEAR(DataRegistro) = ?
        ORDER BY DataRegistro, HoraInicio

        """
        cursor.execute(query, (usuario_id, mes, ano))
        registros = cursor.fetchall()

        # Consultar o valor da hora do usuário selecionado
        cursor.execute("SELECT ValorHora, Usuario FROM Usuarios WHERE IdUsuario = ?", (usuario_id,))
        usuario_info = cursor.fetchone()
        valor_hora = usuario_info[0]
        nome_usuario = usuario_info[1]

        # Calcular o total de horas trabalhadas (considerando sobreposições)
        total_horas = calcular_horas_trabalhadas(registros)

        # Calcular o valor total a receber
        valor_total = total_horas * valor_hora
    else:
        # Se nenhum usuário for selecionado, não há dados para exibir
        nome_usuario = None
        valor_hora = 0
        total_horas = 0
        valor_total = 0

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Renderizar o template e passar os dados
    return render_template(
        'admin_calcular_valor_mensal.html',  
        # Nome do arquivo HTML
        horas_formatadas = formatar_horas_decimais(total_horas),
        mes=mes,
        nome_mes=nome_mes,  # Passar o nome do mês
        ano=ano,
        usuario_id=usuario_id,
        nome_usuario=nome_usuario,
        valor_hora=valor_hora,
        total_horas=total_horas,
        valor_total=valor_total,
        usuarios=usuarios,  # Passar a lista de usuários para o template
        meses=meses  # Passar a lista de meses para o template
    )

