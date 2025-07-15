# Copilot Instructions for Gerenciamento (Lottery Management System)

## Project Overview


### Sobre arquivos
 - Não crie várias documentações sobre um mesmo assunto, quando achar necessário criar uma documnentação para determinado assunto, mantenha sempre nela as intruções separando por seção
 - Se houver muitos arquivos para um mesmo script, que controlam tal script, que dependem de tal script, durante os processos sugira separarmos uma pasta para unir eles, excetos arquivos como .env, d_config.py e outros que sejam dependencias de outros arquivos. 
 - Nunca apague arquivos sem antes confirmar. Nunca de forma alguma apague arquivos como .env, main.py, db_config.py e outros que sejam dependencias de outros arquivos.
 - Cada script criado que for solicitado logging para eles, os logging de erros devem ir tambem para logs/logs_geral.log com identificação do aplicativo que está gerando o log.     mantendo sempre o padrao da forma como os logs são gerados lá.


 ### Sobre banco de dados
- Sempre usar DB_CONFIG do .env
- Nunca hardcoded credentials

### Sobre logging para arquivos da pasta andamento
- Sistema unificado em logs_geral_agendador.log
- Identificadores [AGENDADOR], [SERVICO], etc.


### Sempre que rodar o servidor ou reiniciar
- Sempre rode o servidor com o comando `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`


### Criação de novos arquivos e suas dependencias

- para cada arquivo criado que for uma dependencia exclusiva de tal arquivo, crie ele com nome usando prefixo do arquivo oficial. imagine que foi criado o arquivo backup_banco_de_dados.py, crie o arquivo de logging com nome backup_banco_de_dados.log , se for criado um agendador e tal agendador é especifico para o arquivo backup_banco_de_dados.py, crie o arquivo com nome backup_banco_de_dados_agendador

### Sobre a construção  e atualizações de scripts

- quando eu solicitar que o script deve rodar em oculto, sem terminal. Deverá fazer de forma que o terminal não apareça, mas que o script rode normalmente. Se ele tiver que aparecer momentaneamente, pode aparecer, mas, deve sumir em seguida. Não quero correr o risco de rodar algo e fechar terminal que deveria ficar aberto, por isso, já deverá rodar em oculto.
- quando criar logging ou coisa para arquivo .bat evite emojis que não rodam no windows ou suas dependencias, ou seja, que posssam causar erros na execução dos arquivos. coloque emojis somente se tiver segurança de que não causará problemas.
- quando criar muitos arquivos que se conversam entre si, sem que sejam dependentes de outros scripts, crie uma pasta para eles, evitando assim, que fique tudo misturado.
- sempre que for criar arquivos que dependem de comunicação com o banco de dados, leia @MIGRACAO_ENV_CONSOLIDADO.md e siga o padrão.
- quando criar scripts de teste, apague assim que não for mais necessário.
- ao final de modificações, verifique se não tem documentação para tal arquivo para ser atualizada.
- coloque releases no cabeçario do script sobre as ultimas modificações e informações relevantes como datas.
