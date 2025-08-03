# pip install Faker pandas

from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd
import os

# Inicializa o Faker para português do Brasil
fake = Faker('pt_BR')

# --- Funções de Geração de Dados para cada Tabela ---

def generate_hospitais(num_records):
    """Gera dados fictícios para a tabela Hospitais."""
    hospitais = []
    for i in range(num_records):
        hospitais.append({
            'hospital_id': i + 1,
            'nome_hospital': f"Hospital {fake.last_name()} {random.choice(['Geral', 'Regional', 'Santa Casa', 'Metropolitano'])}",
            'endereco': fake.street_address(),
            'cidade': fake.city(),
            'estado': fake.state_abbr(),
            'cep': fake.postcode(),
            'telefone': fake.phone_number(),
            'capacidade_leitos': random.randint(50, 500),
            'area_emergencia_capacidade': random.randint(5, 50),
            'estoque_farmacia_capacidade': random.randint(1000, 10000),
            'tipo_hospital': random.choice(['Geral', 'Especializado', 'Pronto Socorro']),
            'data_fundacao': fake.date_between(start_date='-50y', end_date='-5y').isoformat()
        })
    return pd.DataFrame(hospitais)

def generate_pacientes(num_records):
    """Gera dados fictícios para a tabela Pacientes."""
    pacientes = []
    for i in range(num_records):
        gender = random.choice(['M', 'F', 'Outro'])
        birth_date = fake.date_of_birth(minimum_age=1, maximum_age=90)
        pacientes.append({
            'paciente_id': i + 1,
            'nome': fake.first_name_male() if gender == 'M' else fake.first_name_female() if gender == 'F' else fake.first_name(),
            'sobrenome': fake.last_name(),
            'data_nascimento': birth_date.isoformat(),
            'genero': gender,
            'cpf': fake.cpf(),
            'rg': fake.rg(),
            'endereco': fake.street_address(),
            'cidade': fake.city(),
            'estado': fake.state_abbr(),
            'cep': fake.postcode(),
            'telefone': fake.phone_number(),
            'email': fake.email(),
            'tipo_sanguineo': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            'historico_medico_resumo': fake.paragraph(nb_sentences=2),
            'data_cadastro': (datetime.now() - timedelta(days=random.randint(0, 365*5))).isoformat(sep=' ', timespec='seconds')
        })
    return pd.DataFrame(pacientes)

def generate_funcionarios(num_records, hospital_ids):
    """Gera dados fictícios para a tabela Funcionarios."""
    funcionarios = []
    cargos = ['Medico', 'Enfermeiro', 'Tecnico Enfermagem', 'Administrativo', 'Farmaceutico', 'Tecnico Laboratorio', 'Atendente', 'Seguranca', 'Limpeza']
    especialidades_medicas = ['Clínico Geral', 'Cardiologista', 'Pediatra', 'Dermatologista', 'Ortopedista', 'Neurologista', 'Ginecologista']
    especialidades_enfermagem = ['Enfermeiro Chefe', 'Enfermeiro UTI', 'Enfermeiro Emergência']

    for i in range(num_records):
        cargo = random.choice(cargos)
        especialidade = None
        crm_coren = None
        if cargo == 'Medico':
            especialidade = random.choice(especialidades_medicas)
            crm_coren = f"CRM/{fake.state_abbr()} {random.randint(10000, 99999)}"
        elif cargo == 'Enfermeiro':
            especialidade = random.choice(especialidades_enfermagem)
            crm_coren = f"COREN/{fake.state_abbr()} {random.randint(100000, 999999)}"

        funcionarios.append({
            'funcionario_id': i + 1,
            'hospital_id': random.choice(hospital_ids),
            'nome': fake.first_name(),
            'sobrenome': fake.last_name(),
            'cpf': fake.cpf(),
            'cargo': cargo,
            'especialidade': especialidade,
            'crm_coren': crm_coren,
            'data_contratacao': fake.date_between(start_date='-20y', end_date='-1y').isoformat(),
            'salario': round(random.uniform(2000, 25000), 2),
            'turno': random.choice(['Manha', 'Tarde', 'Noite', 'Diurno', 'Noturno']),
            'email_corporativo': fake.email(),
            'status_funcionario': random.choice(['Ativo', 'Ferias', 'Afastado', 'Desligado'])
        })
    return pd.DataFrame(funcionarios)

def generate_setores(num_records, hospital_ids):
    """Gera dados fictícios para a tabela Setores."""
    setores = []
    tipos_setor = ['Emergencia', 'UTI', 'Internacao', 'Ambulatorio', 'Farmacia', 'Laboratorio', 'Administrativo', 'Centro Cirurgico', 'Radiologia']
    for i in range(num_records):
        tipo_setor = random.choice(tipos_setor)
        capacidade_leitos = random.randint(5, 100) if tipo_setor in ['Emergencia', 'UTI', 'Internacao'] else None
        setores.append({
            'setor_id': i + 1,
            'hospital_id': random.choice(hospital_ids),
            'nome_setor': f"{tipo_setor} {random.randint(1, 5)}",
            'tipo_setor': tipo_setor,
            'capacidade_leitos_setor': capacidade_leitos,
            'andar': random.randint(1, 10)
        })
    return pd.DataFrame(setores)

def generate_leitos(num_records, setor_ids):
    """Gera dados fictícios para a tabela Leitos."""
    leitos = []
    tipos_leito = ['Clinico', 'UTI', 'Semi-UTI', 'Pediatrico', 'Maternidade', 'Isolamento']
    for i in range(num_records):
        leitos.append({
            'leito_id': i + 1,
            'setor_id': random.choice(setor_ids),
            'numero_leito': f"L-{random.randint(1, 100)}",
            'tipo_leito': random.choice(tipos_leito),
            'status_leito': random.choice(['Disponivel', 'Ocupado', 'Manutencao', 'Higienizacao']),
            'data_ultima_ocupacao': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(sep=' ', timespec='seconds') if random.random() > 0.3 else None
        })
    return pd.DataFrame(leitos)

def generate_medicamentos(num_records):
    """Gera dados fictícios para a tabela Medicamentos."""
    medicamentos = []
    principios_ativos = ['Paracetamol', 'Ibuprofeno', 'Amoxicilina', 'Dipirona', 'Omeprazol', 'Sinvastatina', 'Losartana']
    formas_farmaceuticas = ['Comprimido', 'Cápsula', 'Xarope', 'Injetável', 'Pomada']
    unidades_medida = ['mg', 'g', 'ml', 'UI']
    for i in range(num_records):
        medicamentos.append({
            'medicamento_id': i + 1,
            'nome_comercial': f"{random.choice(principios_ativos)} {fake.word().capitalize()}",
            'principio_ativo': random.choice(principios_ativos),
            'concentracao': f"{random.randint(50, 1000)}{random.choice(['mg', 'ml'])}",
            'forma_farmaceutica': random.choice(formas_farmaceuticas),
            'unidade_medida': random.choice(unidades_medida),
            'estoque_minimo_sugerido': random.randint(10, 500),
            'data_registro': fake.date_between(start_date='-10y', end_date='-1y').isoformat(),
            'fabricante': fake.company()
        })
    return pd.DataFrame(medicamentos)

def generate_estoque_farmacia(num_records, hospital_ids, medicamento_ids):
    """Gera dados fictícios para a tabela EstoqueFarmacia."""
    estoque = []
    for i in range(num_records):
        estoque.append({
            'estoque_id': i + 1,
            'hospital_id': random.choice(hospital_ids),
            'medicamento_id': random.choice(medicamento_ids),
            'quantidade_disponivel': random.randint(0, 1000),
            'data_validade': fake.date_between(start_date='today', end_date='+2y').isoformat(),
            'numero_lote': fake.bothify(text='LOTE-########'),
            'localizacao_armazenamento': random.choice(['Prateleira A', 'Prateleira B', 'Refrigerador 1', 'Armario 3']),
            'data_ultima_atualizacao': datetime.now().isoformat(sep=' ', timespec='seconds')
        })
    return pd.DataFrame(estoque)

def generate_atendimentos(num_records, paciente_ids, hospital_ids, medico_ids, setor_ids):
    """Gera dados fictícios para a tabela Atendimentos."""
    atendimentos = []
    diagnosticos = ['Resfriado Comum', 'Gripe', 'Dor de Cabeça', 'Infecção Urinária', 'Fratura', 'Asma', 'Diabetes', 'Hipertensão']
    for i in range(num_records):
        data_chegada = fake.date_time_between(start_date='-1y', end_date='now')
        data_triagem = data_chegada + timedelta(minutes=random.randint(5, 60))
        data_inicio_atendimento = data_triagem + timedelta(minutes=random.randint(10, 120))
        data_fim_atendimento = data_inicio_atendimento + timedelta(minutes=random.randint(15, 180))

        tempo_espera_triagem = int((data_triagem - data_chegada).total_seconds() / 60)
        tempo_espera_atendimento = int((data_inicio_atendimento - data_triagem).total_seconds() / 60)
        duracao_atendimento = int((data_fim_atendimento - data_inicio_atendimento).total_seconds() / 60)

        atendimentos.append({
            'atendimento_id': i + 1,
            'paciente_id': random.choice(paciente_ids),
            'hospital_id': random.choice(hospital_ids),
            'funcionario_id_medico': random.choice(medico_ids),
            'setor_id': random.choice(setor_ids),
            'data_hora_chegada': data_chegada.isoformat(sep=' ', timespec='seconds'),
            'data_hora_triagem': data_triagem.isoformat(sep=' ', timespec='seconds'),
            'data_hora_inicio_atendimento': data_inicio_atendimento.isoformat(sep=' ', timespec='seconds'),
            'data_hora_fim_atendimento': data_fim_atendimento.isoformat(sep=' ', timespec='seconds'),
            'tipo_atendimento': random.choice(['Emergencia', 'Consulta Ambulatorial', 'Retorno', 'Exame', 'Procedimento']),
            'gravidade_paciente': random.choice(['Baixa', 'Media', 'Alta', 'Urgencia', 'Emergencia']),
            'diagnostico_principal': random.choice(diagnosticos),
            'observacoes_medicas': fake.paragraph(nb_sentences=1),
            'status_atendimento': random.choice(['Concluido', 'Alta', 'Encaminhado Internacao']), # Para dados históricos
            'tempo_espera_triagem_minutos': tempo_espera_triagem,
            'tempo_espera_atendimento_minutos': tempo_espera_atendimento,
            'duracao_atendimento_minutos': duracao_atendimento
        })
    return pd.DataFrame(atendimentos)

def generate_internacoes(num_records, atendimento_ids, paciente_ids, hospital_ids, leito_ids, medico_ids):
    """Gera dados fictícios para a tabela Internacoes."""
    internacoes = []
    diagnosticos = ['Pneumonia', 'Apendicite', 'Infarto', 'AVC', 'Diabetes Descompensada', 'Fratura Exposta']
    for i in range(num_records):
        data_internacao = fake.date_time_between(start_date='-6m', end_date='now')
        data_alta = data_internacao + timedelta(days=random.randint(1, 30)) if random.random() > 0.2 else None # 20% chances de ainda estar ativo
        
        internacoes.append({
            'internacao_id': i + 1,
            'atendimento_id': random.choice(atendimento_ids) if random.random() > 0.1 else None, # 10% de internação direta
            'paciente_id': random.choice(paciente_ids),
            'hospital_id': random.choice(hospital_ids),
            'leito_id': random.choice(leito_ids),
            'data_hora_internacao': data_internacao.isoformat(sep=' ', timespec='seconds'),
            'data_hora_alta': data_alta.isoformat(sep=' ', timespec='seconds') if data_alta else None,
            'diagnostico_internacao': random.choice(diagnosticos),
            'procedimentos_realizados': fake.paragraph(nb_sentences=1) if random.random() > 0.5 else None,
            'status_internacao': 'Ativa' if data_alta is None else random.choice(['Concluida', 'Obito']),
            'funcionario_id_medico_responsavel': random.choice(medico_ids)
        })
    return pd.DataFrame(internacoes)

def generate_prescricoes(num_records, atendimento_ids, paciente_ids, medico_ids):
    """Gera dados fictícios para a tabela Prescricoes."""
    prescricoes = []
    for i in range(num_records):
        prescricoes.append({
            'prescricao_id': i + 1,
            'atendimento_id': random.choice(atendimento_ids),
            'paciente_id': random.choice(paciente_ids),
            'funcionario_id_medico': random.choice(medico_ids),
            'data_hora_prescricao': fake.date_time_between(start_date='-6m', end_date='now').isoformat(sep=' ', timespec='seconds'),
            'status_prescricao': random.choice(['Ativa', 'Suspensa', 'Concluida', 'Cancelada'])
        })
    return pd.DataFrame(prescricoes)

def generate_itens_prescricao(num_records, prescricao_ids, medicamento_ids):
    """Gera dados fictícios para a tabela ItensPrescricao."""
    itens = []
    dosagens = ['10mg', '250mg', '500mg', '1g', '5ml', '10ml']
    frequencias = ['8/8h', '12/12h', '24/24h', 'De 6/6h', 'Única']
    vias = ['Oral', 'Intravenosa', 'Intramuscular', 'Tópica']
    for i in range(num_records):
        data_inicio = fake.date_time_between(start_date='-3m', end_date='now')
        data_fim = data_inicio + timedelta(days=random.randint(1, 15))
        itens.append({
            'item_prescricao_id': i + 1,
            'prescricao_id': random.choice(prescricao_ids),
            'medicamento_id': random.choice(medicamento_ids),
            'dosagem': random.choice(dosagens),
            'frequencia': random.choice(frequencias),
            'via_administracao': random.choice(vias),
            'data_hora_inicio': data_inicio.isoformat(sep=' ', timespec='seconds'),
            'data_hora_fim': data_fim.isoformat(sep=' ', timespec='seconds'),
            'observacoes_item': fake.sentence(nb_words=5) if random.random() > 0.7 else None
        })
    return pd.DataFrame(itens)

def generate_dispensacao_medicamentos(num_records, item_prescricao_ids, farmaceutico_ids):
    """Gera dados fictícios para a tabela DispensacaoMedicamentos."""
    dispensacoes = []
    for i in range(num_records):
        dispensacoes.append({
            'dispensacao_id': i + 1,
            'item_prescricao_id': random.choice(item_prescricao_ids),
            'funcionario_id_farmaceutico': random.choice(farmaceutico_ids),
            'data_hora_dispensacao': fake.date_time_between(start_date='-3m', end_date='now').isoformat(sep=' ', timespec='seconds'),
            'quantidade_dispensada': random.randint(1, 30),
            'observacoes_dispensacao': fake.sentence(nb_words=5) if random.random() > 0.7 else None
        })
    return pd.DataFrame(dispensacoes)

def generate_nir_sac_registros(num_records, hospital_ids, atendimento_ids, paciente_ids, funcionario_ids):
    """Gera dados fictícios para a tabela NIR_SAC_Registros."""
    registros = []
    tipos_registro = ['NIR - Solicitacao Leito', 'NIR - Transferencia', 'SAC - Reclamacao', 'SAC - Sugestao', 'Incidente Interno', 'Erro Medicacao', 'Queda Paciente']
    severidades = ['Baixa', 'Media', 'Alta', 'Critica']
    status_resolucao = ['Aberto', 'Em Analise', 'Em Andamento', 'Resolvido', 'Fechado', 'Cancelado']

    for i in range(num_records):
        tipo_reg = random.choice(tipos_registro)
        atendimento_id = random.choice(atendimento_ids) if random.random() > 0.3 else None
        paciente_id = random.choice(paciente_ids) if random.random() > 0.2 else None
        
        data_registro = fake.date_time_between(start_date='-1y', end_date='now')
        status = random.choice(status_resolucao)
        data_resolucao = data_registro + timedelta(days=random.randint(1, 30)) if status in ['Resolvido', 'Fechado'] else None

        registros.append({
            'registro_id': i + 1,
            'hospital_id': random.choice(hospital_ids),
            'atendimento_id': atendimento_id,
            'paciente_id': paciente_id,
            'funcionario_id_registrador': random.choice(funcionario_ids),
            'tipo_registro': tipo_reg,
            'data_hora_registro': data_registro.isoformat(sep=' ', timespec='seconds'),
            'descricao_incidente_solicitacao': fake.paragraph(nb_sentences=2),
            'severidade': random.choice(severidades),
            'status_resolucao': status,
            'data_hora_resolucao': data_resolucao.isoformat(sep=' ', timespec='seconds') if data_resolucao else None,
            'responsavel_resolucao': fake.name() if random.random() > 0.5 else None,
            'observacoes_resolucao': fake.sentence(nb_words=5) if random.random() > 0.6 else None
        })
    return pd.DataFrame(registros)

def generate_equipamentos_medicos(num_records, hospital_ids, setor_ids):
    """Gera dados fictícios para a tabela EquipamentosMedicos."""
    equipamentos = []
    nomes_equip = ['Monitor Cardíaco', 'Ventilador Pulmonar', 'Máquina de Raio-X', 'Ultrassom', 'Bomba de Infusão', 'Desfibrilador']
    for i in range(num_records):
        data_aquisicao = fake.date_between(start_date='-10y', end_date='-1y')
        equipamentos.append({
            'equipamento_id': i + 1,
            'hospital_id': random.choice(hospital_ids),
            'nome_equipamento': random.choice(nomes_equip),
            'modelo': fake.bothify(text='MODELO-###??'),
            'numero_serie': fake.uuid4(),
            'setor_alocado': random.choice(setor_ids),
            'data_aquisicao': data_aquisicao.isoformat(),
            'status_equipamento': random.choice(['Em Uso', 'Em Manutencao', 'Disponivel', 'Desativado']),
            'ultima_calibracao': (data_aquisicao + timedelta(days=random.randint(30, 365))).isoformat(),
            'proxima_calibracao': (data_aquisicao + timedelta(days=random.randint(365, 730))).isoformat()
        })
    return pd.DataFrame(equipamentos)

def generate_manutencoes(num_records, equipamento_ids, funcionario_ids):
    """Gera dados fictícios para a tabela Manutencoes."""
    manutencoes = []
    tipos_manutencao = ['Preventiva', 'Corretiva', 'Calibracao']
    for i in range(num_records):
        data_inicio = fake.date_time_between(start_date='-1y', end_date='now')
        data_fim = data_inicio + timedelta(hours=random.randint(1, 24))
        manutencoes.append({
            'manutencao_id': i + 1,
            'equipamento_id': random.choice(equipamento_ids),
            'data_hora_inicio': data_inicio.isoformat(sep=' ', timespec='seconds'),
            'data_hora_fim': data_fim.isoformat(sep=' ', timespec='seconds'),
            'tipo_manutencao': random.choice(tipos_manutencao),
            'descricao_problema': fake.sentence(nb_words=10),
            'acoes_realizadas': fake.paragraph(nb_sentences=2),
            'funcionario_id_responsavel': random.choice(funcionario_ids),
            'custo_manutencao': round(random.uniform(50, 2000), 2)
        })
    return pd.DataFrame(manutencoes)

# --- Configuração e Execução da Geração ---

# Defina o número de registros para cada tabela.
# Ajuste esses valores para gerar uma base de dados "grande".
NUM_HOSPITAIS = 3
NUM_PACIENTES = 100
NUM_FUNCIONARIOS = 50
NUM_SETORES = 15 # Por hospital, então total será NUM_HOSPITAIS * NUM_SETORES_POR_HOSPITAL
NUM_LEITOS = 100 # Por setor, então total será NUM_SETORES * NUM_LEITOS_POR_SETOR
NUM_MEDICAMENTOS = 50
NUM_ESTOQUE_FARMACIA = 100
NUM_ATENDIMENTOS = 500
NUM_INTERNACOES = 100
NUM_PRESCRICOES = 200
NUM_ITENS_PRESCRICAO = 300
NUM_DISPENSACAO_MEDICAMENTOS = 250
NUM_NIR_SAC_REGISTROS = 75
NUM_EQUIPAMENTOS_MEDICOS = 50
NUM_MANUTENCOES = 30

# Cria a pasta 'csv_data' se não existir
output_dir = 'csv_data'
os.makedirs(output_dir, exist_ok=True)

print("Gerando dados para Hospitais...")
df_hospitais = generate_hospitais(NUM_HOSPITAIS)
df_hospitais.to_csv(os.path.join(output_dir, 'hospitais.csv'), index=False, encoding='utf-8-sig')
hospital_ids = df_hospitais['hospital_id'].tolist()
print(f"Gerados {len(df_hospitais)} registros para hospitais.csv")

print("Gerando dados para Pacientes...")
df_pacientes = generate_pacientes(NUM_PACIENTES)
df_pacientes.to_csv(os.path.join(output_dir, 'pacientes.csv'), index=False, encoding='utf-8-sig')
paciente_ids = df_pacientes['paciente_id'].tolist()
print(f"Gerados {len(df_pacientes)} registros para pacientes.csv")

print("Gerando dados para Funcionarios...")
df_funcionarios = generate_funcionarios(NUM_FUNCIONARIOS, hospital_ids)
df_funcionarios.to_csv(os.path.join(output_dir, 'funcionarios.csv'), index=False, encoding='utf-8-sig')
medico_ids = df_funcionarios[df_funcionarios['cargo'] == 'Medico']['funcionario_id'].tolist()
farmaceutico_ids = df_funcionarios[df_funcionarios['cargo'] == 'Farmaceutico']['funcionario_id'].tolist()
# Incluir outros funcionários para o registrador de NIR/SAC
all_funcionario_ids = df_funcionarios['funcionario_id'].tolist()
print(f"Gerados {len(df_funcionarios)} registros para funcionarios.csv")

print("Gerando dados para Setores...")
df_setores = generate_setores(NUM_SETORES, hospital_ids)
df_setores.to_csv(os.path.join(output_dir, 'setores.csv'), index=False, encoding='utf-8-sig')
setor_ids = df_setores['setor_id'].tolist()
print(f"Gerados {len(df_setores)} registros para setores.csv")

print("Gerando dados para Leitos...")
df_leitos = generate_leitos(NUM_LEITOS, setor_ids)
df_leitos.to_csv(os.path.join(output_dir, 'leitos.csv'), index=False, encoding='utf-8-sig')
leito_ids = df_leitos['leito_id'].tolist()
print(f"Gerados {len(df_leitos)} registros para leitos.csv")

print("Gerando dados para Medicamentos...")
df_medicamentos = generate_medicamentos(NUM_MEDICAMENTOS)
df_medicamentos.to_csv(os.path.join(output_dir, 'medicamentos.csv'), index=False, encoding='utf-8-sig')
medicamento_ids = df_medicamentos['medicamento_id'].tolist()
print(f"Gerados {len(df_medicamentos)} registros para medicamentos.csv")

print("Gerando dados para EstoqueFarmacia...")
df_estoque_farmacia = generate_estoque_farmacia(NUM_ESTOQUE_FARMACIA, hospital_ids, medicamento_ids)
df_estoque_farmacia.to_csv(os.path.join(output_dir, 'estoque_farmacia.csv'), index=False, encoding='utf-8-sig')
print(f"Gerados {len(df_estoque_farmacia)} registros para estoque_farmacia.csv")

print("Gerando dados para Atendimentos...")
df_atendimentos = generate_atendimentos(NUM_ATENDIMENTOS, paciente_ids, hospital_ids, medico_ids, setor_ids)
df_atendimentos.to_csv(os.path.join(output_dir, 'atendimentos.csv'), index=False, encoding='utf-8-sig')
atendimento_ids = df_atendimentos['atendimento_id'].tolist()
print(f"Gerados {len(df_atendimentos)} registros para atendimentos.csv")

print("Gerando dados para Internacoes...")
df_internacoes = generate_internacoes(NUM_INTERNACOES, atendimento_ids, paciente_ids, hospital_ids, leito_ids, medico_ids)
df_internacoes.to_csv(os.path.join(output_dir, 'internacoes.csv'), index=False, encoding='utf-8-sig')
print(f"Gerados {len(df_internacoes)} registros para internacoes.csv")

print("Gerando dados para Prescricoes...")
df_prescricoes = generate_prescricoes(NUM_PRESCRICOES, atendimento_ids, paciente_ids, medico_ids)
df_prescricoes.to_csv(os.path.join(output_dir, 'prescricoes.csv'), index=False, encoding='utf-8-sig')
prescricao_ids = df_prescricoes['prescricao_id'].tolist()
print(f"Gerados {len(df_prescricoes)} registros para prescricoes.csv")

print("Gerando dados para ItensPrescricao...")
df_itens_prescricao = generate_itens_prescricao(NUM_ITENS_PRESCRICAO, prescricao_ids, medicamento_ids)
df_itens_prescricao.to_csv(os.path.join(output_dir, 'itens_prescricao.csv'), index=False, encoding='utf-8-sig')
item_prescricao_ids = df_itens_prescricao['item_prescricao_id'].tolist()
print(f"Gerados {len(df_itens_prescricao)} registros para itens_prescricao.csv")

print("Gerando dados para DispensacaoMedicamentos...")
df_dispensacao_medicamentos = generate_dispensacao_medicamentos(NUM_DISPENSACAO_MEDICAMENTOS, item_prescricao_ids, farmaceutico_ids)
df_dispensacao_medicamentos.to_csv(os.path.join(output_dir, 'dispensacao_medicamentos.csv'), index=False, encoding='utf-8-sig')
print(f"Gerados {len(df_dispensacao_medicamentos)} registros para dispensacao_medicamentos.csv")

print("Gerando dados para NIR_SAC_Registros...")
df_nir_sac_registros = generate_nir_sac_registros(NUM_NIR_SAC_REGISTROS, hospital_ids, atendimento_ids, paciente_ids, all_funcionario_ids)
df_nir_sac_registros.to_csv(os.path.join(output_dir, 'nir_sac_registros.csv'), index=False, encoding='utf-8-sig')
print(f"Gerados {len(df_nir_sac_registros)} registros para nir_sac_registros.csv")

print("Gerando dados para EquipamentosMedicos...")
df_equipamentos_medicos = generate_equipamentos_medicos(NUM_EQUIPAMENTOS_MEDICOS, hospital_ids, setor_ids)
df_equipamentos_medicos.to_csv(os.path.join(output_dir, 'equipamentos_medicos.csv'), index=False, encoding='utf-8-sig')
equipamento_ids = df_equipamentos_medicos['equipamento_id'].tolist()
print(f"Gerados {len(df_equipamentos_medicos)} registros para equipamentos_medicos.csv")

print("Gerando dados para Manutencoes...")
df_manutencoes = generate_manutencoes(NUM_MANUTENCOES, equipamento_ids, all_funcionario_ids)
df_manutencoes.to_csv(os.path.join(output_dir, 'manutencoes.csv'), index=False, encoding='utf-8-sig')
print(f"Gerados {len(df_manutencoes)} registros para manutencoes.csv")

print("\nTodos os arquivos CSV foram gerados na pasta 'csv_data'.")
