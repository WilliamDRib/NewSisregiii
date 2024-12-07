create database db_saude;
use db_saude;

create table pacientes (
id int not null auto_increment,
codigo int not null,
nome varchar(50) not null,
cns bigint not null,
telefone bigint not null,

anonimo bool not null,
telefone_valido bool not null,
enviado bool DEFAULT False NOT null,
erro_status bool DEFAULT False,

tempo_coleta double not null, 
tempo_envio double,
erro varchar(255),

data_coleta datetime not NULL,
data_envio datetime,

primary key (id),
UNIQUE (codigo)
);