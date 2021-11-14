tos = ('<b>Termos de serviço</b>'
    '\n'
    '\n- Todas as mensagens são registradas, mesmo as editadas e as apagadas.')
start_operator = ('Você faz parte do time de resposta.'
    '\nEnvie as mensagens no canal para responder os usuários.')
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
ban_operator = ('⚙️ Usuário banido por <a href="tg://user?id={0}">{0} {1} {2}</a>.')
topic_format = (
    '{0} <a href="tg://user?id={1}">{1}</a> 👤 {2} {3}')
error_operator = ('⚙️ Utilize os comentários do canal para responder as pessoas.')
help_user = ('<b>Ajuda</b>'
    '\nTodas as mensagens enviadas aqui serão enviadas para atendimento.'
    '\nPara ler os termos de serviço, envie /tos.')
help_operator = ('⚙️ <b>Ajuda</b>'
    '\n<code>/p número</code> para alterar a <b>prioridade</b>.'
    '\n<code>/fim</code> para <b>encerrar</b> o chamado.'
    '\n<code>/ban</code> para banir a pessoa.'
    '\nAlterar prioridade ou finalizar automaticamente <b>desbane</b> a pessoa.')
bot_banned = ('❌ O bot foi bloqueado pelo usuário ❌')
quick_answer_ask = ('Envie uma resposta pronta. Para cancelar, envie /cancelar')
quick_answer_del = ('Envie a resposta pronta a ser removida.')
quick_answer_saved = ('Resposta pronta salva.')
quick_answer_deleted = ('Resposta pronta removida.')
quick_answer_error = ('Resposta pronta não localizada.')
