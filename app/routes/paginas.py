# routes/paginas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc

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
    

@paginas_bp.route('/pcos_por_cliente/<int:id_cliente>', methods=['GET'])
def pcos_por_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os PCOs do cliente selecionado
    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes WHERE IdCliente = ? AND Ativo = 1", (id_cliente,))
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Retorna os PCOs como JSON
    return jsonify([{'IdPcoCliente': pco.IdPcoCliente, 'Nome': pco.Nome} for pco in pcos])


from datetime import datetime

@paginas_bp.route('/consultar_registros')
def consultar_registros():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obter parâmetros de filtro da query string
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente')
    pco_id = request.args.get('pco')

    # Definir valores padrão para as datas
    hoje = datetime.today()
    primeiro_dia_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    hoje_str = hoje.strftime('%Y-%m-%d')

    # Se não houver filtros, usar os valores padrão
    if not data_inicio:
        data_inicio = primeiro_dia_mes
    if not data_fim:
        data_fim = hoje_str

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta base
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
    """

    # Parâmetros da consulta
    params = [session['usuario_id']]

    # Aplicar filtros
    if data_inicio:
        query += " AND rh.DataRegistro >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND rh.DataRegistro <= ?"
        params.append(data_fim)
    if cliente_id:
        query += " AND rh.IdCliente = ?"
        params.append(cliente_id)
    if pco_id:
        query += " AND rh.IdPcoCliente = ?"
        params.append(pco_id)

    query += " ORDER BY rh.DataRegistro DESC"

    # Executar a consulta
    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()

    # Consultar clientes e PCOs para os filtros
    cursor.execute("SELECT IdCliente, Nome FROM Clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes")
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passar os registros e filtros para o template
    return render_template(
        'consultar_registros.html',
        registros=registros,
        clientes=clientes,
        pcos=pcos,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

@paginas_bp.route('/admin/consultar_registros')
def admin_consultar_registros():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obter parâmetros de filtro da query string
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente')
    pco_id = request.args.get('pco')
    colaborador_id = request.args.get('colaborador')

    # Definir valores padrão para as datas
    hoje = datetime.today()
    primeiro_dia_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    hoje_str = hoje.strftime('%Y-%m-%d')

    # Se não houver filtros, usar os valores padrão
    if not data_inicio:
        data_inicio = primeiro_dia_mes
    if not data_fim:
        data_fim = hoje_str

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta base para administradores
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
        rh.Descricao,
        u.Usuario AS Colaborador  -- Coluna Usuario na tabela Usuarios
    FROM RegistrosHoras rh
    INNER JOIN Clientes c ON rh.IdCliente = c.IdCliente
    INNER JOIN PcoClientes pc ON rh.IdPcoCliente = pc.IdPcoCliente
    INNER JOIN Servicos s ON rh.IdServico = s.IdServico
    INNER JOIN Atividades a ON rh.IdAtividade = a.IdAtividade
    INNER JOIN TiposHoras th ON rh.IdTipoHora = th.IdTipoHora
    INNER JOIN Usuarios u ON rh.IdColaborador = u.IdUsuario
    WHERE 1=1
    """

    # Parâmetros da consulta
    params = []

    # Aplicar filtros
    if data_inicio:
        query += " AND rh.DataRegistro >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND rh.DataRegistro <= ?"
        params.append(data_fim)
    if cliente_id:
        query += " AND rh.IdCliente = ?"
        params.append(cliente_id)
    if pco_id:
        query += " AND rh.IdPcoCliente = ?"
        params.append(pco_id)
    if colaborador_id:
        query += " AND rh.IdColaborador = ?"
        params.append(colaborador_id)

    query += " ORDER BY rh.DataRegistro DESC"

    # Executar a consulta
    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()

    # Consultar clientes, PCOs e colaboradores para os filtros
    cursor.execute("SELECT IdCliente, Nome FROM Clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes")
    pcos = cursor.fetchall()

    cursor.execute("SELECT IdUsuario, Usuario FROM Usuarios")  #Coluna Usuario na tabela Usuarios
    colaboradores = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passar os registros e filtros para o template
    return render_template(
        'admin_consultar_registros.html',
        registros=registros,
        clientes=clientes,
        pcos=pcos,
        colaboradores=colaboradores, 
        data_inicio=data_inicio,
        data_fim=data_fim
    )



# Rota para Valor a Receber
@paginas_bp.route('/valor_a_receber')
def valor_a_receber():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('valor_a_receber.html')

# Rota para Cadastrar Usuário (apenas administradores)
@paginas_bp.route('/cadastrar_usuario', methods=['GET'])
def cadastrar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os setores
    cursor.execute("SELECT IdSetor, Nome FROM Setores WHERE Ativo = 1")
    setores = cursor.fetchall()

    # Consulta para obter todos os usuários cadastrados
    cursor.execute("""
        SELECT u.IdUsuario, u.Usuario, u.ValorHora, s.Nome AS Setor, u.Administrador, u.Ativo
        FROM Usuarios u
        INNER JOIN Setores s ON u.Setor = s.IdSetor
    """)
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_usuario.html', setores=setores, usuarios=usuarios)

@paginas_bp.route('/salvar_usuario', methods=['POST'])
def salvar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    usuario = request.form['usuario']
    senha = request.form['senha']
    valor_hora = float(request.form['valor_hora'])
    setor = int(request.form['setor'])
    administrador = int(request.form['administrador'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo usuário na tabela Usuarios
    query = """
    INSERT INTO Usuarios (
        Usuario, Senha, ValorHora, Setor, Administrador, DataCadastro, Ativo
    ) VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
    """
    try:
        cursor.execute(query, (usuario, senha, valor_hora, setor, administrador, ativo))
        conn.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
    except pyodbc.IntegrityError as e:
        conn.rollback()
        flash('Erro ao cadastrar o usuário. Verifique os dados e tente novamente.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_usuario'))


@paginas_bp.route('/editar_usuario/<int:id_usuario>', methods=['GET'])
def editar_usuario(id_usuario):
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os setores
    cursor.execute("SELECT IdSetor, Nome FROM Setores WHERE Ativo = 1")
    setores = cursor.fetchall()

    # Consulta para obter os dados do usuário selecionado
    cursor.execute("""
        SELECT IdUsuario, Usuario, ValorHora, Setor, Administrador, Ativo
        FROM Usuarios
        WHERE IdUsuario = ?
    """, (id_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('paginas.cadastrar_usuario'))

    # Passa os dados para o template
    return render_template('editar_usuario.html', setores=setores, usuario=usuario)

@paginas_bp.route('/salvar_edicao_usuario/<int:id_usuario>', methods=['POST'])
def salvar_edicao_usuario(id_usuario):
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    usuario = request.form['usuario']
    senha = request.form['senha']
    valor_hora = float(request.form['valor_hora'])
    setor = int(request.form['setor'])
    administrador = int(request.form['administrador'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o usuário na tabela Usuarios
    if senha:
        query = """
        UPDATE Usuarios
        SET Usuario = ?, Senha = ?, ValorHora = ?, Setor = ?, Administrador = ?, Ativo = ?
        WHERE IdUsuario = ?
        """
        cursor.execute(query, (usuario, senha, valor_hora, setor, administrador, ativo, id_usuario))
    else:
        query = """
        UPDATE Usuarios
        SET Usuario = ?, ValorHora = ?, Setor = ?, Administrador = ?, Ativo = ?
        WHERE IdUsuario = ?
        """
        cursor.execute(query, (usuario, valor_hora, setor, administrador, ativo, id_usuario))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('paginas.cadastrar_usuario'))

# Rota para Cadastrar Cliente (apenas administradores)
@paginas_bp.route('/cadastrar_cliente', methods=['GET'])
def cadastrar_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os clientes cadastrados
    cursor.execute("SELECT IdCliente, Nome, Descricao, Ativo FROM Clientes")
    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_cliente.html', clientes=clientes)

@paginas_bp.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo cliente na tabela Clientes
    query = """
    INSERT INTO Clientes (
        Nome, Descricao, IdUsuarioCadastro, Ativo
    ) VALUES (?, ?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, session['usuario_id'], ativo))
        conn.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o cliente: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_cliente'))

@paginas_bp.route('/editar_cliente/<int:id_cliente>', methods=['GET'])
def editar_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do cliente selecionado
    cursor.execute("""
        SELECT IdCliente, Nome, Descricao, Ativo
        FROM Clientes
        WHERE IdCliente = ?
    """, (id_cliente,))
    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('paginas.cadastrar_cliente'))

    # Passa os dados para o template
    return render_template('editar_cliente.html', cliente=cliente)


@paginas_bp.route('/salvar_edicao_cliente/<int:id_cliente>', methods=['POST'])
def salvar_edicao_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o cliente na tabela Clientes
    query = """
    UPDATE Clientes
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdCliente = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_cliente))
        conn.commit()
        flash('Cliente atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o cliente: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_cliente'))






# Rota para Cadastrar PCO (apenas administradores)
@paginas_bp.route('/cadastrar_pco', methods=['GET'])
def cadastrar_pco():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os clientes
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    # Consulta para obter todos os PCOs cadastrados
    cursor.execute("""
        SELECT p.IdPcoCliente, p.Nome, p.Descricao, c.Nome AS Cliente, p.Ativo
        FROM PcoClientes p
        INNER JOIN Clientes c ON p.IdCliente = c.IdCliente
    """)
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_pco.html', clientes=clientes, pcos=pcos)


@paginas_bp.route('/editar_pco/<int:id_pco>', methods=['GET'])
def editar_pco(id_pco):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os clientes
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    # Consulta para obter os dados do PCO selecionado
    cursor.execute("""
        SELECT IdPcoCliente, Nome, Descricao, IdCliente, Ativo
        FROM PcoClientes
        WHERE IdPcoCliente = ?
    """, (id_pco,))
    pco = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pco:
        flash('PCO não encontrado.', 'error')
        return redirect(url_for('paginas.cadastrar_pco'))

    # Passa os dados para o template
    return render_template('editar_pco.html', clientes=clientes, pco=pco)


@paginas_bp.route('/salvar_pco', methods=['POST'])
def salvar_pco():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    id_cliente = int(request.form['cliente'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo PCO na tabela PcoClientes
    query = """
    INSERT INTO PcoClientes (
        Nome, Descricao, IdCliente, Ativo
    ) VALUES (?, ?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, id_cliente, ativo))
        conn.commit()
        flash('PCO cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o PCO: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_pco'))




@paginas_bp.route('/salvar_edicao_pco/<int:id_pco>', methods=['POST'])
def salvar_edicao_pco(id_pco):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    id_cliente = int(request.form['cliente'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o PCO na tabela PcoClientes
    query = """
    UPDATE PcoClientes
    SET Nome = ?, Descricao = ?, IdCliente = ?, Ativo = ?
    WHERE IdPcoCliente = ?
    """
    try:
        cursor.execute(query, (nome, descricao, id_cliente, ativo, id_pco))
        conn.commit()
        flash('PCO atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o PCO: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_pco'))



@paginas_bp.route('/cadastrar_setor', methods=['GET'])
def cadastrar_setor():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os setores cadastrados
    cursor.execute("SELECT IdSetor, Nome, Descricao, Ativo FROM Setores")
    setores = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_setor.html', setores=setores)


@paginas_bp.route('/salvar_setor', methods=['POST'])
def salvar_setor():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo setor na tabela Setores
    query = """
    INSERT INTO Setores (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Setor cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o setor: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_setor'))


@paginas_bp.route('/editar_setor/<int:id_setor>', methods=['GET'])
def editar_setor(id_setor):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do setor selecionado
    cursor.execute("""
        SELECT IdSetor, Nome, Descricao, Ativo
        FROM Setores
        WHERE IdSetor = ?
    """, (id_setor,))
    setor = cursor.fetchone()

    cursor.close()
    conn.close()

    if not setor:
        flash('Setor não encontrado.', 'error')
        return redirect(url_for('paginas.cadastrar_setor'))

    # Passa os dados para o template
    return render_template('editar_setor.html', setor=setor)

@paginas_bp.route('/salvar_edicao_setor/<int:id_setor>', methods=['POST'])
def salvar_edicao_setor(id_setor):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o setor na tabela Setores
    query = """
    UPDATE Setores
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdSetor = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_setor))
        conn.commit()
        flash('Setor atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o setor: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_setor'))


@paginas_bp.route('/cadastrar_servico', methods=['GET'])
def cadastrar_servico():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os serviços cadastrados
    cursor.execute("SELECT IdServico, Nome, Descricao, Ativo FROM Servicos")
    servicos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_servico.html', servicos=servicos)


@paginas_bp.route('/salvar_servico', methods=['POST'])
def salvar_servico():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo serviço na tabela Servicos
    query = """
    INSERT INTO Servicos (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Serviço cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o serviço: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_servico'))


@paginas_bp.route('/editar_servico/<int:id_servico>', methods=['GET'])
def editar_servico(id_servico):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do serviço selecionado
    cursor.execute("""
        SELECT IdServico, Nome, Descricao, Ativo
        FROM Servicos
        WHERE IdServico = ?
    """, (id_servico,))
    servico = cursor.fetchone()

    cursor.close()
    conn.close()

    if not servico:
        flash('Serviço não encontrado.', 'error')
        return redirect(url_for('paginas.cadastrar_servico'))

    # Passa os dados para o template
    return render_template('editar_servico.html', servico=servico)


@paginas_bp.route('/salvar_edicao_servico/<int:id_servico>', methods=['POST'])
def salvar_edicao_servico(id_servico):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o serviço na tabela Servicos
    query = """
    UPDATE Servicos
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdServico = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_servico))
        conn.commit()
        flash('Serviço atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o serviço: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_servico'))


@paginas_bp.route('/cadastrar_atividade', methods=['GET'])
def cadastrar_atividade():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todas as atividades cadastradas
    cursor.execute("SELECT IdAtividade, Nome, Descricao, Ativo FROM Atividades")
    atividades = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_atividade.html', atividades=atividades)

@paginas_bp.route('/salvar_atividade', methods=['POST'])
def salvar_atividade():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere a nova atividade na tabela Atividades
    query = """
    INSERT INTO Atividades (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Atividade cadastrada com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar a atividade: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_atividade'))

@paginas_bp.route('/editar_atividade/<int:id_atividade>', methods=['GET'])
def editar_atividade(id_atividade):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados da atividade selecionada
    cursor.execute("""
        SELECT IdAtividade, Nome, Descricao, Ativo
        FROM Atividades
        WHERE IdAtividade = ?
    """, (id_atividade,))
    atividade = cursor.fetchone()

    cursor.close()
    conn.close()

    if not atividade:
        flash('Atividade não encontrada.', 'error')
        return redirect(url_for('paginas.cadastrar_atividade'))

    # Passa os dados para o template
    return render_template('editar_atividade.html', atividade=atividade)


@paginas_bp.route('/salvar_edicao_atividade/<int:id_atividade>', methods=['POST'])
def salvar_edicao_atividade(id_atividade):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza a atividade na tabela Atividades
    query = """
    UPDATE Atividades
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdAtividade = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_atividade))
        conn.commit()
        flash('Atividade atualizada com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar a atividade: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('paginas.cadastrar_atividade'))

