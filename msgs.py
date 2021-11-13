tos = ('<b>Termos de serviço</b>'
    '\n'
    '\n- Todas as mensagens são registradas, mesmo as editadas e as apagadas.')
start = ('Olá, <b>{}</b>!'
    '\nPor favor, envie seu relato de forma objetiva e resumida.'
    '\nSe necessário, inclua prints de tela.'
    '\nTe responderemos assim que possível. ✅')
priorities = (
    #'\n⬜️ 0: Encerrado (<code>/fim</code>;'
    '\n🟦 1: Não urgente;'
    '\n🟩 2: Pouco urgente;'
    '\n🟨 3: Urgente;'
    '\n🟧 4: Muito urgente;'
    '\n🟥 5: Emergência.'
    )
set_priority = ('⚙️ Envie <code>/p valor</code> para definir o valor da prioridade.'
    + priorities)
end_operator = ('⚙️ Atendimento encerrado por <a href="tg://user?id={0}">{0} {1} {2}</a>.')
end_user = ('🔲 <b>Atendimento encerrado.</b>'
    '\nEnvie /start para começar um novo atendimento.')
topic_format = (
    '{0} <a href="tg://user?id={1}">{1} 👤 {2} {3}</a>')
error_operator = ('Utilize os comentários do canal para responder as pessoas.')
