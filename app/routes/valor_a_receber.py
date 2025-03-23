from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta


valor_a_receber_bp = Blueprint('valor_a_receber', __name__)


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
    SELECT HoraInicio, HoraFim
    FROM RegistrosHoras
    WHERE IdColaborador = ?
    AND MONTH(DataRegistro) = ?
    AND YEAR(DataRegistro) = ?
    ORDER BY HoraInicio
    """
    cursor.execute(query, (colaborador_id, mes, ano))
    registros = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Calcular o total de horas trabalhadas (considerando sobreposições)
    total_horas = calcular_horas_trabalhadas(registros)

    # Calcular o valor total a receber
    valor_total = total_horas * valor_hora

    # Renderizar o template e passar os dados
    return render_template(
        'calcular_valor_mensal.html',  # Nome do arquivo HTML
        mes=mes,
        nome_mes=nome_mes,  # Passar o nome do mês
        ano=ano,
        valor_hora=valor_hora,
        total_horas=total_horas,
        valor_total=valor_total,
        meses=meses  # Passar a lista de meses para o template
    )


def calcular_horas_trabalhadas(registros):
    """
    Calcula o total de horas trabalhadas, considerando sobreposições de horários.
    """
    if not registros:
        return 0

    # Ordenar os registros por HoraInicio
    registros_ordenados = sorted(registros, key=lambda x: x[0])

    # Inicializar a lista de intervalos consolidados
    intervalos_consolidados = []

    for registro in registros_ordenados:
        hora_inicio = datetime.strptime(str(registro[0]), '%H:%M:%S')
        hora_fim = datetime.strptime(str(registro[1]), '%H:%M:%S')

        if not intervalos_consolidados:
            intervalos_consolidados.append((hora_inicio, hora_fim))
        else:
            ultimo_inicio, ultimo_fim = intervalos_consolidados[-1]

            # Verificar sobreposição
            if hora_inicio <= ultimo_fim:
                # Atualizar o intervalo consolidado
                novo_inicio = min(ultimo_inicio, hora_inicio)
                novo_fim = max(ultimo_fim, hora_fim)
                intervalos_consolidados[-1] = (novo_inicio, novo_fim)
            else:
                # Adicionar um novo intervalo consolidado
                intervalos_consolidados.append((hora_inicio, hora_fim))

    # Calcular o total de horas trabalhadas
    total_horas = 0
    for inicio, fim in intervalos_consolidados:
        diferenca = fim - inicio
        total_horas += diferenca.total_seconds() / 3600  # Converter segundos para horas

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
        SELECT HoraInicio, HoraFim
        FROM RegistrosHoras
        WHERE IdColaborador = ?
        AND MONTH(DataRegistro) = ?
        AND YEAR(DataRegistro) = ?
        ORDER BY HoraInicio
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
        'admin_calcular_valor_mensal.html',  # Nome do arquivo HTML
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

