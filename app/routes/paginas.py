# routes/paginas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.config import conectar_banco

# Cria um Blueprint para as rotas de páginas
paginas_bp = Blueprint('paginas', __name__)

# Rota para a página Home
@paginas_bp.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('home.html', usuario=session['usuario_nome'])

# Rota para Registrar Horas
@paginas_bp.route('/registrar_horas', methods=['GET'])
def registrar_horas():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados necessários
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes WHERE Ativo = 1")
    pcos = cursor.fetchall()

    cursor.execute("SELECT IdServico, Nome FROM Servicos WHERE Ativo = 1")
    servicos = cursor.fetchall()

    cursor.execute("SELECT IdTipoHora, Nome FROM TiposHoras WHERE Ativo = 1")
    tipos_horas = cursor.fetchall()

    cursor.execute("SELECT IdAtividade, Nome FROM Atividades WHERE Ativo = 1")
    atividades = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template(
        'registrar_horas.html',
        clientes=clientes,
        pcos=pcos,
        servicos=servicos,
        tipos_horas=tipos_horas,
        atividades=atividades
    )


@paginas_bp.route('/salvar_registro', methods=['POST'])
def salvar_registro():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    data = request.form['data']
    hora_inicio = request.form['hora_inicio']
    hora_fim = request.form['hora_fim']
    id_cliente = request.form['cliente']
    id_pco = request.form['pco']
    id_servico = request.form['servico']
    id_tipo_hora = request.form['tipo_hora']
    id_atividade = request.form['atividade']
    descricao = request.form['descricao']

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o registro na tabela RegistrosHoras
    query = """
    INSERT INTO RegistrosHoras (
        IdColaborador, DataRegistro, HoraInicio, HoraFim, IdCliente, IdPcoCliente, IdServico, IdTipoHora, IdAtividade, Descricao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        session['usuario_id'], data, hora_inicio, hora_fim, id_cliente, id_pco, id_servico, id_tipo_hora, id_atividade, descricao
    ))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Registro salvo com sucesso!', 'success')
    return redirect(url_for('paginas.registrar_horas'))

# Rota para Consultar Registros
@paginas_bp.route('/consultar_registros')
def consultar_registros():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os registros do usuário logado
    query = """
    SELECT 
        rh.IdRegistroHora,
        rh.DataRegistro,
        rh.HoraInicio,
        rh.HoraFim,
        c.Nome AS Cliente,
        pc.Nome AS PcoCliente,
        s.Nome AS Servico,
        a.Nome AS Atividade,
        th.Nome AS TipoHora,
        rh.Descricao
    FROM RegistrosHoras rh
    INNER JOIN Clientes c ON rh.IdCliente = c.IdCliente
    INNER JOIN PcoClientes pc ON rh.IdPcoCliente = pc.IdPcoCliente
    INNER JOIN Servicos s ON rh.IdServico = s.IdServico
    INNER JOIN Atividades a ON rh.IdAtividade = a.IdAtividade
    INNER JOIN TiposHoras th ON rh.IdTipoHora = th.IdTipoHora
    WHERE rh.IdColaborador = ?
    ORDER BY rh.DataRegistro DESC
    """
    cursor.execute(query, (session['usuario_id'],))
    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os registros para o template
    return render_template('consultar_registros.html', registros=registros)

# Rota para Valor a Receber
@paginas_bp.route('/valor_a_receber')
def valor_a_receber():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('valor_a_receber.html')

# Rota para Cadastrar Usuário (apenas administradores)
@paginas_bp.route('/cadastrar_usuario')
def cadastrar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_usuario.html')

# Rota para Cadastrar Cliente (apenas administradores)
@paginas_bp.route('/cadastrar_cliente')
def cadastrar_cliente():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_cliente.html')

# Rota para Cadastrar PCO (apenas administradores)
@paginas_bp.route('/cadastrar_pco')
def cadastrar_pco():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_pco.html')